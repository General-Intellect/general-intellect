/**
 * Retell voice agent webhook with persistent memory via General Intellect.
 *
 * Run:
 *   npm install
 *   GI_URL=http://localhost:8000 OPENAI_API_KEY=... npx ts-node src/webhook.ts
 */

import express from "express";
import OpenAI from "openai";
import { GIClient } from "general-intellect";
import { withMemory } from "general-intellect/vapi";

const app = express();
app.use(express.json());

const gi = new GIClient({ agentId: "retell-support" }); // reads GI_URL from env
const openai = new OpenAI();

const SYSTEM_PROMPT =
  "You are a friendly voice agent. Use any memory context provided to " +
  "personalize your responses. Keep answers short — this is a phone call.";

const agentHandler = withMemory(gi)(async (payload) => {
  const context = (payload._gi_context as string) ?? "";
  const transcript = (payload.transcript as string) ?? "";

  if (!transcript) {
    return { response: "Hello! How can I help you today?" };
  }

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: SYSTEM_PROMPT + (context ? "\n\n" + context : "") },
      { role: "user", content: transcript },
    ],
  });

  return { response: completion.choices[0].message.content };
});

app.post("/webhook", async (req, res) => {
  try {
    const result = await agentHandler(req.body);
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/health", (_req, res) => res.json({ status: "ok" }));

const PORT = process.env.PORT ?? 3000;
app.listen(PORT, () => console.log(`Retell agent running on port ${PORT}`));
