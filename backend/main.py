"""
Book Content Embedding Pipeline
================================
Crawls all public pages from a deployed Docusaurus site, cleans and chunks
the text, generates vector embeddings via Cohere, and upserts them with
source metadata into a Qdrant Cloud collection.

Pipeline stages:
  1. CRAWL  -- discover page URLs via sitemap.xml (fallback: link crawl)
  2. FETCH  -- GET each URL, extract cleaned text
  3. CHUNK  -- sliding-window character chunking with sentence-boundary snap
  4. EMBED  -- Cohere embed-english-v3.0 in configurable batches
  5. STORE  -- Qdrant upsert with deterministic UUID5 point IDs (idempotent)
  6. VERIFY -- embed sample queries and print top-3 results per query

Usage:
    cp .env.example .env   # fill in credentials
    uv run python main.py
"""

# =============================================================================
# Imports
# =============================================================================
import math
import os
import pathlib
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

# Force UTF-8 output on Windows to handle emoji / special characters in book content
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cohere
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm


# =============================================================================
# Logging helper  [T008]
# =============================================================================

def log(stage: str, msg: str) -> None:
    """Print a formatted stage message to stdout."""
    print(f"[{stage:<6}]  {msg}")


# =============================================================================
# Data model  [T006]
# =============================================================================

@dataclass
class Config:
    """All pipeline configuration, loaded from environment variables."""
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


@dataclass
class Page:
    """A single fetched documentation page."""
    url: str
    title: str
    text: str              # cleaned plain text
    http_status: int
    crawled_at: datetime


@dataclass
class Chunk:
    """A text segment derived from a Page."""
    page_url: str
    page_title: str
    chunk_index: int
    text: str
    char_count: int

    @property
    def point_id(self) -> str:
        """Deterministic UUID5 for Qdrant -- stable across re-runs."""
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.page_url}#{self.chunk_index}"))


@dataclass
class EmbeddedChunk:
    """A Chunk paired with its embedding vector."""
    chunk: Chunk
    vector: list[float]


# =============================================================================
# Configuration loader  [T007, T021]
# =============================================================================

def _parse_int_env(name: str, default: int) -> int:
    """Read an int env var; raise ValueError with a clear message if non-numeric."""
    raw = os.getenv(name, "").strip()
    if raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(
            f"Environment variable {name} must be an integer, got: {raw!r}"
        )


def load_config() -> Config:
    """
    Load all pipeline configuration from environment variables.

    Required: BASE_URL, COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY
    Optional: COLLECTION_NAME, COHERE_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
              EMBED_BATCH_SIZE, MIN_CHUNK_CHARS
    """
    load_dotenv()

    required = {
        "BASE_URL": os.getenv("BASE_URL", "").strip(),
        "COHERE_API_KEY": os.getenv("COHERE_API_KEY", "").strip(),
        "QDRANT_URL": os.getenv("QDRANT_URL", "").strip(),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY", "").strip(),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(
            f"Missing required environment variable(s): {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your credentials."
        )

    return Config(
        base_url=required["BASE_URL"].rstrip("/"),
        cohere_api_key=required["COHERE_API_KEY"],
        qdrant_url=required["QDRANT_URL"],
        qdrant_api_key=required["QDRANT_API_KEY"],
        collection_name=os.getenv("COLLECTION_NAME", "book-embeddings").strip(),
        cohere_model=os.getenv("COHERE_MODEL", "embed-english-v3.0").strip(),
        chunk_size=_parse_int_env("CHUNK_SIZE", 1000),
        chunk_overlap=_parse_int_env("CHUNK_OVERLAP", 200),
        embed_batch_size=_parse_int_env("EMBED_BATCH_SIZE", 96),
        min_chunk_chars=_parse_int_env("MIN_CHUNK_CHARS", 100),
    )


# =============================================================================
# Stage 1: URL Discovery  [T009, T010, T022]
# =============================================================================

def _canonical_url(url: str) -> str:
    """Normalise URL to prevent duplicates from trailing-slash variants."""
    return url.rstrip("/")


def fetch_sitemap(base_url: str) -> list[str]:
    """
    Fetch {base_url}/sitemap.xml and return all same-domain <loc> URLs.

    Returns [] on any failure (non-200, parse error, timeout).
    Caller falls back to crawl_links() when this returns [].
    """
    sitemap_url = f"{base_url}/sitemap.xml"
    try:
        resp = httpx.get(sitemap_url, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            log("CRAWL", f"Sitemap returned HTTP {resp.status_code} -- will use link crawl")
            return []

        root = ET.fromstring(resp.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        parsed_base = urlparse(base_url)

        urls: list[str] = []
        for loc in root.findall(".//sm:loc", ns):
            raw = (loc.text or "").strip()
            if not raw:
                continue
            parsed = urlparse(raw)
            if parsed.scheme == parsed_base.scheme and parsed.netloc == parsed_base.netloc:
                urls.append(_canonical_url(raw))

        return list(dict.fromkeys(urls))  # deduplicate, preserve order

    except Exception as exc:
        log("CRAWL", f"Sitemap error ({type(exc).__name__}) -- will use link crawl")
        return []


_SKIP_EXTENSIONS = frozenset({
    ".js", ".css", ".json", ".png", ".svg", ".ico",
    ".jpg", ".jpeg", ".gif", ".webp", ".woff", ".woff2",
    ".ttf", ".eot", ".pdf", ".zip",
})
_SKIP_PATHS = frozenset({"/static/", "/assets/", "/_next/", "/.docusaurus/"})


def _is_crawlable(url: str, base_netloc: str) -> bool:
    """Return True if this URL should be crawled (same domain, HTML content)."""
    parsed = urlparse(url)
    if parsed.netloc != base_netloc:
        return False
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in _SKIP_EXTENSIONS):
        return False
    if any(skip in path for skip in _SKIP_PATHS):
        return False
    return True


def crawl_links(base_url: str) -> list[str]:
    """
    Recursively discover page URLs by following <a href> links from base_url.

    Fallback for when sitemap.xml is unavailable. Same-domain only.
    Uses a visited set to prevent re-visiting any URL.
    """
    parsed_base = urlparse(base_url)
    visited: set[str] = set()
    queue: list[str] = [_canonical_url(base_url)]
    found: list[str] = []

    while queue:
        url = queue.pop(0)
        canon = _canonical_url(url)
        if canon in visited:
            continue
        visited.add(canon)

        try:
            resp = httpx.get(url, follow_redirects=True, timeout=15)
            if resp.status_code != 200:
                continue
        except Exception:
            continue

        found.append(canon)
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup.find_all("a", href=True):
            href = str(tag["href"]).strip()
            abs_url = urljoin(url, href).split("#")[0]  # strip fragments
            abs_canon = _canonical_url(abs_url)
            if abs_canon not in visited and _is_crawlable(abs_canon, parsed_base.netloc):
                queue.append(abs_canon)

    return list(dict.fromkeys(found))  # deduplicate, preserve order


# =============================================================================
# Stage 2: Fetch & Clean  [T011, T012, T023]
# =============================================================================

_NAV_CLASS_KEYWORDS = frozenset({
    "navbar", "sidebar", "pagination", "breadcrumb",
    "toc", "menu", "footer", "admonitionIcon",
})
_REMOVE_TAG_NAMES = [
    "nav", "footer", "header", "script", "style",
    "noscript", "aside", "button", "form", "svg",
]


def clean_html(html: str, url: str) -> tuple[str, str]:
    """
    Extract the page title and clean readable text from raw HTML.

    Strips navigation, footer, scripts, and other non-content elements.
    Returns (title, clean_text). Pure function -- no side effects.
    """
    soup = BeautifulSoup(html, "lxml")

    # Extract title before stripping tags
    title = ""
    title_tag = soup.find("title")
    h1_tag = soup.find("h1")
    if title_tag and title_tag.get_text(strip=True):
        title = title_tag.get_text(strip=True)
    elif h1_tag and h1_tag.get_text(strip=True):
        title = h1_tag.get_text(strip=True)
    else:
        title = url

    # Remove structural non-content tags
    for tag_name in _REMOVE_TAG_NAMES:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove elements with navigation-related CSS classes
    for tag in soup.find_all(True):
        cls_list = tag.get("class", [])
        cls_str = " ".join(cls_list) if isinstance(cls_list, list) else str(cls_list)
        if any(kw in cls_str for kw in _NAV_CLASS_KEYWORDS):
            tag.decompose()

    # Find the main content container
    content = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"class": lambda c: c and "markdown" in (
            " ".join(c) if isinstance(c, list) else str(c)
        )})
        or soup.find("body")
        or soup
    )

    raw_text = content.get_text(separator=" ", strip=True)
    clean_text = re.sub(r"\s{2,}", " ", raw_text).strip()
    return title, clean_text


def fetch_page(url: str) -> "Page | None":
    """
    Fetch a single URL and return a Page with cleaned text.

    Returns None on network error, non-2xx status, or empty content.
    """
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15)
    except httpx.TimeoutException:
        log("FETCH", f"Timeout -- skipping {url}")
        return None
    except httpx.ConnectError as exc:
        log("FETCH", f"ConnectError ({exc}) -- skipping {url}")
        return None
    except Exception as exc:
        log("FETCH", f"Error ({type(exc).__name__}: {exc}) -- skipping {url}")
        return None

    if not (200 <= resp.status_code < 300):
        log("FETCH", f"HTTP {resp.status_code} -- skipping {url}")
        return None

    title, text = clean_html(resp.text, url)
    if not text:
        log("FETCH", f"Empty content -- skipping {url}")
        return None

    return Page(
        url=url,
        title=title,
        text=text,
        http_status=resp.status_code,
        crawled_at=datetime.now(timezone.utc),
    )


# =============================================================================
# Stage 3: Chunking  [T013]
# =============================================================================

_SENTENCE_ENDS = frozenset(".!?\n")


def chunk_text(page: Page, chunk_size: int, overlap: int, min_chars: int) -> list[Chunk]:
    """
    Split page text into overlapping fixed-size character chunks.

    At each candidate split point, walks back up to 100 chars to find the
    nearest sentence boundary (.!? or newline). Falls back to hard cut.
    Chunks shorter than min_chars are discarded.
    """
    text = page.text
    if len(text) < min_chars:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Snap to sentence boundary if not at end of text
        if end < len(text):
            for i in range(end, max(end - 100, start), -1):
                if text[i] in _SENTENCE_ENDS:
                    end = i + 1
                    break

        chunk_content = text[start:end].strip()
        if len(chunk_content) >= min_chars:
            chunks.append(Chunk(
                page_url=page.url,
                page_title=page.title,
                chunk_index=index,
                text=chunk_content,
                char_count=len(chunk_content),
            ))
            index += 1

        if end >= len(text):
            break
        start = end - overlap

    return chunks


# =============================================================================
# Stage 4: Embedding  [T014]
# =============================================================================

def embed_chunks(
    chunks: list[Chunk],
    co: cohere.ClientV2,
    model: str,
    batch_size: int,
) -> list[EmbeddedChunk]:
    """
    Send chunks to Cohere in batches and return EmbeddedChunk list.

    Uses input_type="search_document" for indexing.
    Raises on API failure -- pipeline halts (re-run is safe via upsert).
    """
    if not chunks:
        return []

    num_batches = math.ceil(len(chunks) / batch_size)
    embedded: list[EmbeddedChunk] = []

    with tqdm(total=len(chunks), desc="Embedding", unit="chunk") as pbar:
        for i in range(num_batches):
            batch = chunks[i * batch_size : (i + 1) * batch_size]
            response = co.embed(
                texts=[c.text for c in batch],
                model=model,
                input_type="search_document",
                embedding_types=["float"],
            )
            vectors = response.embeddings.float_
            for chunk, vector in zip(batch, vectors):
                embedded.append(EmbeddedChunk(chunk=chunk, vector=vector))
            pbar.update(len(batch))

    return embedded


# =============================================================================
# Stage 5: Qdrant storage  [T015, T016]
# =============================================================================

def init_qdrant(cfg: Config) -> QdrantClient:
    """
    Create a Qdrant client and ensure the collection exists.

    Creates the collection with cosine distance and 1024 dimensions if absent.
    Does NOT delete existing data if the collection already exists.
    """
    client = QdrantClient(url=cfg.qdrant_url, api_key=cfg.qdrant_api_key)

    if not client.collection_exists(cfg.collection_name):
        client.create_collection(
            collection_name=cfg.collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
        log("STORE", f"Created collection '{cfg.collection_name}'")
    else:
        log("STORE", f"Collection '{cfg.collection_name}' exists -- upserting")

    return client


def store_embeddings(
    embedded_chunks: list[EmbeddedChunk],
    client: QdrantClient,
    collection_name: str,
) -> int:
    """
    Upsert all embedded chunks as Qdrant points.

    Uses deterministic UUID5 point IDs -- idempotent re-runs.
    Returns total count of points upserted.
    """
    if not embedded_chunks:
        return 0

    upsert_batch = 100
    total = 0
    num_batches = math.ceil(len(embedded_chunks) / upsert_batch)

    with tqdm(total=len(embedded_chunks), desc="Storing ", unit="pt") as pbar:
        for i in range(num_batches):
            batch = embedded_chunks[i * upsert_batch : (i + 1) * upsert_batch]
            points = [
                PointStruct(
                    id=ec.chunk.point_id,
                    vector=ec.vector,
                    payload={
                        "url": ec.chunk.page_url,
                        "title": ec.chunk.page_title,
                        "chunk_index": ec.chunk.chunk_index,
                        "text": ec.chunk.text,
                        "char_count": ec.chunk.char_count,
                    },
                )
                for ec in batch
            ]
            client.upsert(collection_name=collection_name, points=points)
            total += len(batch)
            pbar.update(len(batch))

    return total


# =============================================================================
# Stage 6: Retrieval verification  [T018, T019]
# =============================================================================

def test_retrieval(
    queries: list[str],
    client: QdrantClient,
    co: cohere.ClientV2,
    cfg: Config,
) -> None:
    """
    Embed each query and print the top-3 retrieval results to stdout.

    Uses input_type="search_query" for asymmetric search (query vs document).
    """
    print()
    for query in queries:
        response = co.embed(
            texts=[query],
            model=cfg.cohere_model,
            input_type="search_query",
            embedding_types=["float"],
        )
        query_vector = response.embeddings.float_[0]

        response_q = client.query_points(
            collection_name=cfg.collection_name,
            query=query_vector,
            limit=3,
            with_payload=True,
        )
        results = response_q.points

        log("VERIFY", f'Query: "{query}"')
        if not results:
            print("         (no results returned)")
        for rank, r in enumerate(results, start=1):
            snippet = r.payload.get("text", "")[:120].replace("\n", " ")
            print(f"         {rank}. (score={r.score:.3f}) {r.payload.get('url', '')}")
            print(f'            "{snippet}..."')
        print()


# =============================================================================
# Local Markdown fallback — reads book/docs/ when live site pages are unavailable
# =============================================================================

_MD_STRIP = re.compile(
    r"^---.*?---\s*",          # YAML front matter
    re.DOTALL | re.MULTILINE,
)
_MD_CODE  = re.compile(r"```.*?```", re.DOTALL)
_MD_INLINE = re.compile(r"`[^`]+`")
_MD_LINK   = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_MD_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_MD_HTML   = re.compile(r"<[^>]+>")


def _md_to_text(md: str) -> str:
    """Convert Markdown to plain text (best-effort, no external deps)."""
    text = _MD_STRIP.sub("", md)
    text = _MD_CODE.sub(" ", text)
    text = _MD_INLINE.sub(" ", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _MD_HEADING.sub("", text)
    text = _MD_HTML.sub(" ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def _md_title(md: str, fallback: str) -> str:
    """Extract title from YAML front matter or first heading."""
    fm = re.search(r"^---\s*\ntitle:\s*[\"']?(.+?)[\"']?\s*\n", md, re.MULTILINE)
    if fm:
        return fm.group(1).strip()
    h1 = re.search(r"^#\s+(.+)", md, re.MULTILINE)
    if h1:
        return h1.group(1).strip()
    return fallback


def load_local_docs(docs_dir: pathlib.Path, base_url: str) -> list[Page]:
    """
    Read all .md files under docs_dir and return Page objects.

    Used as fallback when the deployed site returns 404 for content pages.
    URLs are constructed as {base_url}/docs/{relative_path_without_extension}.
    """
    pages: list[Page] = []
    for md_file in sorted(docs_dir.rglob("*.md")):
        rel = md_file.relative_to(docs_dir)
        # Build URL: drop .md suffix, convert path separators to /
        url_path = str(rel.with_suffix("")).replace("\\", "/")
        # Skip index/category files that don't have standalone pages
        if url_path.endswith("index") or rel.name == "_category_.json":
            continue
        url = f"{base_url.rstrip('/')}/docs/{url_path}"
        try:
            raw = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        title = _md_title(raw, url_path)
        text = _md_to_text(raw)
        if not text:
            continue
        pages.append(Page(
            url=url,
            title=title,
            text=text,
            http_status=200,
            crawled_at=datetime.now(timezone.utc),
        ))
    return pages


# =============================================================================
# main() -- pipeline orchestrator  [T017]
# =============================================================================

def main() -> None:
    """Run the full book content embedding pipeline end-to-end."""

    # --- Config ---
    try:
        cfg = load_config()
    except ValueError as exc:
        print(f"[ERROR ]  Configuration error:\n{exc}", file=sys.stderr)
        sys.exit(1)

    log("CONFIG", f"Base URL:   {cfg.base_url}")
    log("CONFIG", f"Collection: {cfg.collection_name}")
    log("CONFIG", f"Model:      {cfg.cohere_model}")
    log("CONFIG", f"Chunks:     {cfg.chunk_size} chars / {cfg.chunk_overlap} overlap")

    # --- Stage 1: URL Discovery ---
    log("CRAWL", f"Fetching sitemap from {cfg.base_url}/sitemap.xml")
    urls = fetch_sitemap(cfg.base_url)

    if not urls:
        log("CRAWL", "Sitemap empty -- falling back to recursive link crawl")
        urls = crawl_links(cfg.base_url)

    if not urls:
        log("ERROR ", "No URLs discovered. Check BASE_URL and site accessibility.")
        sys.exit(1)

    log("CRAWL", f"Found {len(urls)} URL(s)")

    # --- Stage 2: Fetch & Clean ---
    log("FETCH", f"Fetching {len(urls)} page(s)...")
    pages: list[Page] = []
    for url in tqdm(urls, desc="Fetching", unit="page"):
        page = fetch_page(url)
        if page:
            pages.append(page)

    skipped = len(urls) - len(pages)
    log("FETCH", f"{len(pages)} fetched, {skipped} skipped")

    # If the live site returned fewer than 3 content pages, fall back to local markdown.
    # This handles Vercel deployment lag or routing issues with trailingSlash config.
    if len(pages) < 3:
        # Locate book/docs/ relative to this script (../book/docs from backend/)
        script_dir = pathlib.Path(__file__).parent
        docs_dir = (script_dir / ".." / "book" / "docs").resolve()
        if docs_dir.exists():
            log("FETCH", f"Fewer than 3 live pages — loading local docs from {docs_dir}")
            pages = load_local_docs(docs_dir, cfg.base_url)
            log("FETCH", f"{len(pages)} page(s) loaded from local markdown")
        else:
            log("ERROR ", f"Local docs not found at {docs_dir}. Exiting.")
            sys.exit(1)

    if not pages:
        log("ERROR ", "No pages available. Exiting.")
        sys.exit(1)

    # --- Stage 3: Chunking ---
    all_chunks: list[Chunk] = []
    for page in pages:
        all_chunks.extend(
            chunk_text(page, cfg.chunk_size, cfg.chunk_overlap, cfg.min_chunk_chars)
        )

    log("CHUNK", f"{len(all_chunks)} chunk(s) from {len(pages)} page(s)")

    if not all_chunks:
        log("ERROR ", "No chunks produced. Lower MIN_CHUNK_CHARS or check page content.")
        sys.exit(1)

    # --- Stage 4: Embedding ---
    co = cohere.ClientV2(api_key=cfg.cohere_api_key)
    log("EMBED", f"Embedding {len(all_chunks)} chunk(s) via {cfg.cohere_model}...")
    embedded_chunks = embed_chunks(all_chunks, co, cfg.cohere_model, cfg.embed_batch_size)
    log("EMBED", f"{len(embedded_chunks)} embedding(s) generated")

    # --- Stage 5: Storage ---
    client = init_qdrant(cfg)
    log("STORE", f"Upserting {len(embedded_chunks)} point(s)...")
    stored = store_embeddings(embedded_chunks, client, cfg.collection_name)
    log("STORE", f"{stored} point(s) upserted")

    # --- Stage 6: Retrieval Verification ---
    log("VERIFY", "Running test queries...")
    test_retrieval(
        queries=[
            "What is ROS 2 and how does it work?",
            "How does a digital twin model a physical system?",
            "What is a Vision-Language-Action model?",
        ],
        client=client,
        co=co,
        cfg=cfg,
    )

    # --- Summary ---
    print(f"[DONE ]   {len(pages)} pages | {len(all_chunks)} chunks | {stored} vectors stored")


if __name__ == "__main__":
    main()
