from fastapi import FastAPI

from .api.routes import router, store

app = FastAPI(
    title="General Intellect",
    description="Persistent, semantic memory for AI agents. No vector DB required.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "memories": store.count,
        "namespaces": store.namespace_count,
    }
