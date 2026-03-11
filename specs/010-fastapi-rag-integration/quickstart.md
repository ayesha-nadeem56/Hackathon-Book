# Quickstart: FastAPI RAG Integration (Local Development)

**Feature**: 010-fastapi-rag-integration
**Date**: 2026-03-11

---

## Prerequisites

- Python 3.11+ with `uv` installed (`pip install uv`)
- Node.js 18+ with npm (for Docusaurus frontend)
- A populated Qdrant collection (run `cd backend && uv run python main.py` first)
- `backend/.env` filled with all required credentials:

```env
GROQ_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
COLLECTION_NAME=book-embeddings
COHERE_API_KEY=...
```

---

## Step 1: Add FastAPI to Backend Dependencies

```bash
cd backend
uv add fastapi "uvicorn[standard]"
```

---

## Step 2: Start the FastAPI Server

```bash
cd backend
uv run uvicorn api:app --reload --port 8000
```

Expected output:
```
[QDRANT]  Connected — 'book-embeddings' has 342 vector(s)  top_k=3  threshold=None
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## Step 3: Test the Query Endpoint

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS 2?"}'
```

Expected response:
```json
{
  "answer": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software...",
  "sources": [
    {
      "url": "https://hackathon-book-uogx.vercel.app/docs/module-1-ros2/introduction",
      "title": "Module 1 — ROS 2 Fundamentals"
    }
  ]
}
```

---

## Step 4: Test the Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "dependencies": {
    "qdrant": "ok",
    "agent": "ok"
  }
}
```

---

## Step 5: Start the Docusaurus Frontend

In a separate terminal:

```bash
cd book
npm install
npm run start
```

The Docusaurus dev server starts at `http://localhost:3000`. The floating chatbot widget appears in the bottom-right corner on every page.

---

## Step 6: Verify End-to-End Integration

1. Open `http://localhost:3000` in a browser
2. Navigate to any chapter (e.g., `/docs/module-1-ros2/`)
3. Click the chat button (bottom-right)
4. Type a question about the book content
5. Confirm the chat panel displays an answer with source links

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ERROR: Required environment variable...` | Missing `.env` key | Check `backend/.env` |
| `ERROR: Collection 'book-embeddings' not found` | Vector store not populated | `cd backend && uv run python main.py` |
| CORS error in browser console | Backend not running or wrong port | Start backend on port 8000 |
| Chatbot widget not visible | Missing `Root.js` or build cache | `cd book && npm run clear && npm run start` |
| `Agent response timed out` | Groq rate limit or slow response | Retry; check `GROQ_API_KEY` validity |

---

## File Layout After Implementation

```text
backend/
├── api.py          ← NEW: FastAPI server (POST /query, GET /health)
├── main.py         ← existing embedding pipeline (unchanged)
├── retrieve.py     ← existing retrieval helpers (unchanged)
└── pyproject.toml  ← add fastapi, uvicorn[standard]

agent.py            ← existing CLI agent (add run_once() export)

book/
└── src/
    ├── theme/
    │   └── Root.js         ← NEW: Docusaurus Root swizzle (global wrapper)
    └── components/
        └── ChatWidget/
            ├── index.js    ← NEW: Chat widget React component
            └── styles.module.css  ← NEW: Floating panel styles
```
