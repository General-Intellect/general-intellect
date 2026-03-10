import os

import httpx


def _format_context(results: list[dict]) -> str:
    if not results:
        return ""
    lines = "\n".join(f"- {r['content']}" for r in results)
    return f"[Memory context]\n{lines}\n"


class GIClient:
    """Synchronous General Intellect client.

    Usage:
        gi = GIClient(url="http://localhost:8000", agent_id="support-bot")
        context = gi.recall(query=user_message, namespace=call_id)
        gi.remember(content=user_message, namespace=call_id)
    """

    def __init__(
        self,
        url: str | None = None,
        agent_id: str = "default",
        default_namespace: str = "default",
        timeout: float = 5.0,
    ):
        self.url = (url or os.getenv("GI_URL", "")).rstrip("/")
        self.agent_id = agent_id
        self.default_namespace = default_namespace
        self._client = httpx.Client(base_url=self.url, timeout=timeout) if self.url else None

    def _enabled(self) -> bool:
        return bool(self.url and self._client)

    def remember(
        self,
        content: str,
        namespace: str | None = None,
        metadata: dict | None = None,
    ) -> str | None:
        """Write a memory. Returns the memory ID, or None if GI is disabled."""
        if not self._enabled():
            return None
        resp = self._client.post(
            "/memory",
            json={
                "agent_id": self.agent_id,
                "namespace": namespace or self.default_namespace,
                "content": content,
                "metadata": metadata or {},
            },
        )
        resp.raise_for_status()
        return resp.json()["id"]

    def recall(
        self,
        query: str,
        namespace: str | None = None,
        top_k: int = 3,
    ) -> str:
        """Query memories. Returns a formatted context string ready for LLM injection."""
        if not self._enabled():
            return ""
        resp = self._client.post(
            "/memory/query",
            json={
                "agent_id": self.agent_id,
                "namespace": namespace or self.default_namespace,
                "query": query,
                "top_k": top_k,
            },
        )
        resp.raise_for_status()
        return _format_context(resp.json()["results"])

    def forget(self, mem_id: str) -> None:
        """Delete a memory by ID."""
        if not self._enabled():
            return
        resp = self._client.delete(f"/memory/{mem_id}")
        if resp.status_code != 404:
            resp.raise_for_status()

    def close(self):
        if self._client:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class AsyncGIClient:
    """Async General Intellect client for use in async agent loops.

    Usage:
        gi = AsyncGIClient(url="http://localhost:8000", agent_id="support-bot")
        context = await gi.recall(query=user_message, namespace=call_id)
        await gi.remember(content=user_message, namespace=call_id)
    """

    def __init__(
        self,
        url: str | None = None,
        agent_id: str = "default",
        default_namespace: str = "default",
        timeout: float = 5.0,
    ):
        self.url = (url or os.getenv("GI_URL", "")).rstrip("/")
        self.agent_id = agent_id
        self.default_namespace = default_namespace
        self._client = httpx.AsyncClient(base_url=self.url, timeout=timeout) if self.url else None

    def _enabled(self) -> bool:
        return bool(self.url and self._client)

    async def remember(
        self,
        content: str,
        namespace: str | None = None,
        metadata: dict | None = None,
    ) -> str | None:
        if not self._enabled():
            return None
        resp = await self._client.post(
            "/memory",
            json={
                "agent_id": self.agent_id,
                "namespace": namespace or self.default_namespace,
                "content": content,
                "metadata": metadata or {},
            },
        )
        resp.raise_for_status()
        return resp.json()["id"]

    async def recall(
        self,
        query: str,
        namespace: str | None = None,
        top_k: int = 3,
    ) -> str:
        if not self._enabled():
            return ""
        resp = await self._client.post(
            "/memory/query",
            json={
                "agent_id": self.agent_id,
                "namespace": namespace or self.default_namespace,
                "query": query,
                "top_k": top_k,
            },
        )
        resp.raise_for_status()
        return _format_context(resp.json()["results"])

    async def forget(self, mem_id: str) -> None:
        if not self._enabled():
            return
        resp = await self._client.delete(f"/memory/{mem_id}")
        if resp.status_code != 404:
            resp.raise_for_status()

    async def close(self):
        if self._client:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()
