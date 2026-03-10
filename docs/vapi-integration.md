# Vapi Integration Guide

Add persistent memory to any Vapi voice agent in under 10 minutes.

## How it works

```
Vapi call starts
      │
      ▼
Webhook fires  ──►  Your handler
                        │
                   gi.recall()  ──►  memory server
                        │
                   LLM call (with context)
                        │
                   gi.remember()  ──►  memory server
                        │
                   Return response to Vapi
```

## Quickstart

### 1. Start the memory server

```bash
docker run -d -p 8000:8000 generalintelect/gi-server
```

### 2. Create a Vapi webhook handler

=== "Python (FastAPI)"

    ```python
    import os
    from fastapi import FastAPI, Request
    from openai import OpenAI
    from generalintelect import GIClient

    app = FastAPI()
    gi = GIClient(agent_id="support-bot")   # GI_URL from env
    openai = OpenAI()

    SYSTEM_PROMPT = "You are a helpful customer support agent."

    @app.post("/webhook")
    async def handle(request: Request):
        payload = await request.json()

        call_id   = payload.get("call", {}).get("id", "unknown")
        transcript = payload.get("transcript", "")

        # 1. Pull relevant memories
        context = gi.recall(query=transcript, namespace=call_id)

        # 2. Call LLM with memory context
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
                {"role": "user",   "content": transcript},
            ],
        )
        answer = resp.choices[0].message.content

        # 3. Store this turn
        gi.remember(content=f"User: {transcript}\nAgent: {answer}", namespace=call_id)

        return {"response": answer}
    ```

=== "Python (decorator)"

    ```python
    from generalintelect import GIClient
    from generalintelect.vapi import with_memory

    gi = GIClient(agent_id="support-bot")

    @app.post("/webhook")
    @with_memory(gi)
    def handle(payload: dict) -> dict:
        context    = payload["_gi_context"]
        transcript = payload.get("transcript", "")
        answer     = llm.complete(SYSTEM_PROMPT + context + transcript)
        return {"response": answer}
    ```

=== "Node.js"

    ```typescript
    import { GIClient } from 'general-intellect';
    import { withMemory } from 'general-intellect/vapi';

    const gi = new GIClient({ agentId: 'support-bot' });

    export const POST = withMemory(gi)(async (payload) => {
      const context    = payload._gi_context as string;
      const transcript = payload.transcript  as string ?? '';
      const answer     = await llm.complete(SYSTEM_PROMPT + context + transcript);
      return { response: answer };
    });
    ```

### 3. Set environment variables

```bash
export GI_URL=http://localhost:8000
export OPENAI_API_KEY=sk-...
```

### 4. Point Vapi at your webhook

In the Vapi dashboard: **Agent → Webhook URL → `https://your-server.com/webhook`**

---

## Memory namespace strategies

| Strategy | Namespace | Effect |
|---|---|---|
| Per-call (default) | `call_id` | Fresh memory each call |
| Per-customer | `customer_id` | Agent remembers the customer across calls |
| Per-org | `org_id` | Shared memory across all agents in an org |

```python
# Per-customer memory — pass customer_id as namespace
context = gi.recall(query=transcript, namespace=customer_id)
gi.remember(content=transcript, namespace=customer_id)
```

---

## Graceful degradation

The SDK is designed to degrade silently if the memory server is unreachable:

```python
gi = GIClient(agent_id="support-bot")  # GI_URL not set → all calls are no-ops
context = gi.recall(...)               # returns ""
gi.remember(...)                       # does nothing
```

This means you can deploy the integration to production without running the
memory server, and enable memory later by setting `GI_URL`.
