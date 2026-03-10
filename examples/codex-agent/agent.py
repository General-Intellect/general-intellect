"""
Coding agent with persistent memory via General Intellect.

Remembers past debugging sessions, code patterns, and project context
across conversations. Each "session" gets its own namespace.

Run:
    pip install -r requirements.txt
    GI_URL=http://localhost:8000 OPENAI_API_KEY=... python agent.py
"""

import os

from openai import OpenAI

from generalintelect import GIClient

gi = GIClient(agent_id="codex-agent")  # reads GI_URL from env
client = OpenAI()

SYSTEM_PROMPT = (
    "You are an expert coding assistant with persistent memory. "
    "You remember past debugging sessions, preferred patterns, and project context. "
    "Reference past context when relevant."
)


def chat(user_message: str, session_id: str) -> str:
    context = gi.recall(query=user_message, namespace=session_id)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + ("\n\n" + context if context else "")},
            {"role": "user", "content": user_message},
        ],
    )
    answer = completion.choices[0].message.content

    gi.remember(
        content=f"User: {user_message}\nAgent: {answer}",
        namespace=session_id,
        metadata={"type": "conversation_turn"},
    )

    return answer


if __name__ == "__main__":
    session = input("Session ID (press Enter for 'default'): ").strip() or "default"
    print(f"\nCoding agent ready. Session: '{session}'. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break
        print(f"Agent: {chat(user_input, session)}\n")
