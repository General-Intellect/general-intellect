# General Intellect

> Persistent, semantic memory for AI agents. No vector DB required.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/general-intellect?label=PyPI)](https://pypi.org/project/general-intellect/)

## One command to start

```bash
docker run -p 8000:8000 generalintelect/gi-server
```

## Three lines to integrate

```python
from generalintelect import GIClient

gi = GIClient(url="http://localhost:8000", agent_id="support-bot")

context = gi.recall(query=user_message, namespace=call_id)
response = llm.complete(system_prompt + context + user_message)
gi.remember(content=user_message, namespace=call_id)
```

## Why?

| | General Intellect | Pinecone / Weaviate |
|---|---|---|
| Setup | `docker run` | Account + API key + index config |
| Dependencies | None | External managed service |
| Latency (p99, 10k memories) | **<50ms** | 50–200ms + network |
| Cost | Free, self-hosted | $70+/mo |
| Integration | 3 lines | 20+ lines |

## Benchmark

Measured on MacBook M2, 10,000 memories in a single namespace:

| | Latency |
|---|---|
| p50 | ~8ms |
| p95 | ~18ms |
| p99 | ~24ms |

Run it yourself: `python -m scripts.benchmark`

## Install

```bash
# Python
pip install general-intellect

# Node.js
npm install general-intellect
```

## Vapi / Retell middleware

```python
from generalintelect.vapi import with_memory

@with_memory(gi)
def handle_webhook(payload: dict) -> dict:
    context = payload["_gi_context"]  # injected automatically
    return {"response": llm.complete(system_prompt + context + transcript)}
```

```typescript
import { withMemory } from 'general-intellect/vapi';

export const POST = withMemory(gi)(async (payload) => {
  const context = payload._gi_context as string;
  return { response: await llm.complete(systemPrompt + context + transcript) };
});
```

Memory degrades gracefully — if `GI_URL` is not set, the agent behaves exactly as before.

## Self-hosting

```bash
git clone https://github.com/General-Intellect/general-intellect
cd general-intellect
docker compose up
```

## Examples

| Example | Stack | Description |
|---|---|---|
| [vapi-customer-support](examples/vapi-customer-support/) | Python + FastAPI | Vapi webhook with per-call memory |
| [retell-voice-agent](examples/retell-voice-agent/) | Node + Express | Retell webhook with persistent memory |
| [codex-agent](examples/codex-agent/) | Python | CLI coding agent with session memory |

## Design principles

- **No Pinecone. No Weaviate. No Postgres.** Sub-50ms retrieval, zero infra setup.
- **Self-hostable by default.** Docker Compose, one command.
- **SDK ergonomics first.** 3 lines to integrate.
- **Agent-identity aware.** Namespace + `agent_id` isolation baked in from day one.

## Architecture

```
Agent → GIClient.recall() → FastAPI server → LSH Index (SimHash + numpy)
                                                    ↓
                                        sentence-transformers (local)
                                        all-MiniLM-L6-v2
```

No data leaves your infrastructure. The embedding model runs locally in the container.

## Docs

→ [Quickstart](docs/quickstart.md) · [API Reference](docs/api-reference.md) · [Vapi Integration](docs/vapi-integration.md)

## License

MIT
