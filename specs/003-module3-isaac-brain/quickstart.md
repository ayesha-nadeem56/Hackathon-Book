# Quickstart: Module 3 — The AI-Robot Brain (NVIDIA Isaac)

**Branch**: `003-module3-isaac-brain` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This guide covers the development workflow for authoring and validating Module 3 content locally.

---

## Prerequisites

- Node.js 18+ installed
- Repository cloned to local machine
- Module 1 and Module 2 book content present in `book/docs/`

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

The site opens at `http://localhost:3000`. Module 3 will appear in the sidebar under **Module 3: The AI-Robot Brain** (position 3, after Module 2).

---

## 3. File Locations

| File | Purpose |
|---|---|
| `book/docs/module-3-isaac-brain/_category_.json` | Sidebar label, position 3, collapsible |
| `book/docs/module-3-isaac-brain/index.md` | Module landing page |
| `book/docs/module-3-isaac-brain/chapter-1-isaac-sim.md` | NVIDIA Isaac Sim + Replicator |
| `book/docs/module-3-isaac-brain/chapter-2-isaac-ros.md` | Isaac ROS GEMs + cuVSLAM + NITROS |
| `book/docs/module-3-isaac-brain/chapter-3-nav2.md` | Nav2 costmaps + planners + recovery |

---

## 4. Content Validation

### 4a. Check for bare XML angle brackets (MDX v3 parser error)

Run from repo root:

```bash
grep -rn "<[A-Za-z]" book/docs/module-3-isaac-brain/ --include="*.md"
```

Any match is a violation. Replace with HTML entities (`&lt;`, `&gt;`) or backtick-escape the content.

### 4b. Check for non-ASCII characters in fenced code blocks

```bash
grep -Pn "[^\x00-\x7F]" book/docs/module-3-isaac-brain/ --include="*.md"
```

Any match inside a fenced block (` ``` `) is a violation. Replace with ASCII equivalents.

### 4c. Verify sidebar positions are unique

```bash
grep -n "sidebar_position" book/docs/module-3-isaac-brain/*.md
```

Expected: `index.md` = 0, `chapter-1` = 1, `chapter-2` = 2, `chapter-3` = 3. No duplicates.

### 4d. Check Mermaid node count

Each Mermaid diagram must have 8 or fewer nodes. Count manually or search:

```bash
grep -c "-->" book/docs/module-3-isaac-brain/chapter-1-isaac-sim.md
```

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
| MDX parse error: Unexpected token `<` | Bare angle bracket in prose or table | Replace with `&lt;` / `&gt;` or backtick-escape |
| Mermaid diagram not rendering | Special characters in node IDs | Use camelCase or underscore node IDs only |
| Sidebar position conflict | Duplicate `sidebar_position` values | Assign unique integers 0-3 within the module |
| Broken link warning | `.md` extension missing in relative link | Add `.md` extension to all intra-module links |
| Build error: unknown admonition | Typo in `:::info` / `:::note` syntax | Verify admonition type spelling |

---

## 7. Deployment

GitHub Pages deployment is automatic on merge to `main`. No manual deploy step required.

```
Push to main --> GitHub Actions --> npm run build --> Deploy to Pages
```
