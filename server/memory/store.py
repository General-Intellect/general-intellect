import time
import uuid

from .models import MemoryItem, MemoryQueryResult


class MemoryStore:
    def __init__(self):
        self._store: dict[str, MemoryItem] = {}

    def write(self, agent_id: str, namespace: str, content: str, metadata: dict) -> str:
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        self._store[mem_id] = MemoryItem(
            id=mem_id,
            agent_id=agent_id,
            namespace=namespace,
            content=content,
            metadata=metadata,
        )
        return mem_id

    def query(self, agent_id: str, namespace: str, query: str, top_k: int) -> list[MemoryQueryResult]:
        now = time.time()
        candidates = [
            m for m in self._store.values()
            if m.namespace == namespace and m.agent_id == agent_id
        ]
        query_words = set(query.lower().split())
        scored = []
        for mem in candidates:
            content_words = set(mem.content.lower().split())
            overlap = len(query_words & content_words)
            age = now - mem.created_at
            recency = 1.0 / (1.0 + age / 3600)
            score = (overlap / max(len(query_words), 1)) * 0.7 + recency * 0.3
            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            MemoryQueryResult(
                id=mem.id,
                content=mem.content,
                score=round(score, 4),
                age_seconds=round(now - mem.created_at, 1),
            )
            for score, mem in scored[:top_k]
        ]

    def delete(self, mem_id: str) -> bool:
        if mem_id in self._store:
            del self._store[mem_id]
            return True
        return False

    def expire(self, namespace: str, older_than_seconds: int) -> int:
        now = time.time()
        to_delete = [
            mid for mid, mem in self._store.items()
            if mem.namespace == namespace and (now - mem.created_at) > older_than_seconds
        ]
        for mid in to_delete:
            del self._store[mid]
        return len(to_delete)

    @property
    def count(self) -> int:
        return len(self._store)

    @property
    def namespace_count(self) -> int:
        return len({m.namespace for m in self._store.values()})
