export interface GIClientOptions {
  url?: string;
  agentId: string;
  defaultNamespace?: string;
  timeout?: number;
}

export interface RecallResult {
  id: string;
  content: string;
  score: number;
  age_seconds: number;
}

function formatContext(results: RecallResult[]): string {
  if (results.length === 0) return "";
  const lines = results.map((r) => `- ${r.content}`).join("\n");
  return `[Memory context]\n${lines}\n`;
}

/**
 * General Intellect client for Node.js / TypeScript agents.
 *
 * Usage:
 *   const gi = new GIClient({ url: "http://localhost:8000", agentId: "support-bot" });
 *   const context = await gi.recall({ query: transcript, namespace: callId });
 *   await gi.remember({ content: transcript, namespace: callId });
 */
export class GIClient {
  private url: string;
  private agentId: string;
  private defaultNamespace: string;
  private timeout: number;

  constructor(options: GIClientOptions) {
    this.url = (options.url ?? process.env.GI_URL ?? "").replace(/\/$/, "");
    this.agentId = options.agentId;
    this.defaultNamespace = options.defaultNamespace ?? "default";
    this.timeout = options.timeout ?? 5000;
  }

  private get enabled(): boolean {
    return this.url.length > 0;
  }

  async remember(options: {
    content: string;
    namespace?: string;
    metadata?: Record<string, unknown>;
  }): Promise<string | null> {
    if (!this.enabled) return null;
    const res = await fetch(`${this.url}/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: this.agentId,
        namespace: options.namespace ?? this.defaultNamespace,
        content: options.content,
        metadata: options.metadata ?? {},
      }),
      signal: AbortSignal.timeout(this.timeout),
    });
    if (!res.ok) throw new Error(`GI write failed: ${res.status}`);
    const data = (await res.json()) as { id: string };
    return data.id;
  }

  async recall(options: {
    query: string;
    namespace?: string;
    topK?: number;
  }): Promise<string> {
    if (!this.enabled) return "";
    const res = await fetch(`${this.url}/memory/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: this.agentId,
        namespace: options.namespace ?? this.defaultNamespace,
        query: options.query,
        top_k: options.topK ?? 3,
      }),
      signal: AbortSignal.timeout(this.timeout),
    });
    if (!res.ok) throw new Error(`GI query failed: ${res.status}`);
    const data = (await res.json()) as { results: RecallResult[] };
    return formatContext(data.results);
  }

  async forget(memId: string): Promise<void> {
    if (!this.enabled) return;
    const res = await fetch(`${this.url}/memory/${memId}`, {
      method: "DELETE",
      signal: AbortSignal.timeout(this.timeout),
    });
    if (!res.ok && res.status !== 404) {
      throw new Error(`GI delete failed: ${res.status}`);
    }
  }
}
