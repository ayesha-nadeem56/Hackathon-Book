# Feature Specification: RAG Retrieval Validation Pipeline

**Feature Branch**: `008-rag-retrieval`
**Created**: 2026-03-10
**Status**: Draft
**Input**: User description: "Retrieve stored embeddings and validate the RAG retrieval pipeline"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query the Vector Store and Retrieve Relevant Chunks (Priority: P1)

A developer has a populated Qdrant collection (from Spec-1 ingestion) and wants to issue natural-language queries against it. They run a script, see the top-k most relevant text chunks returned for each query, with scores and source metadata, and can confirm the results are semantically correct.

**Why this priority**: This is the core validation gate for the entire RAG system. If retrieval does not return relevant content for known queries, the pipeline is broken regardless of how well ingestion ran.

**Independent Test**: Run the retrieval script with 3-5 known book-topic queries. Confirm each returns at least one chunk whose text clearly relates to the query topic and whose source URL matches the expected chapter.

**Acceptance Scenarios**:

1. **Given** a populated Qdrant collection, **When** the developer runs the retrieval script with a query matching a known chapter topic, **Then** the top result has a similarity score > 0.5 and its source URL points to the correct chapter.
2. **Given** a populated Qdrant collection, **When** the developer queries with a topic not covered in the book, **Then** results are returned but with noticeably lower scores (< 0.4) signalling low confidence.
3. **Given** the Qdrant collection is empty or unreachable, **When** the developer runs the retrieval script, **Then** a clear error message is shown and the script exits with a non-zero code.

---

### User Story 2 - Validate Metadata Integrity of Retrieved Chunks (Priority: P2)

A developer inspects the retrieved chunks to confirm that every result carries complete, accurate metadata: source URL, page title, chunk index, and original text. This validates that the ingestion pipeline stored everything correctly.

**Why this priority**: Metadata integrity is required for any downstream use (chatbot attribution, source links, context assembly). Without it, retrieval results cannot be trusted even if scores are high.

**Independent Test**: For any query result, verify that url, title, chunk_index, and text fields are all present, non-empty, and consistent with each other (the URL matches the title's chapter).

**Acceptance Scenarios**:

1. **Given** a retrieved chunk, **When** its payload is inspected, **Then** url, title, chunk_index, and text are all present and non-empty.
2. **Given** a retrieved chunk with chunk_index > 0, **When** the URL is inspected, **Then** it matches the same page URL as chunk_index 0 from the same chapter.
3. **Given** the retrieval script runs successfully, **When** output is reviewed, **Then** every printed result includes both the source URL and a text snippet.

---

### User Story 3 - Configurable Top-K and Score Threshold (Priority: P3)

A developer can control how many results are returned per query (TOP_K) and optionally filter by a minimum similarity score (SCORE_THRESHOLD) via environment variables, without touching source code.

**Why this priority**: Different use cases need different k values and confidence thresholds.

**Independent Test**: Set TOP_K=1 and SCORE_THRESHOLD=0.6. Run a known query. Confirm exactly 1 result is returned with score >= 0.6.

**Acceptance Scenarios**:

1. **Given** TOP_K=5 is configured, **When** a query is run, **Then** at most 5 results are returned.
2. **Given** SCORE_THRESHOLD=0.6 is configured, **When** results below that score exist, **Then** they are excluded from output.
3. **Given** neither variable is set, **When** the script runs, **Then** defaults are used (TOP_K=3, no threshold).

---

### Edge Cases

- What happens if the Qdrant collection name does not match the ingested collection?
- What happens if a retrieved chunk's text field is empty or truncated?
- What if the query string is empty or whitespace-only?
- What if the Cohere API is unavailable when embedding the query?
- What if TOP_K exceeds the total number of stored vectors?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST connect to the configured Qdrant collection and verify it exists before running any query.
- **FR-002**: System MUST embed each query using the same Cohere model used during ingestion, with input_type="search_query".
- **FR-003**: System MUST retrieve the top-K most similar chunks from Qdrant for each query.
- **FR-004**: System MUST display each result with rank, similarity score, source URL, and a text snippet.
- **FR-005**: System MUST validate that each retrieved payload contains all required fields (url, title, chunk_index, text) and log a warning for any missing field.
- **FR-006**: System MUST support configurable TOP_K (default: 3) and optional SCORE_THRESHOLD (default: none) via environment variables.
- **FR-007**: System MUST accept queries from a hardcoded default list OR from command-line arguments (one query per argument).
- **FR-008**: System MUST exit with code 0 on success and non-zero on connection failure, empty collection, or missing config.
- **FR-009**: All configuration (Qdrant URL, API key, collection name, Cohere key, model, TOP_K, SCORE_THRESHOLD) MUST be loadable from .env with no code changes.

### Key Entities

- **Query**: A natural-language string to embed and match against stored vectors.
- **RetrievalResult**: A single returned Qdrant point — score, source URL, title, chunk index, text snippet.
- **ValidationReport**: Summary of a retrieval run — query count, result count, metadata pass/fail per result, overall pass/fail status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 100% of queries covering known book topics, at least 1 result with score > 0.5 is returned.
- **SC-002**: 100% of retrieved results include all required metadata fields (url, title, chunk_index, text).
- **SC-003**: The retrieval script completes all queries in under 10 seconds for up to 10 queries.
- **SC-004**: Configuring TOP_K and SCORE_THRESHOLD via environment variables produces matching results with no code changes.
- **SC-005**: Script exits with code 0 on success and non-zero on connection or configuration errors.

## Assumptions

- The Qdrant collection (book-embeddings) is already populated from Spec-1 (007-embedding-pipeline).
- The same Cohere model (embed-english-v3.0) and collection name used during ingestion are reused here.
- The retrieval script lives in backend/ and shares the .env file and uv project from Spec-1.
- No re-embedding or data modification occurs — retrieval is read-only.
- No new Python dependencies are required beyond what Spec-1 already installed.

## Out of Scope

- LLM reasoning, answer generation, or prompt construction
- Chatbot or conversational interface
- FastAPI or any HTTP endpoint
- Re-embedding, re-indexing, or modifying stored vectors
- UI or frontend integration
- Reranking or hybrid search
