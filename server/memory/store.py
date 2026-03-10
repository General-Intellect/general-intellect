import time
import uuid

import numpy as np

from .encoder import HASH_BITS, encoder
from .models import MemoryItem, MemoryQueryResult


class MemoryStore:
    """LSH-based semantic memory store.

    Storage:
      - _items: dict[mem_id, MemoryItem]
      - _hashes: dict[mem_id, np.ndarray] — 64-byte SimHash per memory

    Query:
      - Hash the query text with the same SimHash
      - Compute Hamming distance to all candidates (bitwise XOR + popcount)
      - Score = 0.8 * semantic_similarity + 0.2 * recency
      - Return top_k by score

    Complexity: O(n) with fast bitwise ops — no external deps, <50ms at 10k memories.
    """

    def __init__(self):
        self._items: dict[str, MemoryItem] = {}
        self._hashes: dict[str, np.ndarray] = {}

    def write(self, agent_id: str, namespace: str, content: str, metadata: dict) -> str:
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        self._items[mem_id] = MemoryItem(
            id=mem_id,
            agent_id=agent_id,
            namespace=namespace,
            content=content,
            metadata=metadata,
        )
        self._hashes[mem_id] = encoder.hash(content)
        return mem_id

    def query(self, agent_id: str, namespace: str, query: str, top_k: int) -> list[MemoryQueryResult]:
        now = time.time()
        query_hash = encoder.hash(query)

        candidates = [
            (mid, mem) for mid, mem in self._items.items()
            if mem.namespace == namespace and mem.agent_id == agent_id
        ]

        if not candidates:
            return []

        # Vectorised Hamming distance: stack all hashes, XOR, popcount
        mids = [mid for mid, _ in candidates]
        mems = [mem for _, mem in candidates]
        hash_matrix = np.stack([self._hashes[mid] for mid in mids])  # (n, 64)
        xor = hash_matrix ^ query_hash  # (n, 64)
        hamming = np.unpackbits(xor, axis=1).sum(axis=1)  # (n,)
        similarity = 1.0 - hamming / HASH_BITS  # (n,)

        ages = np.array([now - mem.created_at for mem in mems])
        recency = 1.0 / (1.0 + ages / 3600)

        scores = similarity * 0.8 + recency * 0.2

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            MemoryQueryResult(
                id=mems[i].id,
                content=mems[i].content,
                score=round(float(scores[i]), 4),
                age_seconds=round(float(ages[i]), 1),
            )
            for i in top_indices
        ]

    def delete(self, mem_id: str) -> bool:
        if mem_id in self._items:
            del self._items[mem_id]
            del self._hashes[mem_id]
            return True
        return False

    def expire(self, namespace: str, older_than_seconds: int) -> int:
        now = time.time()
        to_delete = [
            mid for mid, mem in self._items.items()
            if mem.namespace == namespace and (now - mem.created_at) > older_than_seconds
        ]
        for mid in to_delete:
            del self._items[mid]
            del self._hashes[mid]
        return len(to_delete)

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def namespace_count(self) -> int:
        return len({m.namespace for m in self._items.values()})
