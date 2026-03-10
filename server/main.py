from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router, store
from .memory.encoder import encoder


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load the embedding model so the first request isn't slow
    encoder.load()
    yield


app = FastAPI(
    title="General Intellect",
    description="Persistent, semantic memory for AI agents. No vector DB required.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "memories": store.count,
        "namespaces": store.namespace_count,
    }
