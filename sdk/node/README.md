# general-intellect (Node.js SDK)

Persistent, semantic memory for AI agents. No vector DB required.

## Install

```bash
npm install general-intellect
```

## Usage

```typescript
import { GIClient } from 'general-intellect';

const gi = new GIClient({ url: 'http://localhost:8000', agentId: 'support-bot' });

// In your Vapi webhook handler:
const context = await gi.recall({ query: transcript, namespace: callId });
const response = await llm.complete(systemPrompt + context + transcript);
await gi.remember({ content: transcript, namespace: callId });
```

### Vapi / Retell middleware

```typescript
import { GIClient } from 'general-intellect';
import { withMemory } from 'general-intellect/vapi';

const gi = new GIClient({ agentId: 'support-bot' }); // reads GI_URL from env

export const POST = withMemory(gi)(async (payload) => {
  const context = payload._gi_context as string; // injected automatically
  const response = await llm.complete(systemPrompt + context + transcript);
  return { response };
});
```

Memory degrades gracefully — if `GI_URL` is not set, `recall()` returns `""` and `remember()` is a no-op.

## Run the memory server

```bash
docker run -p 8000:8000 generalintelect/gi-server
```

## Requirements

Node.js >= 18 (uses native `fetch` and `AbortSignal.timeout`)
