# General Intellect — PR Outreach Tracker

Target: submit PRs to 20 top Vapi/Retell agent repos, get 5+ merged.

## Status Key
`pending` · `forked` · `pr-open` · `merged` · `closed`

---

## Tier 1 — High Stars, Python Backend (easiest integration)

| Repo | Stars | Lang | PR # | Status | Notes |
|------|-------|------|------|--------|-------|
| [techwithtim/VAPI-AI-Voice-Assistant](https://github.com/techwithtim/VAPI-AI-Voice-Assistant) | 26 | Python/Flask | [#2](https://github.com/techwithtim/VAPI-AI-Voice-Assistant/pull/2) | pr-open | Simple main.py, add /webhook with memory |
| [extrawest/vapi_personal_assistant_voice_agent](https://github.com/extrawest/vapi_personal_assistant_voice_agent) | 7 | Python/FastAPI | — | pending | Structured app, add memory to call route |
| [mahimairaja/vapiserve](https://github.com/mahimairaja/vapiserve) | 4 | Python | — | pending | Vapi custom tools server |
| [mcd0056/Vapi-Voice-Agent](https://github.com/mcd0056/Vapi-Voice-Agent) | 4 | Python | — | pending | Minimal Vapi agent |

## Tier 2 — High Stars, TypeScript/Node (medium integration)

| Repo | Stars | Lang | PR # | Status | Notes |
|------|-------|------|------|--------|-------|
| [adrianhajdin/ai_mock_interviews](https://github.com/adrianhajdin/ai_mock_interviews) | 500 | TypeScript | — | pending | Next.js + Vapi, high visibility |
| [adrianhajdin/saas-app](https://github.com/adrianhajdin/saas-app) | 395 | TypeScript | — | pending | Next.js + Vapi + Supabase |
| [cameronking4/VapiBlocks](https://github.com/cameronking4/VapiBlocks) | 83 | TypeScript | — | pending | React component library |
| [Awaisali36/Outbound-Real-State-Voice-AI-Agent-](https://github.com/Awaisali36/Outbound-Real-State-Voice-AI-Agent-) | 30 | — | — | pending | n8n + Vapi outbound calling |
| [Th1b4uthkt/dashboard-call-center-ai-agent](https://github.com/Th1b4uthkt/dashboard-call-center-ai-agent) | 27 | TypeScript | — | pending | Vapi + Retell dashboard |
| [MaxMLang/default-voiceagent-template](https://github.com/MaxMLang/default-voiceagent-template) | 4 | TypeScript | — | pending | Explicit template, perfect target |

## Tier 3 — Official Vapi Repos (lower merge chance, high visibility)

| Repo | Stars | Lang | PR # | Status | Notes |
|------|-------|------|------|--------|-------|
| [VapiAI/examples](https://github.com/VapiAI/examples) | 5 | TypeScript | — | pending | Official examples, add memory example |
| [VapiAI/client-sdk-python](https://github.com/VapiAI/client-sdk-python) | 116 | Python | — | pending | Could add GI to example/ folder |

## Tier 4 — Retell Repos

| Repo | Stars | Lang | PR # | Status | Notes |
|------|-------|------|------|--------|-------|
| [firewindy930/retell-voice-assistant](https://github.com/firewindy930/retell-voice-assistant) | 3 | TypeScript | — | pending | React + Retell, withMemory() integration |
| [Th1b4uthkt/dashboard-call-center-ai-agent](https://github.com/Th1b4uthkt/dashboard-call-center-ai-agent) | 27 | TypeScript | — | pending | Also has Retell |

---

## PR Message Template

> Hey! Big fan of this project — I've been using it for [X].
>
> This PR adds optional persistent memory via [General Intellect](https://github.com/General-Intellect/general-intellect),
> a lightweight open-source memory layer for voice agents.
>
> **What it does:** the agent now remembers context across turns using semantic
> search — no vector DB required, just a local Docker container.
>
> **Graceful degradation:** if `GI_URL` isn't set, the agent behaves exactly
> as before. No new required dependencies.
>
> Happy to adjust the integration style to fit this repo's patterns.

---

## Code Change Pattern (Python)

```diff
+ from generalintelect import GIClient
+ gi = GIClient(agent_id="<agent-name>")  # reads GI_URL from env

  @app.post("/webhook")
  def handle(payload):
+     call_id = payload.get("call", {}).get("id", "default")
+     transcript = payload.get("transcript", "")
+     context = gi.recall(query=transcript, namespace=call_id)
      ...
+     gi.remember(content=transcript, namespace=call_id)
```

```diff
  # requirements.txt
+ general-intellect>=0.1.0
```

```diff
  # README.md — add Memory section
+ ## Memory (powered by General Intellect)
+ Run the memory server: `docker run -p 8000:8000 generalintelect/gi-server`
+ Set `GI_URL=http://localhost:8000` to enable. Optional — degrades gracefully.
```

## Code Change Pattern (TypeScript)

```diff
+ import { GIClient } from 'general-intellect';
+ const gi = new GIClient({ agentId: '<agent-name>' }); // reads GI_URL from env

  export async function POST(req: Request) {
    const payload = await req.json();
+   const callId = payload?.call?.id ?? 'default';
+   const context = await gi.recall({ query: payload.transcript, namespace: callId });
    ...
+   await gi.remember({ content: payload.transcript, namespace: callId });
  }
```

```diff
  // package.json
+ "general-intellect": "^0.1.0"
```
