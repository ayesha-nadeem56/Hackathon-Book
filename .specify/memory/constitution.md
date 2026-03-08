<!--
Sync Impact Report
==================
Version change: (new) → 1.0.0
Modified principles: N/A — initial constitution creation
Added sections:
  - Core Principles (5 principles)
  - Architecture Standards
  - Constraints & Success Criteria
  - Governance
Removed sections: All template placeholders replaced
Templates reviewed:
  - .specify/templates/plan-template.md ✅ compatible (Constitution Check section is dynamic)
  - .specify/templates/spec-template.md ✅ compatible
  - .specify/templates/tasks-template.md ✅ compatible
Deferred TODOs: None
-->

# AI-Driven Interactive Book with Integrated RAG Chatbot — Constitution

## Core Principles

### I. Accuracy & Technical Correctness

All book content, code examples, and chatbot responses MUST be factually correct
and technically verified. AI-generated content MUST be reviewed and refined before
publication. Code examples MUST be functional and reproducible in modern Python
environments.

**Rationale**: Inaccurate technical content erodes user trust and renders the book
unreliable as a learning resource.

### II. Clarity & Readability

All content MUST be written for a broad technical audience. Language MUST be clear,
concise, and free of unnecessary jargon. Documentation MUST follow Docusaurus
standards for consistent structure and navigation.

**Rationale**: A broad audience requires inclusive writing that does not assume
deep specialist knowledge beyond what is introduced in the book itself.

### III. Reproducibility of Workflows

All AI and software workflows described in the book MUST be reproducible by readers.
Code, configurations, and environment setup instructions MUST be version-pinned
and tested. All code examples MUST include inline documentation explaining their purpose.

**Rationale**: Reproducibility is the foundation of credible technical education;
readers must be able to follow and validate every workflow independently.

### IV. Modularity & Maintainable Architecture

The system MUST be built from loosely coupled, independently deployable components:
Docusaurus frontend, FastAPI backend, Qdrant vector store, and Neon Postgres. Each
component MUST be replaceable without requiring rewrites of other components. The
smallest viable change MUST be preferred for all modifications.

**Rationale**: A modular architecture reduces blast radius during changes, enables
independent scaling, and simplifies long-term maintenance.

### V. Transparency in AI-Generated Content

All AI-generated content MUST be explicitly identified. The RAG chatbot MUST only
answer using retrieved book content and MUST NOT hallucinate or fabricate information
outside the grounded corpus. Chatbot responses MUST cite the source section when
possible.

**Rationale**: Transparency in AI usage builds reader trust and prevents misinformation,
which is especially critical in an educational context.

## Architecture Standards

The following technology stack is MANDATORY and MUST NOT be substituted without an
approved Architecture Decision Record (ADR):

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Frontend           | Docusaurus static documentation site |
| Deployment         | GitHub Pages                        |
| Backend            | FastAPI service for RAG orchestration |
| Vector Database    | Qdrant Cloud (Free Tier)            |
| Relational Database | Neon Serverless Postgres            |
| AI Orchestration   | OpenAI Agents / ChatKit SDK         |

**API Design**: Backend services MUST follow clean REST API design principles using
FastAPI. All endpoints MUST be versioned, documented, and include explicit error responses.

**Embeddings**: Vector embeddings MUST be stored and retrieved exclusively via Qdrant
Cloud. Embedding models MUST be documented and version-pinned.

**Chatbot Interface**: The RAG chatbot frontend MUST be embedded directly within the
Docusaurus book site. The interface MUST support two modes:
1. Full-book question answering (entire corpus)
2. Selected-text question answering (user-highlighted passage)

**Version Control**: Git-based version control MUST be used for all project artifacts,
including book content, configuration, and infrastructure code.

## Constraints & Success Criteria

### Operational Constraints

- The system MUST operate within the free-tier limits of Qdrant Cloud and Neon Postgres.
- All code MUST be compatible with modern Python environments (Python 3.11+).
- No secrets or API tokens MUST be hardcoded; all credentials MUST use `.env` files
  and MUST be documented in `.env.example`.
- The book MUST be structured as a multi-chapter documentation site.
- The chatbot MUST support answering questions about the entire book corpus.
- The chatbot MUST support answering questions based only on user-selected text.

### Success Criteria

| ID     | Criterion                                                                 |
|--------|---------------------------------------------------------------------------|
| SC-001 | Book successfully deployed and publicly accessible on GitHub Pages        |
| SC-002 | All chapters accessible and navigable through the Docusaurus site         |
| SC-003 | RAG chatbot embedded and functional within the deployed book              |
| SC-004 | Chatbot accurately answers questions grounded in book content             |
| SC-005 | Selected-text question-answering functionality works end-to-end           |
| SC-006 | End-to-end system operates without runtime errors in production           |

## Governance

This constitution supersedes all other project practices and guidelines. All
architectural decisions MUST reference and comply with the principles defined here.

**Amendment Procedure**:
1. Propose amendment with rationale and impact analysis.
2. Record the decision in an Architecture Decision Record (ADR) under `history/adr/`.
3. Update this constitution file and increment the version per semantic versioning.
4. Update all dependent templates and documents listed in the Sync Impact Report.

**Versioning Policy**:
- MAJOR: Backward-incompatible governance changes, principle removals, or redefinitions.
- MINOR: New principles or sections added, or materially expanded guidance.
- PATCH: Clarifications, wording fixes, or non-semantic refinements.

**Compliance Review**:
All PRs and design reviews MUST verify compliance with the five core principles.
Complexity MUST be justified against the Modularity & Maintainable Architecture principle.
Refer to `.specify/memory/constitution.md` as the authoritative governance document
during all development workflows.

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
