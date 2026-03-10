# General Intellect

**Persistent, semantic memory for AI agents. No vector DB required.**

General Intellect is a self-hostable memory service that gives your Vapi, Retell, or custom AI agents persistent memory across calls and sessions — without Pinecone, Weaviate, or any external database.

## Why General Intellect?

| | General Intellect | Pinecone / Weaviate |
|---|---|---|
| Setup | `docker run` | Account + API key + index config |
| Dependencies | None | External managed service |
| Latency | <50ms p99 | 50–200ms + network |
| Cost | Free, self-hosted | $70+/mo |
| Integration | 3 lines | 20+ lines |

## How it works

1. Your agent calls `gi.remember(content, namespace)` after each turn
2. On the next turn, `gi.recall(query, namespace)` retrieves the most relevant memories
3. The returned context string is injected directly into your LLM system prompt

```python
context = gi.recall(query=user_message, namespace=call_id)
response = llm.complete(system_prompt + context + user_message)
gi.remember(content=user_message, namespace=call_id)
```

## Architecture

```
Agent Loop
    │
    ▼
GIClient.recall()  ──►  gi-server (FastAPI)
                              │
                         LSH Index
                       (SimHash + numpy)
                              │
                    sentence-transformers
                    all-MiniLM-L6-v2 (local)
```

No data leaves your infrastructure. The embedding model runs locally inside the Docker container.

## Get started

→ [Quickstart](quickstart.md)
