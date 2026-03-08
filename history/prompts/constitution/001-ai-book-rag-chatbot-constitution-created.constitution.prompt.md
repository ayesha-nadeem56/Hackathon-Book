---
id: "001"
title: AI Book RAG Chatbot Constitution Created
stage: constitution
date: 2026-03-07
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: hp
command: /sp.constitution
labels: ["constitution","rag","docusaurus","fastapi","qdrant","neon","openai"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - n/a
---

## Prompt

Project: AI-Driven Interactive Book with Integrated RAG Chatbot

Core principles:
- Accuracy of information and technical correctness
- Clarity and readability for a broad technical audience
- Reproducibility of AI and software workflows
- Modularity and maintainable architecture
- Transparency in AI-generated content

Key standards:
- All book content must be structured using Docusaurus documentation standards
- All AI-generated content must be reviewed and refined for clarity and correctness
- Code examples must be functional, documented, and reproducible
- The chatbot must only answer using retrieved book content (RAG grounding)
- Backend services must follow clean API design using FastAPI
- Vector embeddings must be stored and retrieved using Qdrant Cloud
- Structured data storage must use Neon Serverless Postgres
- Chatbot implementation must use OpenAI Agents / ChatKit SDK
- Frontend chatbot interface must be embedded within the Docusaurus book
- Git-based version control must be used for all project artifacts

Architecture standards:
- Frontend: Docusaurus static documentation site
- Backend: FastAPI service for RAG orchestration
- Vector database: Qdrant Cloud (Free Tier)
- Relational database: Neon Serverless Postgres
- AI orchestration: OpenAI Agents / ChatKit SDK
- Deployment: GitHub Pages for the book

Constraints:
- Book must be structured as a multi-chapter documentation site
- Chatbot must support answering questions about the entire book
- Chatbot must support answering questions based only on user-selected text
- System must operate within free-tier limits of Qdrant and Neon
- All code must be compatible with modern Python environments

Success criteria:
- Book successfully deployed on GitHub Pages
- All chapters accessible through the Docusaurus site
- RAG chatbot embedded and functioning inside the book
- Chatbot accurately answers questions based on book content
- Selected text question-answering functionality works correctly
- End-to-end system architecture operates without runtime errors

## Response snapshot

Created `.specify/memory/constitution.md` at version 1.0.0 with:
- 5 core principles (Accuracy, Clarity, Reproducibility, Modularity, Transparency)
- Architecture Standards section with mandatory technology stack table
- Constraints & Success Criteria section (6 SC entries)
- Governance section with amendment procedure and versioning policy
- Sync Impact Report embedded as HTML comment

All template placeholders replaced; no unresolved tokens remaining.

## Outcome

- ✅ Impact: Project constitution established at v1.0.0; governs all future feature specs, plans, and tasks
- 🧪 Tests: n/a — constitution artifact; no automated tests applicable
- 📁 Files: .specify/memory/constitution.md (created/overwritten)
- 🔁 Next prompts: /sp.specify <feature-name> to create first feature spec; /sp.adr if stack decisions need formal ADR
- 🧠 Reflection: Constitution cleanly maps 5 user-provided principles to declarative MUST-based rules with rationale; technology stack locked via Architecture Standards table

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS — no bracket tokens remaining, dates ISO, principles declarative
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Add ADR for technology stack selection if user requests formal record
