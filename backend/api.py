"""
Book RAG API
============
FastAPI server that exposes the RAG book Q&A agent over HTTP.

Endpoints:
    POST /query   — ask a natural-language question; returns grounded answer + sources
    GET  /health  — dependency health check (Qdrant + agent)

Usage:
    cd backend
    uv run uvicorn api:app --reload --port 8000

Environment (loaded from backend/.env via agent.py load_config):
    Required: GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, COHERE_API_KEY
    Optional: COHERE_MODEL, AGENT_MODEL, TOP_K, SCORE_THRESHOLD
"""

# =============================================================================
# UTF-8 stdout fix (Windows cp1252 compatibility)
# =============================================================================
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# =============================================================================
# sys.path — allow importing agent.py from project root
# =============================================================================
import asyncio
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

# =============================================================================
# Standard library + third-party
# =============================================================================
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# =============================================================================
# Import agent helpers from project root agent.py
# =============================================================================
from agent import build_agent, init_qdrant, load_config, run_once


# =============================================================================
# Pydantic models (T005)
# =============================================================================

class QueryRequest(BaseModel):
    query: str


class SourceReference(BaseModel):
    url: str
    title: str = ""


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceReference]


class ErrorResponse(BaseModel):
    error: str


class HealthStatus(BaseModel):
    status: str
    dependencies: dict[str, str]


# =============================================================================
# Lifespan — startup / shutdown (T003)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the RAG agent once at startup; clean up on shutdown."""
    cfg = load_config()
    qdrant_client = init_qdrant(cfg)
    agent, run_config = build_agent(cfg, qdrant_client)

    app.state.cfg = cfg
    app.state.qdrant_client = qdrant_client
    app.state.agent = agent
    app.state.run_config = run_config

    print("[API] BookAgent ready. POST /query to ask questions.")
    yield

    qdrant_client.close()


# =============================================================================
# FastAPI app + CORS (T004)
# =============================================================================

app = FastAPI(
    title="Book RAG API",
    version="1.0.0",
    description="Exposes the RAG book Q&A agent over HTTP for the Docusaurus frontend.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hackathon-book-uogx.vercel.app",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# =============================================================================
# Source extraction helper (T007)
# =============================================================================

_URL_RE = re.compile(r"^URL:\s*(.+)$", re.MULTILINE)
_TITLE_RE = re.compile(r"^Title:\s*(.+)$", re.MULTILINE)


def parse_sources(result) -> list[SourceReference]:
    """
    Extract SourceReference objects from the agent's conversation history.

    The OpenAI Agents SDK represents tool outputs as dicts with:
        {"type": "function_call_output", "output": "<formatted text>", ...}

    Parses 'Title: <value>' and 'URL: <value>' lines from format_passages() output.
    Returns a deduplicated list of SourceReference objects.
    """
    seen_urls: set[str] = set()
    sources: list[SourceReference] = []

    for msg in result.to_input_list():
        if not isinstance(msg, dict):
            continue
        if msg.get("type") != "function_call_output":
            continue
        text = msg.get("output", "") or ""
        if not isinstance(text, str):
            text = str(text)

        titles = _TITLE_RE.findall(text)
        urls = _URL_RE.findall(text)

        for i, url in enumerate(urls):
            url = url.strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            title = titles[i].strip() if i < len(titles) else ""
            sources.append(SourceReference(url=url, title=title))

    return sources


# =============================================================================
# POST /query — US1 (T008 + T009)
# =============================================================================

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, request: Request):
    """
    Ask a natural-language question about the book.

    The agent retrieves relevant passages from Qdrant and returns a grounded
    answer. All responses cite only content from the indexed book corpus.
    """
    # Validate input (FR-005)
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="query must be a non-empty string")
    if len(q) > 2000:
        raise HTTPException(
            status_code=400,
            detail="query exceeds maximum length of 2000 characters",
        )

    agent = request.app.state.agent
    run_config = request.app.state.run_config

    try:
        result = await asyncio.wait_for(
            run_once(agent, run_config, q),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Agent response timed out. Please try again.")
    except Exception as exc:
        print(f"[API] Query failed: {exc}", file=sys.stderr)
        raise HTTPException(status_code=503, detail="Retrieval service unavailable. Please try again shortly.")

    answer = result.final_output or ""
    sources = parse_sources(result)
    return QueryResponse(answer=answer, sources=sources)


# =============================================================================
# GET /health — US3 (T014)
# =============================================================================

@app.get("/health")
async def health(request: Request) -> JSONResponse:
    """
    Service health check.

    Verifies connectivity to Qdrant and confirms the agent is initialized.
    Returns HTTP 200 when all dependencies are healthy, HTTP 503 when degraded.
    """
    # Check Qdrant
    try:
        await asyncio.wait_for(
            asyncio.to_thread(request.app.state.qdrant_client.get_collections),
            timeout=5.0,
        )
        qdrant_status = "ok"
    except Exception:
        qdrant_status = "unreachable"

    # Check agent
    agent_status = (
        "ok" if request.app.state.agent is not None else "not_initialized"
    )

    overall = "ok" if qdrant_status == "ok" and agent_status == "ok" else "degraded"
    status = HealthStatus(
        status=overall,
        dependencies={"qdrant": qdrant_status, "agent": agent_status},
    )

    return JSONResponse(
        content=status.model_dump(),
        status_code=200 if overall == "ok" else 503,
    )
