# Quickstart: Module 2 — The Digital Twin (Gazebo & Unity)

**Branch**: `002-module2-digital-twin` | **Date**: 2026-03-09

This guide documents how to set up the Docusaurus book locally, work with Module 2 content,
run the development server, validate content, and build for production.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | 18 LTS | https://nodejs.org (or `nvm install 18`) |
| npm | 9+ (bundled with Node 18) | Bundled with Node.js |
| Git | Any recent | https://git-scm.com |
| Python | 3.10+ | For code example validation only |

---

## 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/ayesha-nadeem56/Hackathon-Book.git
cd Hackathon-Book

# Switch to the module 2 feature branch
git checkout 002-module2-digital-twin

# Install Docusaurus dependencies
cd book
npm install
```

---

## 2. Run the Development Server

```bash
# From the book/ directory
npm start
```

Opens `http://localhost:3000` in your browser with hot-reload enabled.
Module 2 appears in the sidebar under **"Module 2: The Digital Twin"** at position 2.

---

## 3. Build for Production

```bash
# From the book/ directory
npm run build
```

Output is in `book/build/`. The build MUST complete with zero errors and zero broken links.
Broken links cause the build to fail — this is the primary quality gate for Module 2.

---

## 4. Module 2 File Locations

```text
book/docs/module-2-digital-twin/
├── _category_.json            # Sidebar label "Module 2: The Digital Twin", position 2
├── index.md                   # Module landing page (sidebar_position: 0)
├── chapter-1-gazebo.md        # Gazebo physics simulation (sidebar_position: 1)
├── chapter-2-unity.md         # Unity environments + ROS-TCP-Connector (sidebar_position: 2)
└── chapter-3-sensors.md       # LiDAR, RGBD camera, IMU simulation (sidebar_position: 3)
```

Spec files (not deployed):
```text
specs/002-module2-digital-twin/
├── spec.md          # Feature specification
├── plan.md          # Implementation plan
├── research.md      # Technical research decisions
├── data-model.md    # Content structure schema (this module)
├── quickstart.md    # This file
├── tasks.md         # Implementation task list
├── checklists/
│   └── requirements.md   # Spec quality checklist
└── contracts/
    └── chapter-content-contract.md   # Chapter structure contract
```

---

## 5. Add or Edit a Chapter

1. Open `book/docs/module-2-digital-twin/chapter-<N>-<slug>.md`
2. Ensure frontmatter is present: `id`, `sidebar_position`
3. Follow the body structure from `contracts/chapter-content-contract.md`:
   - Start with `## Learning Objectives` (4 items)
   - Include a `:::info Prerequisites` admonition
   - Include at least 1 Mermaid diagram per chapter
   - End with `## Summary` table (minimum 6 rows)
4. Run `npm start` to preview changes live
5. Run `npm run build` to validate before committing

---

## 6. Content Validation

### Check for bare XML angle brackets (MDX v3 rule)

In prose and table cells, XML tag names MUST use backticks, not bare angle brackets:

```bash
# Search for potential bare angle brackets in module 2 content
# (Review results manually -- some angle brackets in code blocks are OK)
grep -n "<[a-zA-Z]" book/docs/module-2-digital-twin/*.md
```

### Check for non-ASCII characters (Windows cp1252 safety)

```bash
# Find non-ASCII characters in module 2 files
grep -Pn "[^\x00-\x7F]" book/docs/module-2-digital-twin/*.md
```

No output means all files are ASCII-only (correct).

### Validate Mermaid diagrams

Mermaid diagrams are validated at build time. Any syntax error causes `npm run build` to fail.
Run the build to validate all diagrams:

```bash
cd book && npm run build
```

### Check broken links

```bash
cd book && npm run build
# Build fails on broken links -- zero broken links required
```

---

## 7. Deployment to GitHub Pages

Deployment is automated via GitHub Actions on every merge to `main`.

**Manual deploy** (alternative):

```bash
# From the book/ directory
GIT_USER=<your-github-username> npm run deploy
```

This pushes `book/build/` to the `gh-pages` branch automatically.

---

## 8. File Naming Conventions

| Item | Pattern | Example |
|---|---|---|
| Module directory | `module-<N>-<slug>/` | `module-2-digital-twin/` |
| Chapter file | `chapter-<N>-<slug>.md` | `chapter-1-gazebo.md` |
| Chapter id (frontmatter) | `chapter-<N>-<slug>` | `chapter-1-gazebo` |
| Sidebar position | Integer 1-based | `sidebar_position: 1` |

---

## 9. Common Issues

| Issue | Cause | Fix |
|---|---|---|
| Build fails with "Unterminated JSX" | Bare `<tag>` in prose or table cell | Wrap tag name in backticks: `` `tag` `` |
| Build fails with "Invalid character" | Non-ASCII character in fenced code block | Replace with ASCII equivalent |
| Broken link error | `.md` extension missing in relative link | Use `./chapter-1-gazebo.md` not `./chapter-1-gazebo` |
| Mermaid diagram not rendering | Spaces in node IDs | Use camelCase or underscores in Mermaid node IDs |
| Chapter not appearing in sidebar | `sidebar_position` duplicate | Ensure each file has a unique `sidebar_position` |
