---
id: 027
title: Embedding Pipeline Architecture Plan
stage: plan
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: 007-embedding-pipeline
branch: 007-embedding-pipeline
user: hp
command: /sp.plan
labels: ["plan","embedding","qdrant","cohere","python","uv","pipeline","crawl"]
links:
  spec: specs/007-embedding-pipeline/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-embedding-pipeline/plan.md
  - specs/007-embedding-pipeline/research.md
  - specs/007-embedding-pipeline/data-model.md
  - specs/007-embedding-pipeline/quickstart.md
  - specs/007-embedding-pipeline/contracts/ingestion-pipeline.md
tests:
  - n/a (plan stage — tests defined in tasks)
---

## Prompt

Spec-1: URL Ingestion & Embedding Pipeline
Create 'backend/ folder, initialize project with 'uv', and add a single 'main.py'
IK main.py', implement URL fetching, text cleaning, and chunking
Generate embeddings using Cohere models
Store embeddings and metadata in Qdrant Cloud
Add a 'main() function to run the full ingestion pipeline end-to-end

## Response snapshot

Produced full planning artifacts for `007-embedding-pipeline`:

**plan.md**: Complete implementation plan — Python 3.11+, single `backend/main.py`, `uv`-managed project. Pipeline stages: crawl (sitemap-first) → clean (BeautifulSoup) → chunk (1000 chars, 200 overlap) → embed (Cohere `embed-english-v3.0`, 1024 dims, batches of 96) → store (Qdrant upsert, UUID5 IDs) → verify (test queries). All 5 constitution principles pass.

**research.md**: Resolved all unknowns — Docusaurus sitemap.xml confirmed at deployed URL (`https://hackathon-book-uogx.vercel.app/sitemap.xml`), Cohere v3 batch limits, Qdrant free-tier headroom (~4 MB vs 1 GB limit), `uv init --no-workspace` command, chunking algorithm with sentence-boundary snapping.

**data-model.md**: Python dataclasses — `Config`, `Page`, `Chunk`, `EmbeddedChunk`. Qdrant point schema with UUID5 IDs. Validation rules per field.

**contracts/ingestion-pipeline.md**: Full function contract for every public function in `main.py` — inputs, outputs, error behaviour, idempotency guarantees, side effects.

**quickstart.md**: Step-by-step setup guide — uv init, dep install, .env config, run command, expected output, re-run safety, troubleshooting table.

Agent context (CLAUDE.md) updated with new tech stack entries.

## Outcome

- ✅ Impact: All Phase 0 and Phase 1 planning artifacts complete; pipeline architecture fully specified; ready for /sp.tasks
- 🧪 Tests: Defined in contracts — cleaner, chunker, config validation unit tests; integration test for full pipeline
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/ingestion-pipeline.md
- 🔁 Next prompts: /sp.tasks to generate task breakdown; /sp.implement to build backend/main.py
- 🧠 Reflection: User provided explicit scope (single main.py, uv, Cohere, Qdrant) — plan required no clarifications. Deployed URL discovered from docusaurus.config.js in repo.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Constitution Check — all 5 principles PASS
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
