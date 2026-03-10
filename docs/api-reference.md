# API Reference

Base URL: `http://localhost:8000`

All request and response bodies are JSON.

---

## Write Memory

```
POST /memory
```

Store a memory for an agent in a namespace.

**Request**

```json
{
  "agent_id": "support-agent-01",
  "namespace": "acme-corp",
  "content": "User prefers email over SMS for notifications",
  "metadata": { "session_id": "sess_123", "turn": 4 }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | yes | Unique agent identifier |
| `namespace` | string | yes | Isolation scope (e.g. call ID, org ID) |
| `content` | string | yes | The text to store |
| `metadata` | object | no | Arbitrary key-value metadata |

**Response**

```json
{ "id": "mem_abc123", "latency_ms": 12 }
```

---

## Query Memory

```
POST /memory/query
```

Retrieve the most semantically relevant memories for a query.

**Request**

```json
{
  "agent_id": "support-agent-01",
  "namespace": "acme-corp",
  "query": "what are this user's notification preferences?",
  "top_k": 3
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `agent_id` | string | yes | — | Must match the writing agent |
| `namespace` | string | yes | — | Must match the writing namespace |
| `query` | string | yes | — | Natural language query |
| `top_k` | integer | no | 3 | Number of results to return |

**Response**

```json
{
  "results": [
    {
      "id": "mem_abc123",
      "content": "User prefers email over SMS for notifications",
      "score": 0.91,
      "age_seconds": 320
    }
  ],
  "latency_ms": 18
}
```

Scores combine semantic similarity (80%) and recency (20%).

---

## Delete Memory

```
DELETE /memory/{id}
```

Delete a specific memory by ID.

**Response**

```json
{ "deleted": "mem_abc123" }
```

Returns `404` if the memory does not exist.

---

## Expire Memories

```
POST /memory/expire
```

Bulk-delete all memories in a namespace older than a threshold.

**Request**

```json
{ "namespace": "acme-corp", "older_than_seconds": 3600 }
```

**Response**

```json
{ "expired": 14 }
```

---

## Health Check

```
GET /health
```

**Response**

```json
{ "status": "ok", "memories": 1423, "namespaces": 7 }
```

---

## Scoring

Retrieval score = `0.8 × semantic_similarity + 0.2 × recency`

- **Semantic similarity**: Hamming distance between 512-bit SimHash vectors derived from `all-MiniLM-L6-v2` embeddings
- **Recency**: `1 / (1 + age_hours)` — memories written in the last hour score near 1.0

## Namespace isolation

Memories are fully isolated by `(agent_id, namespace)`. An agent cannot read memories written by another agent, even in the same namespace.
