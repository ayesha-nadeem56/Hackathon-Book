# Quickstart: Module 4 — Vision-Language-Action (VLA)

**Branch**: `004-module4-vla` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This guide covers the development workflow for authoring and validating Module 4 content locally.

---

## Prerequisites

- Node.js 18+ installed
- Repository cloned to local machine
- Modules 1, 2, and 3 book content present in `book/docs/`

---

## 1. Clone and Install

```bash
# Clone the repository (if not already done)
git clone https://github.com/<your-org>/Hackathon-Book.git
cd Hackathon-Book

# Install Docusaurus dependencies
cd book
npm install
```

---

## 2. Start Development Server

```bash
# From the book/ directory
npm run start
```

The site opens at `http://localhost:3000`. Module 4 will appear in the sidebar under **Module 4: Vision-Language-Action** (position 4, after Module 3).

---

## 3. File Locations

| File | Purpose |
|---|---|
| `book/docs/module-4-vla/_category_.json` | Sidebar label, position 4, collapsible |
| `book/docs/module-4-vla/index.md` | Module landing page |
| `book/docs/module-4-vla/chapter-1-whisper.md` | Whisper ASR + Python transcription + ROS 2 |
| `book/docs/module-4-vla/chapter-2-llm-planner.md` | LLM planning + system prompt + guardrail |
| `book/docs/module-4-vla/chapter-3-capstone.md` | End-to-end VLA capstone |

---

## 4. Content Validation

### 4a. Check for bare XML angle brackets (MDX v3 parser error)

Run from repo root:

```bash
grep -rn "<[A-Za-z]" book/docs/module-4-vla/ --include="*.md"
```

Any match is a violation. Replace with HTML entities (`&lt;`, `&gt;`) or backtick-escape the content.

### 4b. Check for non-ASCII characters in fenced code blocks

```bash
grep -Pn "[^\x00-\x7F]" book/docs/module-4-vla/ --include="*.md"
```

Any match inside a fenced block is a violation. Replace with ASCII equivalents (e.g., `--` instead of em-dash).

### 4c. Verify sidebar positions are unique

```bash
grep -n "sidebar_position" book/docs/module-4-vla/*.md
```

Expected: `index.md` = 0, `chapter-1` = 1, `chapter-2` = 2, `chapter-3` = 3. No duplicates.

### 4d. Check system prompt code fence tag

```bash
grep -n "^```" book/docs/module-4-vla/chapter-2-llm-planner.md
```

The system prompt block MUST use ` ```text ` not ` ```json ` to prevent MDX curly-brace interpretation.

---

## 5. Build Validation

```bash
# From book/ directory
npm run build
```

A successful build prints:

```
[SUCCESS] Generated static files in build/
```

Zero errors and zero broken links required before merge.

---

## 6. Common Issues

| Issue | Cause | Fix |
|---|---|---|
| MDX parse error: Unexpected token `{` | Python f-string or JSON curly brace in prose | Move curly braces into fenced code block; use backtick for inline variable names |
| MDX parse error: Unexpected token `<` | Bare angle bracket in prose or table | Replace with `&lt;` / `&gt;` or backtick-escape |
| Mermaid diagram not rendering | Special characters in node IDs | Use camelCase or underscore node IDs only |
| Sidebar position conflict | Duplicate `sidebar_position` values | Assign unique integers 0-3 within the module |
| Broken link warning | `.md` extension missing or wrong module path | Verify actual directory name; add `.md` to all relative links |
| System prompt renders as broken JSON | Wrong fence tag (`json` instead of `text`) | Change ` ```json ` to ` ```text ` for system prompt block |

---

## 7. Deployment

GitHub Pages deployment is automatic on merge to `main`. No manual deploy step required.

```
Push to main --> GitHub Actions --> npm run build --> Deploy to Pages
```
