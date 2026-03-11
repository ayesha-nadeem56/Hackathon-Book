# Data Model: FastAPI RAG Integration

**Feature**: 010-fastapi-rag-integration
**Date**: 2026-03-11
**Derived from**: spec.md entities + agent.py payload structure

---

## Entities

### 1. QueryRequest

Represents a single user question sent from the frontend chatbot to the API.

| Field     | Type   | Required | Constraints               | Notes                              |
|-----------|--------|----------|---------------------------|------------------------------------|
| `query`   | string | Yes      | Non-empty, ≤ 2,000 chars  | The user's natural-language question |

**Validation rules**:
- `query` MUST NOT be null, empty string, or whitespace-only → HTTP 400
- `query` length MUST NOT exceed 2,000 characters → HTTP 400

**Source**: FR-001, FR-005

---

### 2. QueryResponse

Represents the API's reply to a successful query. Returned on HTTP 200.

| Field     | Type                | Required | Notes                                          |
|-----------|---------------------|----------|------------------------------------------------|
| `answer`  | string              | Yes      | The agent's grounded response text             |
| `sources` | array[SourceReference] | Yes   | Retrieved passages that grounded the answer; may be empty if none found |

**Invariants**:
- `answer` is always a non-empty string (may be the "no relevant content" message)
- `sources` is always an array (never null); may be `[]`

**Source**: FR-001, FR-002

---

### 3. SourceReference

A single cited book passage included in a `QueryResponse`.

| Field   | Type   | Required | Notes                                          |
|---------|--------|----------|------------------------------------------------|
| `url`   | string | Yes      | Absolute URL to the book page containing this passage |
| `title` | string | No       | Human-readable page title; empty string if unavailable |

**Derived from**: Qdrant payload fields `url` and `title` in `agent.py:retrieve_from_qdrant()`.

**Source**: FR-001

---

### 4. ErrorResponse

Returned on any API error (HTTP 400, 503, 504).

| Field   | Type   | Required | Notes                                  |
|---------|--------|----------|----------------------------------------|
| `error` | string | Yes      | Human-readable description of the failure |

**Source**: FR-003

---

### 5. HealthStatus

Returned by the health endpoint on GET `/health`.

| Field          | Type   | Required | Values               | Notes                                       |
|----------------|--------|----------|----------------------|---------------------------------------------|
| `status`       | string | Yes      | `"ok"`, `"degraded"` | Overall service readiness                   |
| `dependencies` | object | Yes      | —                    | Map of dependency name → status string      |

**`dependencies` keys**:
- `"qdrant"`: `"ok"` or `"unreachable"`
- `"agent"`: `"ok"` or `"not_initialized"`

**Source**: FR-004

---

## Relationships

```
QueryRequest
    │  (received by FastAPI POST /query)
    ▼
QueryResponse
    ├── answer: string (from Runner.run → result.final_output)
    └── sources: [ SourceReference, ... ]
                  (from Qdrant payload: url, title)

GET /health → HealthStatus
               └── dependencies: { qdrant: ..., agent: ... }

Any error → ErrorResponse
```

---

## Existing Qdrant Payload Schema (from `backend/main.py`)

Each vector point stored by the embedding pipeline has this payload:

| Field         | Type    | Notes                                   |
|---------------|---------|-----------------------------------------|
| `url`         | string  | Source page URL                         |
| `title`       | string  | Page title                              |
| `chunk_index` | integer | Position of this chunk within the page  |
| `text`        | string  | Raw chunk text (up to ~1,000 chars)     |
| `char_count`  | integer | Character length of the chunk           |

The `SourceReference` entity maps: `url` → `url`, `title` → `title`.

---

## Agent State (Runtime, not persisted)

The FastAPI server holds these objects in `app.state` (singleton, created at startup):

| Name         | Type        | Lifecycle                          |
|--------------|-------------|------------------------------------|
| `agent`      | `Agent`     | Created once in `lifespan()`; reused across requests |
| `run_config` | `RunConfig` | Created once in `lifespan()`; reused across requests |

Each request is **stateless** — no session memory is persisted across HTTP calls (per spec Out of Scope).
