# Research: Book Content Embedding Pipeline

**Feature**: `007-embedding-pipeline` | **Date**: 2026-03-09 | **Phase**: 0

---

## 1. Docusaurus Site Crawling

**Decision**: Parse `sitemap.xml` first; fall back to recursive link crawl if unavailable.

**Rationale**: The project uses the Docusaurus `classic` preset (`docusaurus.config.js` line 37), which bundles `@docusaurus/plugin-sitemap` automatically. The sitemap IS generated at `{BASE_URL}/sitemap.xml` — no explicit plugin config is required. Content lives under `/docs/` (confirmed via `routeBasePath: 'docs'`). Deployed URL confirmed: `https://hackathon-book-uogx.vercel.app/sitemap.xml`.

**Sitemap format**: Standard XML sitemap — `<urlset><url><loc>https://...</loc></url></urlset>`. Parse with `ElementTree` or `BeautifulSoup`.

**Fallback (recursive link crawl)**:
- Start from `BASE_URL`
- Extract all `<a href>` anchors
- Keep only same-domain, HTML-content URLs (skip `.js`, `.css`, `.json`, images, `#` anchors)
- Use a visited-set to avoid loops

**Pages to exclude**:
- Asset paths: `/assets/`, `/_next/`, `/static/`
- Non-content: `404`, search pages, tag indexes
- Already excluded by Docusaurus sitemap automatically

**HTML selectors for content extraction** (Docusaurus v2 structure):
- Main content: `article`, `.markdown`, `[class*="docItemContainer"]`
- Skip: `nav`, `footer`, `.navbar`, `.sidebar`, `.pagination`, `[aria-label="breadcrumb"]`

**Alternatives considered**:
- `scrapy` — too heavy for a single-file script; rejected
- `playwright` — JS rendering not needed for Docusaurus (static HTML); rejected
- Pure `requests` — synchronous; acceptable for small sites; `httpx` preferred for async capability

---

## 2. Cohere Embedding Model

**Decision**: `embed-english-v3.0`

**Rationale**: Latest Cohere English embedding model as of 2026. Superior semantic quality vs v2. Required parameters differ from v2 — must pass `input_type`.

**Specifications**:
- Vector dimension: **1024**
- Maximum input tokens: 512 per text
- API batch limit: **96 texts per call**
- `input_type` values:
  - `"search_document"` — use when indexing chunks into the vector store
  - `"search_query"` — use when embedding a user query for retrieval
- Embedding type: `float` (default) — produces `list[float]` vectors
- Free tier: available with rate limits (~1000 API calls/min on trial)

**Alternatives considered**:
- `embed-multilingual-v3.0` — 1024 dims, supports 100+ languages; overkill for English-only book; rejected
- `embed-english-light-v3.0` — 384 dims; faster but lower quality; rejected for this retrieval use case
- OpenAI `text-embedding-3-small` — not in project tech stack; rejected per constitution

**Python SDK usage** (cohere v5+ uses `ClientV2`):
```python
from cohere import ClientV2
co = ClientV2(api_key=api_key)
response = co.embed(texts=[...], model="embed-english-v3.0", input_type="search_document")
vectors = response.embeddings  # list[list[float]]
```

**Note on batch size**: Cohere API hard limit is 2048 texts per call; recommended 100–500 for reliability. We use 96 as a conservative default to stay well within limits and avoid timeouts on slower connections. This is configurable via `EMBED_BATCH_SIZE`.

---

## 3. Qdrant Collection and Upsert

**Decision**: Cosine distance, 1024 dims; deterministic UUID5 point IDs; upsert for idempotency.

**Collection creation** (qdrant-client v1.x):
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
client.recreate_collection(  # or create_collection if not exists
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)
```

**Point upsert**:
```python
from qdrant_client.models import PointStruct

points = [
    PointStruct(
        id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{url}#{chunk_index}")),
        vector=embedding_vector,
        payload={"url": url, "title": title, "chunk_index": chunk_index, "text": text, "char_count": len(text)},
    )
    for ...
]
client.upsert(collection_name=COLLECTION_NAME, points=points)
```

**Similarity search**:
```python
results = client.search(
    collection_name=COLLECTION_NAME,
    query_vector=query_embedding,
    limit=5,
    with_payload=True,
)
```

**Free Tier Limits** (Qdrant Cloud, verified):
- Storage: ~50 GB per cluster
- **1 collection maximum** — plan accordingly; do not create multiple test collections
- **30-day inactivity timeout** — collection is deleted if unused for 30 days; re-run pipeline to refresh
- 1 vector (1024 dims, float32) = 4 × 1024 bytes = ~4 KB
- 1000 chunks × 4 KB = ~4 MB vector data — well within limits (< 0.01% of 50 GB)
- Payload adds ~1–2 KB/chunk → total estimate ~7 MB for full book corpus

---

## 4. `uv` Package Manager

**Decision**: Use `uv` for project init, dependency management, and script execution.

**Commands**:
```bash
# Initialize new project in existing directory
cd backend/
uv init --no-workspace

# Add runtime dependencies
uv add httpx beautifulsoup4 lxml cohere qdrant-client python-dotenv tqdm

# Add dev dependencies
uv add --dev pytest

# Run the pipeline
uv run python main.py

# Run tests
uv run pytest
```

**`pyproject.toml`** (uv generates this):
```toml
[project]
name = "embedding-pipeline"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "beautifulsoup4>=4.12",
    "lxml>=5.2",
    "cohere>=5.0",
    "qdrant-client>=1.9",
    "python-dotenv>=1.0",
    "tqdm>=4.66",
]

[dependency-groups]
dev = ["pytest>=8.0"]
```

---

## 5. Chunking Strategy

**Decision**: Fixed character-count sliding window with sentence-boundary snapping.

**Parameters** (configurable via env):
- `CHUNK_SIZE`: 1000 characters (default)
- `CHUNK_OVERLAP`: 200 characters (default)
- `MIN_CHUNK_CHARS`: 100 characters minimum to retain a chunk

**Algorithm**:
1. Find candidate split point at `start + CHUNK_SIZE`
2. Walk backward up to 100 chars to find nearest sentence-ending punctuation (`.`, `!`, `?`, `\n`)
3. If found, split there; otherwise split at hard boundary
4. Next chunk starts at `split_point - CHUNK_OVERLAP`
5. Discard chunks shorter than `MIN_CHUNK_CHARS`

**Rationale**: 1000 chars fits comfortably within Cohere's 512-token window (~750 tokens average English text). Overlap preserves cross-boundary context. Sentence snapping avoids cutting mid-sentence.

---

## 6. Resolved Unknowns Summary

| Unknown | Resolution |
|---------|------------|
| Crawling entry point | `https://hackathon-book-uogx.vercel.app/sitemap.xml` |
| Cohere model + dims | `embed-english-v3.0`, 1024 dims |
| Cohere batch limit | 96 texts per call |
| Qdrant point ID scheme | UUID5 from `url + chunk_index` |
| Free tier storage headroom | ~4 MB vectors vs 1 GB limit — ample |
| uv project init | `uv init --no-workspace` in `backend/` |
| Chunk size | 1000 chars / 200 overlap (configurable) |
