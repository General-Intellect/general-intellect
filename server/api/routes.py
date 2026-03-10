import time

from fastapi import APIRouter, HTTPException

from ..memory.models import (
    ExpireRequest,
    MemoryQuery,
    MemoryQueryResponse,
    MemoryWrite,
    MemoryWriteResponse,
)
from ..memory.store import MemoryStore

router = APIRouter()
store = MemoryStore()


@router.post("/memory", response_model=MemoryWriteResponse)
async def write_memory(payload: MemoryWrite):
    t0 = time.time()
    mem_id = store.write(
        agent_id=payload.agent_id,
        namespace=payload.namespace,
        content=payload.content,
        metadata=payload.metadata or {},
    )
    return MemoryWriteResponse(id=mem_id, latency_ms=round((time.time() - t0) * 1000, 2))


@router.post("/memory/query", response_model=MemoryQueryResponse)
async def query_memory(payload: MemoryQuery):
    t0 = time.time()
    results = store.query(
        agent_id=payload.agent_id,
        namespace=payload.namespace,
        query=payload.query,
        top_k=payload.top_k,
    )
    return MemoryQueryResponse(results=results, latency_ms=round((time.time() - t0) * 1000, 2))


@router.delete("/memory/{mem_id}")
async def delete_memory(mem_id: str):
    if not store.delete(mem_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": mem_id}


@router.post("/memory/expire")
async def expire_memory(payload: ExpireRequest):
    count = store.expire(namespace=payload.namespace, older_than_seconds=payload.older_than_seconds)
    return {"expired": count}
