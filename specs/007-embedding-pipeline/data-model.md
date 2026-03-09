# Data Model: Book Content Embedding Pipeline

**Feature**: `007-embedding-pipeline` | **Date**: 2026-03-09

---

## Python Types (dataclasses in `main.py`)

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Page:
    """A single fetched documentation page."""
    url: str               # canonical URL as found in sitemap
    title: str             # extracted from <title> or first <h1>
    text: str              # cleaned plain text (post-BeautifulSoup)
    http_status: int       # HTTP response status code
    crawled_at: datetime   # UTC timestamp of fetch


@dataclass
class Chunk:
    """A text segment derived from a Page."""
    page_url: str          # parent page URL
    page_title: str        # parent page title (for payload)
    chunk_index: int       # 0-based position within the page
    text: str              # verbatim chunk text
    char_count: int        # len(text)

    @property
    def point_id(self) -> str:
        """Deterministic UUID5 for Qdrant — stable across re-runs."""
        import uuid
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.page_url}#{self.chunk_index}"))


@dataclass
class EmbeddedChunk:
    """A Chunk paired with its embedding vector."""
    chunk: Chunk
    vector: list[float]    # 1024-dimension float vector from Cohere
```

---

## Qdrant Point Schema

Each embedded chunk is stored as a Qdrant `PointStruct`:

```
PointStruct:
  id:     str (UUID5)        — deterministic from (url + chunk_index)
  vector: list[float]        — 1024-dim float32 cosine vector
  payload:
    url:         str         — source page URL
    title:       str         — page title
    chunk_index: int         — 0-based chunk position on page
    text:        str         — verbatim chunk text (shown in retrieval results)
    char_count:  int         — character count of text
```

---

## Qdrant Collection Configuration

```
Collection name:   book-embeddings  (from COLLECTION_NAME env var)
Vector config:
  size:            1024
  distance:        Cosine
On conflict:       Upsert (overwrite by point_id — idempotent re-runs)
```

---

## State Transitions

```
URL (string)
  ──[crawl]──▶  Page  (url, title, text, status, crawled_at)
  ──[chunk]──▶  Chunk[]  (page_url, chunk_index, text, char_count)
  ──[embed]──▶  EmbeddedChunk[]  (chunk + vector)
  ──[store]──▶  Qdrant PointStruct[]  (id, vector, payload)
```

---

## Validation Rules

| Field | Rule |
|-------|------|
| `Page.http_status` | Must be 2xx to proceed; others are logged and skipped |
| `Page.text` | Must be ≥ `MIN_CHUNK_CHARS` after cleaning; else page is skipped |
| `Chunk.char_count` | Must be ≥ `MIN_CHUNK_CHARS`; shorter chunks are dropped |
| `EmbeddedChunk.vector` | Must have length == 1024 (asserted post-embed) |
| Required env vars | `BASE_URL`, `COHERE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY` — raise `ValueError` if missing |

---

## Configuration Object

```python
@dataclass
class Config:
    base_url: str
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    collection_name: str = "book-embeddings"
    cohere_model: str = "embed-english-v3.0"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embed_batch_size: int = 96
    min_chunk_chars: int = 100
```

Loaded from environment variables via `python-dotenv` at startup. All four required fields raise `ValueError` if absent.
