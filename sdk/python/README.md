# general-intellect (Python SDK)

Persistent, semantic memory for AI agents. No vector DB required.

## Install

```bash
pip install general-intellect
```

## Usage

```python
from generalintelect import GIClient

gi = GIClient(url="http://localhost:8000", agent_id="support-bot")

# In your LLM call handler:
context = gi.recall(query=user_message, namespace=call_id)
response = llm.complete(system_prompt + context + user_message)
gi.remember(content=f"User said: {user_message}", namespace=call_id)
```

### Async

```python
from generalintelect import AsyncGIClient

gi = AsyncGIClient(url="http://localhost:8000", agent_id="support-bot")

context = await gi.recall(query=user_message, namespace=call_id)
await gi.remember(content=user_message, namespace=call_id)
```

### Vapi / Retell middleware

```python
from generalintelect import GIClient
from generalintelect.vapi import with_memory

gi = GIClient(agent_id="support-bot")  # reads GI_URL from env

@with_memory(gi)
def handle_webhook(payload: dict) -> dict:
    context = payload["_gi_context"]  # injected automatically
    response = llm.complete(system_prompt + context + transcript)
    return {"response": response}
```

Memory degrades gracefully — if `GI_URL` is not set, `recall()` returns `""` and `remember()` is a no-op.

## Run the memory server

```bash
docker run -p 8000:8000 generalintelect/gi-server
```
