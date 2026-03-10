# General Intellect

> Persistent, semantic memory for AI agents. No vector DB required.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## What is it?

General Intellect is a self-hostable memory service for voice and coding agents. Drop it into any Vapi or Retell agent in 3 lines of code and give your agent persistent memory across calls — without Pinecone, Weaviate, or any external vector database.

## Quickstart

```bash
docker run -p 8000:8000 generalintelect/gi-server
```

### Python (Vapi handler)

```python
from generalintelect import GIClient

gi = GIClient(url="http://localhost:8000", agent_id="support-bot")

context = gi.recall(query=user_message, namespace=call_id)
response = llm.complete(system_prompt + context + user_message)
gi.remember(content=f"User said: {user_message}", namespace=call_id)
```

### Node.js (Vapi webhook)

```typescript
import { GIClient } from 'general-intellect';

const gi = new GIClient({ url: 'http://localhost:8000', agentId: 'support-bot' });

const context = await gi.recall({ query: transcript, namespace: callId });
const response = await llm.complete(systemPrompt + context + transcript);
await gi.remember({ content: transcript, namespace: callId });
```

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/memory` | Write a memory |
| `POST` | `/memory/query` | Query memories by semantic similarity |
| `DELETE` | `/memory/{id}` | Delete a memory |
| `POST` | `/memory/expire` | Expire old memories in a namespace |
| `GET` | `/health` | Health check |

## Self-hosting

```bash
git clone https://github.com/General-Intellect/general-intellect
cd general-intellect
docker compose up
```

## Design Principles

- **No Pinecone. No Weaviate. No Postgres.** Sub-50ms retrieval, zero infra setup.
- **Self-hostable by default.** Docker Compose, one command.
- **SDK ergonomics first.** 3 lines to integrate.
- **Agent-identity aware.** Namespace + agent ACL baked in from day one.

## License

MIT
