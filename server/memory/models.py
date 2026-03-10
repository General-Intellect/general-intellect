import time
from typing import Any, Optional
from pydantic import BaseModel, Field


class MemoryWrite(BaseModel):
    agent_id: str
    namespace: str
    content: str
    metadata: Optional[dict[str, Any]] = {}


class MemoryQuery(BaseModel):
    agent_id: str
    namespace: str
    query: str
    top_k: int = 3


class MemoryItem(BaseModel):
    id: str
    agent_id: str
    namespace: str
    content: str
    metadata: dict[str, Any] = {}
    created_at: float = Field(default_factory=time.time)


class MemoryWriteResponse(BaseModel):
    id: str
    latency_ms: float


class MemoryQueryResult(BaseModel):
    id: str
    content: str
    score: float
    age_seconds: float


class MemoryQueryResponse(BaseModel):
    results: list[MemoryQueryResult]
    latency_ms: float


class ExpireRequest(BaseModel):
    namespace: str
    older_than_seconds: int
