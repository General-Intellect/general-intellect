# Vapi Customer Support Agent — with Memory

A Vapi webhook handler that gives your voice agent persistent memory across a call.

## Setup

```bash
# 1. Start the memory server
docker run -p 8000:8000 generalintelect/gi-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the webhook handler
GI_URL=http://localhost:8000 OPENAI_API_KEY=sk-... uvicorn main:app --port 8080
```

## Connect to Vapi

In your Vapi dashboard, set the webhook URL to:
```
https://your-server.com/webhook
```

## How it works

1. Vapi sends the call transcript to `/webhook`
2. The handler recalls relevant memories for this `call_id`
3. Memory context is injected into the LLM system prompt
4. The LLM response is stored as a new memory

Memory is scoped to the `call_id` by default. To share memory across calls
(e.g. returning customers), use a `customer_id` as the namespace instead.
