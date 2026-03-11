# Feature Specification: FastAPI RAG Integration — Backend-Frontend Bridge

**Feature Branch**: `010-fastapi-rag-integration`
**Created**: 2026-03-11
**Status**: Draft
**Input**: Integrate backend RAG system with frontend using FastAPI

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Queries the RAG Agent via HTTP (Priority: P1)

A developer runs the FastAPI server locally and submits a natural-language question via an HTTP POST request. The server delegates the query to the RAG agent (from Spec 009), retrieves relevant book passages, and returns a grounded JSON response containing the agent's answer and source references.

**Why this priority**: This is the foundational integration point — without a working query endpoint that calls the RAG agent, no frontend interaction is possible. All other stories depend on this working correctly.

**Independent Test**: Start the server. Send a POST request with a JSON body containing a question matching a known book topic. Confirm the response is valid JSON containing an answer field with grounded content and a sources field listing at least one passage reference.

**Acceptance Scenarios**:

1. **Given** the server is running and the vector store is populated, **When** a client POSTs `{"query": "What is ROS2?"}`, **Then** the server returns HTTP 200 with a JSON body containing `answer` (non-empty string) and `sources` (array of references).
2. **Given** the server is running and the question matches no book content, **When** a client POSTs a question outside the book's scope, **Then** the server returns HTTP 200 with `answer` indicating no relevant content was found and `sources` as an empty array.
3. **Given** the server is running but the vector store is unreachable, **When** a client submits any query, **Then** the server returns HTTP 503 with a JSON error body describing the retrieval failure.

---

### User Story 2 — Frontend Sends a Query and Displays the Response (Priority: P2)

A frontend client (browser or static site widget) presents an input form. The user types a question and submits it. The frontend sends the query to the FastAPI server and renders the returned answer and source citations in the UI — without the user needing to know about the backend implementation.

**Why this priority**: The frontend integration closes the end-to-end loop. A working API without a consuming frontend delivers no user-facing value. This story validates the full data flow from user input to rendered output.

**Independent Test**: Open the frontend in a browser. Enter a question in the chat widget. Confirm the widget shows a loading indicator while awaiting the response, then renders the answer text and a list of source citations after the response arrives — all without page reload.

**Acceptance Scenarios**:

1. **Given** the frontend is loaded and the server is running, **When** the user submits a question, **Then** the UI shows a loading state within 300 ms and renders the full answer within 10 seconds.
2. **Given** the server returns an error response, **When** the frontend receives it, **Then** the UI displays a user-readable error message without crashing or showing raw JSON.
3. **Given** the user submits an empty question, **When** they click submit, **Then** the frontend prevents the request and shows a validation message prompting them to enter a question.

---

### User Story 3 — Health Check Confirms Service Readiness (Priority: P3)

An operator or CI pipeline calls the server's health endpoint to confirm the service is ready to accept queries — specifically that it can reach the vector store and the AI service.

**Why this priority**: A health check enables deployment verification and integration testing without requiring a full query round-trip. It also allows frontend code to gracefully degrade when the backend is unavailable.

**Independent Test**: Start the server. Send a GET request to the health endpoint. Confirm the response is HTTP 200 with a JSON body indicating all dependencies (vector store, AI service) are reachable. Stop the vector store and confirm the health endpoint returns a non-200 status.

**Acceptance Scenarios**:

1. **Given** all dependencies are healthy, **When** a GET request is sent to the health endpoint, **Then** the server responds with HTTP 200 and a JSON body with `status: "ok"`.
2. **Given** the vector store is unavailable, **When** a GET request is sent to the health endpoint, **Then** the server responds with a non-200 status code and a JSON body naming the failing dependency.

---

### Edge Cases

- What if the client sends a request with a missing or malformed `query` field?
- What if the RAG agent takes longer than the expected timeout to respond?
- What if the frontend and backend run on different origins — does the API handle cross-origin requests?
- What if the client sends a query that is empty, whitespace-only, or exceeds a reasonable character limit?
- What if the AI service returns a rate-limit error during a query?
- What if multiple concurrent requests arrive simultaneously?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an HTTP POST endpoint that accepts a JSON body containing a `query` field (string) and returns a JSON response containing `answer` (string) and `sources` (array of objects with at minimum a `url` field).
- **FR-002**: System MUST delegate every incoming query to the RAG agent (Spec 009) and return only grounded answers derived from retrieved book passages — it MUST NOT generate speculative answers.
- **FR-003**: System MUST return a structured error response (with a descriptive `error` field) for any recoverable failure, using appropriate HTTP status codes (400 for bad input, 503 for dependency failures).
- **FR-004**: System MUST expose an HTTP GET health endpoint that checks connectivity to the vector store and AI service and reports their status in a JSON response.
- **FR-005**: System MUST reject requests where `query` is absent, empty, or contains only whitespace, returning HTTP 400 with a descriptive error message.
- **FR-006**: System MUST allow cross-origin requests from the frontend's local development origin so the frontend can communicate with the backend without browser security errors.
- **FR-007**: All service credentials and configuration values (AI service keys, vector store connection, port number) MUST be loaded from environment variables — none may be hardcoded.
- **FR-008**: System MUST complete a query round-trip (receive request → invoke agent → return response) within a defined timeout; if exceeded, the server MUST return HTTP 504 with an appropriate error message.
- **FR-009**: The frontend integration MUST send queries to the backend via HTTP, render the returned `answer` text, and display each entry in `sources` with at minimum a clickable URL.

### Key Entities

- **QueryRequest**: Represents a single user question sent from the frontend. Contains a `query` field (non-empty string). Optionally may include `session_id` for future conversational context support.
- **QueryResponse**: Represents the server's reply to a query. Contains `answer` (string — grounded response from the RAG agent) and `sources` (array of source objects, each with a `url` and optionally `title` and `excerpt`).
- **SourceReference**: A single cited book passage returned within a `QueryResponse`. Contains at minimum a `url` linking back to the relevant book section.
- **HealthStatus**: Represents the service readiness report. Contains `status` (string: "ok" or "degraded") and a `dependencies` map showing the health of each downstream service.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A question submitted through the frontend returns a grounded answer rendered in the UI within 10 seconds under normal conditions.
- **SC-002**: 100% of query responses return valid, parseable JSON with the specified `answer` and `sources` structure — no raw text or unstructured errors escape to the client under normal operation.
- **SC-003**: The health endpoint correctly reports a non-healthy status within 2 seconds when any dependency (vector store or AI service) is unreachable.
- **SC-004**: Invalid or empty query requests are rejected at the API boundary — zero such requests reach the RAG agent.
- **SC-005**: The end-to-end integration (frontend → API → RAG agent → response rendered in UI) works without errors in a local development environment, validated by a manual walkthrough covering at least 3 distinct questions.

---

## Assumptions

- The RAG agent from Spec 009 is already operational and accessible programmatically (i.e., it can be invoked as a function/module, not only via its own CLI).
- The vector store (Qdrant) is populated with book content and accessible during local development.
- The frontend is a Docusaurus-based static site running on a local development server; it communicates with the backend over HTTP on the same machine.
- A single query endpoint (no streaming) is sufficient for the initial integration — streaming responses are out of scope.
- Session/conversational memory across multiple HTTP requests is out of scope for this feature; each request is treated as independent.
- Authentication between the frontend and backend is out of scope for local development — the API is unprotected and intended only for local use.
- The character limit for a query is assumed to be 2,000 characters as a reasonable upper bound; this may be adjusted in planning.
- Cross-origin resource sharing (CORS) configuration allows the local frontend origin (e.g., `http://localhost:3000`) by default.

---

## Out of Scope

- Streaming (chunked/SSE) response delivery to the frontend
- Multi-turn conversational memory persisted across HTTP requests
- User authentication or API key protection
- Production deployment, containerisation, or cloud hosting
- Rate limiting or request throttling
- Analytics, logging pipelines, or observability infrastructure beyond basic error reporting
