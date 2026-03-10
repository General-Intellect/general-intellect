import { GIClient } from "./index";

type WebhookHandler = (payload: Record<string, unknown>) => Promise<unknown>;

/**
 * Wraps a Vapi or Retell webhook handler with automatic memory injection.
 * Gracefully degrades — if GI_URL is not set or the server is unreachable,
 * the handler runs as normal with an empty context.
 *
 * Usage:
 *   const gi = new GIClient({ agentId: "support-bot" });
 *
 *   export const POST = withMemory(gi)(async (payload) => {
 *     const context = payload._gi_context as string;
 *     const response = await llm.complete(systemPrompt + context + transcript);
 *     return { response };
 *   });
 */
export function withMemory(gi: GIClient) {
  return function (handler: WebhookHandler): WebhookHandler {
    return async function (payload: Record<string, unknown>) {
      const callId = extractCallId(payload);
      const message = extractMessage(payload);

      let context = "";
      if (message) {
        try {
          context = await gi.recall({ query: message, namespace: callId });
        } catch {
          // degrade gracefully
        }
      }

      payload._gi_context = context;
      const result = await handler(payload);

      if (message) {
        try {
          await gi.remember({ content: message, namespace: callId });
        } catch {
          // degrade gracefully
        }
      }

      return result;
    };
  };
}

function extractCallId(payload: Record<string, unknown>): string {
  // Vapi
  const vapiCall = payload.call as Record<string, unknown> | undefined;
  if (vapiCall?.id) return vapiCall.id as string;
  // Retell
  if (payload.call_id) return payload.call_id as string;
  return "default";
}

function extractMessage(payload: Record<string, unknown>): string {
  // Vapi: full transcript
  if (payload.transcript) return payload.transcript as string;
  // Vapi: single message content
  const msg = payload.message as Record<string, unknown> | undefined;
  if (msg?.content) return msg.content as string;
  return "";
}
