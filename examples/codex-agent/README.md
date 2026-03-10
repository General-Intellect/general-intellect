# Codex Agent — with Persistent Memory

A coding agent that remembers past debugging sessions, preferred patterns, and
project context across conversations.

## Setup

```bash
# 1. Start the memory server
docker run -p 8000:8000 generalintelect/gi-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the agent
GI_URL=http://localhost:8000 OPENAI_API_KEY=sk-... python agent.py
```

## Example session

```
Session ID (press Enter for 'default'): my-project

You: I keep getting a KeyError on 'user_id' in my Flask app
Agent: Based on your past sessions, you've had similar issues with missing
       request context. Try using request.json.get('user_id') instead of
       request.json['user_id'] to avoid the KeyError...

You: quit
```

Start a new terminal, run again with the same session ID — the agent will
remember the previous conversation.
