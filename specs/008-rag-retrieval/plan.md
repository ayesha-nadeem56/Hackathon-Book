# Implementation Plan: RAG Retrieval Validation Pipeline

**Branch**: `008-rag-retrieval` | **Date**: 2026-03-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-rag-retrieval/spec.md`

## Summary

Build `backend/retrieve.py` — a single-file retrieval validation script that:
1. Loads credentials from the shared `.env` (COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME).
2. Embeds each query using Cohere `ClientV2` with `input_type="search_query"`.
3. Calls `client.query_points()` on Qdrant (v1.17 API) to retrieve the top-K most similar chunks.
4. Prints each result with rank, score, source URL, and text snippet.
5. Validates that every result payload contains all required fields (url, title, chunk_index, text).
6. Exits with code 0 on success and non-zero on connection / config errors.

Depends entirely on the Qdrant collection (`book-embeddings`) populated by Spec-1 (007-embedding-pipeline). No new dependencies required.

---

## Technical Context

**Language/Version**: Python 3.14.2 (managed with `uv`)
**Primary Dependencies**: `cohere` (ClientV2, v5+), `qdrant-client==1.17.0`, `python-dotenv` — all already in `backend/pyproject.toml` from Spec-1
**Storage**: Qdrant Cloud (read-only; collection `book-embeddings` pre-populated with 74 vectors)
**Testing**: pytest (manual invocation; no new test fixtures required at this stage)
**Target Platform**: Windows / Linux CLI (developer workstation)
**Project Type**: Single-file script, extends existing `backend/` project
**Performance Goals**: All queries complete in < 10 seconds for up to 10 queries (SC-003)
**Constraints**: Free-tier Qdrant (1 collection, 30-day inactivity timeout); no re-embedding; read-only
**Scale/Scope**: Validation script — single developer, 3–10 test queries per run

---

## Constitution Check

*GATE: Must pass before Phase 0 research.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Accuracy & Technical Correctness | ✅ PASS | Uses same Cohere model + Qdrant collection as Spec-1; no model drift |
| II. Clarity & Readability | ✅ PASS | Single file, clear CLI usage, printed output with rank/score/URL/snippet |
| III. Reproducibility of Workflows | ✅ PASS | All config via `.env`; `uv run` invocation fully reproducible |
| IV. Modularity & Maintainable Architecture | ✅ PASS | Smallest viable change; single file added to existing `backend/` project |
| V. Transparency in AI-Generated Content | ✅ PASS | Retrieval-only; no generation, hallucination risk is zero in this script |

**Gate result: ALL PASS — no violations to justify.**

---

## Project Structure

### Documentation (this feature)

```text
specs/008-rag-retrieval/
├── plan.md              ✅ This file
├── research.md          ✅ Phase 0 output
├── data-model.md        ✅ Phase 1 output
├── quickstart.md        ✅ Phase 1 output
├── contracts/
│   └── retrieval-cli.md ✅ Phase 1 output
└── tasks.md             (Phase 2 — /sp.tasks command)
```

### Source Code (repository)

```text
backend/
├── main.py              # Spec-1: embedding pipeline (unchanged)
├── retrieve.py          # NEW: retrieval validation script (this feature)
├── .env                 # Shared credentials (gitignored)
├── .env.example         # Placeholder template
└── pyproject.toml       # uv project — no new deps needed
```

**Structure Decision**: Single-file script added to the existing `backend/` project. No new packages, no new directories. Shares `.env`, `pyproject.toml`, and the `uv` virtual environment from Spec-1.

---

## Phase 0: Research Findings

See [research.md](research.md) for full findings. Key decisions:

| Decision | Rationale |
|----------|-----------|
| `cohere.ClientV2` with `input_type="search_query"` | Matches Spec-1 ingestion model; asymmetric embedding required for cosine similarity to work correctly |
| `client.query_points()` (not `client.search()`) | `search()` removed in qdrant-client 1.17; `query_points()` is the current API |
| Exit codes: 0 success / 1 config error / 2 connection error / 3 empty collection | Clear error taxonomy for scripting and CI integration |
| Hardcoded default queries + CLI argv override (FR-007) | Lets developers run without arguments for a quick sanity check |
| `TOP_K` default=3, `SCORE_THRESHOLD` default=None (FR-006) | Matches spec defaults; no filtering by default |

---

## Phase 1: Design

### Data Model

See [data-model.md](data-model.md) for entity definitions. Summary:

- **Config**: all settings loaded from `.env`; validated on startup; raises `SystemExit(1)` if missing
- **Query**: `str` — natural-language input
- **RetrievalResult**: `score: float`, `url: str`, `title: str`, `chunk_index: int`, `text: str`
- **ValidationReport**: per-result field validation summary + overall pass/fail

### API Contract

See [contracts/retrieval-cli.md](contracts/retrieval-cli.md). The script exposes a CLI interface:

```
uv run python retrieve.py [query1] [query2] ...
```

Returns human-readable ranked results to stdout; exits 0 on success.

---

## Implementation Checklist

- [ ] `load_config()` — reads `.env`, validates required keys, raises `SystemExit(1)` on missing
- [ ] `init_qdrant()` — creates `QdrantClient`, verifies collection exists, raises `SystemExit(2)` on failure
- [ ] `embed_query()` — calls `cohere.ClientV2.embed()` with `input_type="search_query"`
- [ ] `retrieve()` — calls `client.query_points()`, applies `SCORE_THRESHOLD` filter, returns top-K results
- [ ] `validate_payload()` — checks url/title/chunk_index/text fields; logs `WARNING` for missing
- [ ] `print_results()` — formats rank, score, URL, snippet to stdout
- [ ] `main()` — orchestrates all above; accepts `sys.argv[1:]` as queries; exits with correct code
- [ ] Default query list (3–5 known book topics) used when no CLI args provided
- [ ] UTF-8 stdout fix (Windows compatibility, same as Spec-1)

---

## Risks & Follow-ups

1. **Qdrant collection empty / expired**: Free tier has 30-day inactivity timeout. Script must check collection point count and exit with code 3 + clear message if zero vectors found.
2. **Cohere API rate limit**: Unlikely for 3–10 queries, but script should propagate the exception with a readable message rather than a stack trace.
3. **Next**: Run `/sp.tasks` to generate granular, testable task list, then `/sp.implement` to produce `backend/retrieve.py`.
