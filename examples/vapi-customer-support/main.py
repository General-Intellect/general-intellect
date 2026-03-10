"""
Vapi customer support agent with persistent memory via General Intellect.

Each call gets its own memory namespace (call_id), so the agent remembers
context within a call. Cross-call memory can be added by using a customer ID
as the namespace instead.

Run:
    pip install -r requirements.txt
    GI_URL=http://localhost:8000 OPENAI_API_KEY=... uvicorn main:app
"""

import os

from fastapi import FastAPI, Request
from openai import OpenAI

from generalintelect import GIClient

app = FastAPI()

gi = GIClient(agent_id="customer-support")  # reads GI_URL from env
openai_client = OpenAI()

SYSTEM_PROMPT = (
    "You are a friendly customer support agent. "
    "Use any memory context provided to personalize your responses. "
    "Be concise — this is a voice call."
)


@app.post("/webhook")
async def handle_vapi_webhook(request: Request):
    payload = await request.json()

    call_id = payload.get("call", {}).get("id", "unknown")
    transcript = payload.get("transcript", "")

    if not transcript:
        return {"response": "Hello! How can I help you today?"}

    # Pull relevant memories for this call
    context = gi.recall(query=transcript, namespace=call_id)

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + ("\n\n" + context if context else "")},
            {"role": "user", "content": transcript},
        ],
    )
    answer = completion.choices[0].message.content

    # Store this turn so the agent remembers it
    gi.remember(
        content=f"User: {transcript}\nAgent: {answer}",
        namespace=call_id,
    )

    return {"response": answer}


@app.get("/health")
async def health():
    return {"status": "ok"}
