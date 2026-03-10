# Retell Voice Agent — with Memory

A Retell webhook handler that gives your voice agent persistent memory.

## Setup

```bash
# 1. Start the memory server
docker run -p 8000:8000 generalintelect/gi-server

# 2. Install dependencies
npm install

# 3. Run the webhook handler
GI_URL=http://localhost:8000 OPENAI_API_KEY=sk-... npm start
```

## Connect to Retell

In your Retell dashboard, set the webhook URL to:
```
https://your-server.com/webhook
```

## How it works

The `withMemory(gi)` wrapper automatically:
1. Extracts the call transcript from the Retell payload
2. Queries memory for relevant context
3. Injects it as `payload._gi_context` before calling your handler
4. Writes the transcript to memory after the handler returns
