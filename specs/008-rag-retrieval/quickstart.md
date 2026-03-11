# Quickstart: RAG Retrieval Validation Script

**Feature**: 008-rag-retrieval | **Date**: 2026-03-10

---

## Prerequisites

- [ ] Spec-1 (007-embedding-pipeline) has been run successfully and `book-embeddings` collection in Qdrant is populated.
- [ ] `backend/.env` exists with `QDRANT_URL`, `QDRANT_API_KEY`, `COLLECTION_NAME`, and `COHERE_API_KEY` set.
- [ ] Python 3.11+ and `uv` are installed. (On Windows: `python -m uv` if `uv` is not in PATH.)

---

## Step 1: Navigate to backend/

```bash
cd backend/
```

---

## Step 2: Verify .env is populated

```bash
# Check the required keys exist (do NOT print values):
grep -E "^(QDRANT_URL|QDRANT_API_KEY|COLLECTION_NAME|COHERE_API_KEY)=" .env
```

Expected: 4 lines printed.

---

## Step 3: Run with default queries

```bash
uv run python retrieve.py
```

Expected output: 5 queries × 3 results each, followed by a validation report showing `Overall: PASS`.

---

## Step 4: Run with custom queries

```bash
uv run python retrieve.py "What is prompt engineering?" "How do AI agents work?"
```

Expected: 2 queries, up to 3 results each (or fewer if SCORE_THRESHOLD filters some out).

---

## Step 5: Test TOP_K and SCORE_THRESHOLD

```bash
# Return only 1 result per query, minimum score 0.6:
TOP_K=1 SCORE_THRESHOLD=0.6 uv run python retrieve.py "What is retrieval-augmented generation?"
```

On Windows PowerShell:
```powershell
$env:TOP_K=1; $env:SCORE_THRESHOLD=0.6; uv run python retrieve.py "What is retrieval-augmented generation?"
```

Expected: exactly 1 result with score ≥ 0.60 (or 0 results if no match exceeds threshold).

---

## Success Criteria Verification

| SC | How to verify |
|----|--------------|
| SC-001: ≥1 result with score > 0.5 for known topics | Inspect output scores for default queries |
| SC-002: 100% of results have all metadata fields | Validation report shows `Metadata valid: N / N` |
| SC-003: < 10 seconds for 10 queries | Time the run with `time uv run python retrieve.py` |
| SC-004: TOP_K and SCORE_THRESHOLD work via env | Step 5 above |
| SC-005: Exit code 0 on success | `echo $?` (bash) or `echo $LASTEXITCODE` (PS) after run |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ERROR: Required environment variable 'QDRANT_URL' is not set` | Check `backend/.env` has all 4 required keys |
| `ERROR: Cannot connect to Qdrant` | Verify QDRANT_URL and QDRANT_API_KEY; check cluster is active |
| `ERROR: Collection 'book-embeddings' not found` | Re-run `uv run python main.py` to populate embeddings |
| `ERROR: Collection exists but contains 0 vectors` | Re-run `uv run python main.py` |
| `UnicodeEncodeError` on Windows | Script includes UTF-8 fix; ensure Python ≥ 3.7 |
| Low scores (< 0.4) for all queries | Verify same `COHERE_MODEL` used in both main.py and retrieve.py |
