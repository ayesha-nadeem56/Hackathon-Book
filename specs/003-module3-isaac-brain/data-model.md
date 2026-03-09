# Data Model: Module 3 — The AI-Robot Brain (NVIDIA Isaac)

**Branch**: `003-module3-isaac-brain` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This document describes the content structure model for Module 3 of the Docusaurus book.
There is no relational or vector database in this phase — the "data model" is the schema of static content files.

---

## Entity 1: Module (Directory)

**Location**: `book/docs/module-3-isaac-brain/`

**`_category_.json` schema**:
```json
{
  "label": "Module 3: The AI-Robot Brain",
  "position": 3,
  "collapsible": true,
  "collapsed": false,
  "description": "NVIDIA Isaac Sim, Isaac ROS perception, and Nav2 navigation for humanoid robots"
}
```

**`index.md` frontmatter**:
```yaml
---
id: module-3-overview
sidebar_position: 0
---
```

**Validation rules**:
- `position` MUST be 3 (unique; follows Module 2 at position 2).
- `index.md` MUST link to `./chapter-1-isaac-sim.md`.
- `index.md` MUST include a Prerequisites admonition referencing Modules 1 and 2.

---

## Entity 2: Chapter (MDX File)

**Location**: `book/docs/module-3-isaac-brain/chapter-<N>-<slug>.md`

**Frontmatter schema**:
```yaml
---
id: chapter-<N>-<slug>
sidebar_position: <N>
---
```

**Body structure** (ordered, all MUST be present):

| Order | Section | Required Content |
|---|---|---|
| 1 | `## Learning Objectives` | Exactly 4 bullet points |
| 2 | `:::info Prerequisites` | Links to prior chapters or modules |
| 3-N | Content sections | Prose + Mermaid diagrams + config/code blocks |
| Last | `## Summary` | Term / Definition table (minimum 7 rows) |

**Validation rules**:
- `sidebar_position` unique within `module-3-isaac-brain/`.
- Body MUST begin with exactly 4 Learning Objectives.
- Body MUST end with Summary table (min 7 rows).
- ASCII-only in all fenced code blocks.
- No bare XML angle brackets in prose or table cells.
- At least one Mermaid diagram per chapter; maximum 8 nodes per diagram.

---

## Entity 3: YAML Configuration Block

YAML is the primary configuration format for Isaac Sim Replicator configs and Nav2 costmap parameters.

**Format**:
```yaml
# Nav2 global costmap -- key parameters explained
global_costmap:
  global_frame: map          # coordinate frame of the costmap
  resolution: 0.05           # meters per cell (5 cm resolution)
  inflation_radius: 0.55     # buffer zone around obstacles in meters
```

**Validation rules**:
- YAML blocks MUST use the `yaml` language tag.
- First line MUST be a comment identifying the config context.
- All content ASCII-only; inline comments on key fields required.

---

## Entity 4: Bash Command Block

Bash blocks show ROS 2 launch commands for Isaac ROS packages.

**Format**:
```bash
# Launch cuVSLAM -- visual SLAM on GPU
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py
```

**Validation rules**:
- Bash blocks MUST use the `bash` language tag.
- All content ASCII-only (no Unicode dashes in flags).
- Include a comment above the command explaining what it launches.

---

## Entity 5: Diagram (Mermaid Block)

**Supported types for Module 3**:

| Type | Use Case |
|---|---|
| `graph LR` | Pipelines (Replicator, Isaac ROS perception, Nav2 architecture) |
| `graph TD` | Processing hierarchies |
| `sequenceDiagram` | Nav2 navigation request/response sequences |

**Validation rules**:
- Maximum 8 nodes per diagram.
- Node IDs: camelCase or underscores (no spaces, no special characters).
- Must accurately represent the concept described in surrounding prose.
- Validated at `npm run build` time.

---

## Module 3 Content Map

| File | `sidebar_position` | Title | Key Content Elements |
|---|---|---|---|
| `_category_.json` | — | — | position 3, label, collapsible |
| `index.md` | 0 | Module 3 Overview | Narrative, prerequisites, chapter table, 5 outcomes, CTA |
| `chapter-1-isaac-sim.md` | 1 | NVIDIA Isaac Sim | 4 pillars, 6-row comparison table, synthetic data rationale, Replicator YAML block, label types table, 2 Mermaid diagrams, Summary (7 rows) |
| `chapter-2-isaac-ros.md` | 2 | Isaac ROS Perception | fps comparison, NITROS explanation, 4-row GEM table, cuVSLAM 5-step prose, bash launch block, 2 Mermaid diagrams, Summary (7 rows) |
| `chapter-3-nav2.md` | 3 | Navigation with Nav2 | costmap types, NavFn + DWB explanation, 5-row topics table, recovery behaviors, YAML costmap config, 2 Mermaid diagrams, Summary (7 rows) |

---

## State Transitions

```
Draft --> Review --> Published
```

- **Draft**: MDX file created; may have incomplete sections.
- **Review**: All sections complete; `npm run build` passes; no bare angle brackets; ASCII-only code.
- **Published**: Merged to `main`; deployed to GitHub Pages.
