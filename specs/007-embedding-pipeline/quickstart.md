# Quickstart: Book Content Embedding Pipeline

**Feature**: `007-embedding-pipeline` | **Date**: 2026-03-09

---

## Prerequisites

- Python 3.11+ installed
- [`uv`](https://docs.astral.sh/uv/) installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A [Cohere](https://cohere.com) account with an API key (free tier works)
- A [Qdrant Cloud](https://cloud.qdrant.io) account with a cluster URL and API key (free tier works)

---

## Setup

### 1. Create the backend project

```bash
# From the repo root
mkdir backend
cd backend
uv init --no-workspace
```

### 2. Install dependencies

```bash
uv add httpx beautifulsoup4 lxml cohere qdrant-client python-dotenv tqdm
uv add --dev pytest
```

### 3. Configure environment

```bash
# In backend/
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BASE_URL=https://hackathon-book-uogx.vercel.app/
COHERE_API_KEY=<your-cohere-api-key>
QDRANT_URL=https://<your-cluster-id>.qdrant.io
QDRANT_API_KEY=<your-qdrant-api-key>
```

Optional overrides (leave defaults unless needed):

```env
COLLECTION_NAME=book-embeddings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBED_BATCH_SIZE=96
```

---

## Run the Pipeline

```bash
# From backend/
uv run python main.py
```

Expected output:

```
[CRAWL]  Fetching sitemap from https://hackathon-book-uogx.vercel.app/sitemap.xml
[CRAWL]  Found 42 URLs
[FETCH]  Fetching 42 pages...
[FETCH]  42 fetched, 0 skipped
[CHUNK]  1,284 chunks from 42 pages
[EMBED]  Embedding 1,284 chunks in 14 batches...
[STORE]  Collection 'book-embeddings' ready
[STORE]  1,284 points upserted
[VERIFY] Test query: "What is a digital twin?"
         1. (0.91) https://hackathon-book-uogx.vercel.app/module2/...
            "A digital twin is a virtual representation of a physical system..."
         2. (0.88) ...
         3. (0.85) ...
[DONE]   42 pages | 1,284 chunks | 1,284 vectors stored
```

---

## Re-running

Re-running the pipeline against the same URL is safe — all points are upserted (overwritten) by deterministic ID. No duplicate vectors are created.

```bash
# Safe to run multiple times
uv run python main.py
```

---

## Run Tests

```bash
cd backend/
uv run pytest
```

Tests cover:
- `clean_html()` — strips nav/footer, returns title + text
- `chunk_text()` — correct chunk count, overlap, min-size filtering
- Configuration validation — missing env vars raise `ValueError`

---

## Verify Results in Qdrant Console

1. Log in to [Qdrant Cloud](https://cloud.qdrant.io)
2. Open your cluster → Collections → `book-embeddings`
3. Confirm point count matches pipeline output
4. Use the console search to run a test query

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ValueError: BASE_URL is required` | Check `.env` file exists and has all required keys |
| `CohereAPIError: 401` | Verify `COHERE_API_KEY` in `.env` |
| `UnexpectedResponse: 401` | Verify `QDRANT_API_KEY` and `QDRANT_URL` in `.env` |
| Sitemap returns 404 | Set `BASE_URL` to a different root or check the Vercel deployment |
| 0 chunks produced | Page content may be minimal; lower `MIN_CHUNK_CHARS` in `.env` |
| Pipeline slow | Reduce `CHUNK_SIZE` or ensure network connection is stable |
