# Quickstart

Get General Intellect running in under 5 minutes.

## 1. Start the server

```bash
docker run -p 8000:8000 generalintelect/gi-server
```

Or with Docker Compose (recommended for production):

```bash
git clone https://github.com/General-Intellect/general-intellect
cd general-intellect
docker compose up
```

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok","memories":0,"namespaces":0}
```

## 2. Install the SDK

=== "Python"

    ```bash
    pip install general-intellect
    ```

=== "Node.js"

    ```bash
    npm install general-intellect
    ```

## 3. Add memory to your agent

=== "Python"

    ```python
    from generalintelect import GIClient

    gi = GIClient(url="http://localhost:8000", agent_id="my-agent")

    # Recall relevant context before LLM call
    context = gi.recall(query=user_message, namespace=session_id)

    # Call your LLM with the context injected
    response = llm.complete(system_prompt + context + user_message)

    # Store this turn in memory
    gi.remember(content=user_message, namespace=session_id)
    ```

=== "Node.js"

    ```typescript
    import { GIClient } from 'general-intellect';

    const gi = new GIClient({ url: 'http://localhost:8000', agentId: 'my-agent' });

    const context = await gi.recall({ query: userMessage, namespace: sessionId });
    const response = await llm.complete(systemPrompt + context + userMessage);
    await gi.remember({ content: userMessage, namespace: sessionId });
    ```

## 4. Graceful degradation

Set `GI_URL` as an environment variable and omit the `url` argument. If `GI_URL`
is not set, all SDK calls are silent no-ops — your agent works exactly as before.

```bash
export GI_URL=http://localhost:8000
```

```python
gi = GIClient(agent_id="my-agent")  # reads GI_URL from env
```

## Next steps

- [Vapi Integration Guide](vapi-integration.md)
- [API Reference](api-reference.md)
- [Examples](https://github.com/General-Intellect/general-intellect/tree/main/examples)
