# Implementation Plan: Module 3 — The AI-Robot Brain (NVIDIA Isaac)

**Branch**: `003-module3-isaac-brain` | **Date**: 2026-03-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-module3-isaac-brain/spec.md`

---

## Summary

Extend the Docusaurus book with a third module (`book/docs/module-3-isaac-brain/`) covering NVIDIA Isaac tools for AI-driven robotics. The module comprises a module index page, a `_category_.json` sidebar descriptor, and three chapter files in MDX-compatible Markdown. All content is conceptual (no GPU hardware installation required); chapters include Mermaid diagrams, YAML/bash configuration examples in ASCII-only fenced blocks, prerequisite admonitions, and summary tables (minimum 7 rows each). The Docusaurus build must pass with zero errors and zero broken links.

---

## Technical Context

**Language/Version**: MDX v3 (Docusaurus 3.9.2)
**Primary Dependencies**: Docusaurus 3.9.2 (already scaffolded in `book/`); Mermaid plugin (already configured)
**Storage**: N/A — static file generation only
**Testing**: `npm run build` in `book/` (zero errors, zero broken links)
**Target Platform**: GitHub Pages; authoring on Windows 10 / OneDrive
**Project Type**: Documentation module (Docusaurus category)
**Constraints**:
  - ASCII-only characters in all fenced code/config blocks (Windows cp1252 safe)
  - No bare XML angle brackets in prose or table cells (MDX v3 JSX parser)
  - Relative links between chapters use `.md` extension
  - Module category `position: 3` (follows Module 2 at position 2)
  - Mermaid diagrams: maximum 8 nodes; camelCase/underscore node IDs only
  - YAML config blocks preferred over Python f-strings (curly braces in prose risk MDX parsing)
**Scale/Scope**: 5 files — 1 `_category_.json`, 1 `index.md`, 3 chapter `.md` files

---

## Constitution Check

| Gate | Status | Evidence |
|---|---|---|
| I. Accuracy & Technical Correctness | PASS | All technical claims (Isaac Sim 4.x, cuVSLAM 5-step pipeline, Nav2 DWB controller, NITROS zero-copy) verified in research.md |
| II. Clarity & Readability | PASS | Each chapter has 4 Learning Objectives, defined terms on first use, prerequisite admonitions, summary table |
| III. Reproducibility of Workflows | PASS | Config examples are YAML-based and annotated; no software installation required; conceptual-only |
| IV. Modularity & Architecture | PASS | Module is a self-contained Docusaurus category at position 3; no changes to other modules or shared infrastructure |
| V. Transparency in AI Content | PASS | No chatbot content in scope; chapter prose reviewed before merge |

No violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-module3-isaac-brain/
├── plan.md              # This file
├── research.md          # Phase 0 -- all unknowns resolved
├── data-model.md        # Phase 1 -- content structure schema
├── quickstart.md        # Phase 1 -- development workflow
├── tasks.md             # Phase 2 output (/sp.tasks -- NOT created here)
├── checklists/
│   └── requirements.md  # Spec quality checklist (16/16 PASS)
└── contracts/
    └── chapter-content-contract.md  # Phase 1 -- chapter structure contract
```

### Source Code (repository)

```text
book/docs/module-3-isaac-brain/
├── _category_.json            # Sidebar label, position 3, collapsible
├── index.md                   # Module landing page with chapter overview
├── chapter-1-isaac-sim.md     # Isaac Sim + synthetic data + Replicator
├── chapter-2-isaac-ros.md     # Isaac ROS GEMs + NITROS + cuVSLAM
└── chapter-3-nav2.md          # Nav2 costmaps + planners + recovery
```

---

## Phase 0: Research

See [research.md](./research.md) for full findings. Summary:

| Unknown | Resolution |
|---|---|
| Isaac Sim architecture | Four pillars: Omniverse / USD / RTX / PhysX |
| Isaac Sim vs Gazebo dimensions | 6-row table: rendering, physics, scene format, AI training, ROS 2 integration, hardware |
| Replicator domain randomization | Varies: lighting, materials, object poses, camera params; annotated YAML config |
| Isaac ROS GEM selection | 4 GEMs: visual_slam, object_detection, image_segmentation, depth_segmentation |
| cuVSLAM pipeline | 5 steps: feature extraction, matching, visual odometry, map update, loop closure |
| NITROS performance | 5 fps (CPU) vs 60 fps (GPU) -- 12x improvement; zero CPU-GPU copy architecture |
| Nav2 components | global costmap + local costmap + inflation radius + NavFn + DWB Controller |
| Nav2 topic interface | 5 topics: /map, /odom, /scan, /goal_pose, /cmd_vel |
| Recovery behaviors | Spin, Back Up, Clear Costmap |

---

## Phase 1: Design

### Content Architecture per Chapter

#### `_category_.json`

```json
{
  "label": "Module 3: The AI-Robot Brain",
  "position": 3,
  "collapsible": true,
  "collapsed": false,
  "description": "NVIDIA Isaac Sim, Isaac ROS perception, and Nav2 navigation for humanoid robots"
}
```

#### `index.md` — Module Landing Page

Front-matter: `id: module-3-overview`, `sidebar_position: 0`

Sections:
1. Opening narrative — the three-layer brain: train (Isaac Sim), perceive (Isaac ROS), navigate (Nav2)
2. Prerequisites admonition — Modules 1 and 2
3. Chapter overview table (3 rows: chapter / tool / role)
4. Module Learning Outcomes (5 items)
5. CTA link: `[Chapter 1 — NVIDIA Isaac Sim →](./chapter-1-isaac-sim.md)`

#### `chapter-1-isaac-sim.md` — NVIDIA Isaac Sim

Front-matter: `id: chapter-1-isaac-sim`, `sidebar_position: 1`

Sections:
1. **What is NVIDIA Isaac Sim?** — four pillars: Omniverse, USD, RTX, PhysX; why it produces photorealistic images for AI training
2. **Isaac Sim vs Gazebo** — 6-row comparison table; when to use each (AI training = Isaac Sim; functional testing = Gazebo)
3. **Why Synthetic Data?** — the data problem (collecting real annotated data is expensive, slow, dangerous); synthetic data solves all three
4. **Replicator: Domain Randomization** — what Replicator does; four randomization categories; label types table; annotated YAML config snippet (ASCII-only)
5. **Where Isaac Sim Fits in the Pipeline** — Isaac Sim generates data → AI model trained → deployed in Isaac ROS perception (Chapter 2)
6. **Mermaid diagram 1**: Replicator pipeline (IsaacSim --> Replicator --> DomainRandomization --> SyntheticDataset --> AIModelTraining)
7. **Mermaid diagram 2**: Chapter narrative arc (graph LR; IsaacSim --> SyntheticData --> IsaacROS --> RealWorldPerception --> Nav2 --> AutonomousNavigation)
8. **Summary table**: 7 rows (Isaac Sim, Omniverse, USD, RTX, Replicator, Synthetic Data, Domain Randomization)

#### `chapter-2-isaac-ros.md` — Isaac ROS Perception

Front-matter: `id: chapter-2-isaac-ros`, `sidebar_position: 2`

Sections:
1. **What is Isaac ROS?** — ROS 2 packages accelerated by NVIDIA GPU; why GPU matters for robotics (fps comparison: 5 fps CPU vs 60 fps GPU)
2. **NITROS: Zero-Copy Transport** — what NITROS does; before/after memory copy explanation; why it enables real-time throughput
3. **Isaac ROS GEMs** — 4-row GEM overview table (package / capability / key output topic); GEM = GPU-Enabled Module definition
4. **cuVSLAM: Visual SLAM on GPU** — 5-step pipeline prose (one paragraph per step); ROS 2 input/output topics
5. **Launching Isaac ROS cuVSLAM** — annotated bash `ros2 launch` command snippet (ASCII-only)
6. **Mermaid diagram 1**: cuVSLAM 7-node pipeline (FeatureExtraction --> FeatureMatching --> VisualOdometry --> MapUpdate --> LoopClosure --> /odom --> Nav2)
7. **Mermaid diagram 2**: Isaac ROS perception pipeline (graph LR; /camera --> NITROS --> cuVSLAM + ObjectDetection + ImageSegmentation --> /odom + /detections + /segmentation)
8. **Summary table**: 7 rows (Isaac ROS, GEM, NITROS, cuVSLAM, Feature Extraction, Loop Closure, Visual Odometry)

#### `chapter-3-nav2.md` — Navigation with Nav2

Front-matter: `id: chapter-3-nav2`, `sidebar_position: 3`

Sections:
1. **What is Nav2?** — successor to ROS 1 move_base; ROS 2 navigation stack; receives pose from cuVSLAM, outputs `/cmd_vel`
2. **Costmaps** — global costmap (full map); local costmap (rolling window from sensor data); inflation radius; why separate costmaps
3. **Planners and Controllers** — NavFn global planner (Dijkstra on global costmap); DWB Controller local planner (sample velocities, score trajectories, execute best)
4. **Nav2 Topics** — 5-row topic table (topic / direction / message type / purpose)
5. **Obstacle Avoidance and Recovery** — what happens when obstacle detected (local replanning); recovery behaviors: Spin, Back Up, Clear Costmap
6. **Mermaid diagram 1**: Nav2 architecture LR (GlobalCostmap + LocalCostmap --> NavFn --> DWBController --> /cmd_vel)
7. **Mermaid diagram 2**: Navigation sequence diagram (Nav2 receives /goal_pose; queries costmaps; plans path; executes; detects obstacle; recovers)
8. **Annotated YAML costmap config block** (ASCII-only, with inline comments explaining inflation_radius, resolution, update_frequency)
9. **Summary table**: 7 rows (Nav2, Global Costmap, Local Costmap, Inflation Radius, NavFn, DWB Controller, Recovery Behavior)

### Acceptance Checks

- [ ] `_category_.json` has `"position": 3`
- [ ] `index.md` has `sidebar_position: 0` and links to `./chapter-1-isaac-sim.md`
- [ ] Each chapter has exactly 4 Learning Objectives
- [ ] Chapter 1 has 6-row Isaac Sim vs Gazebo table and Replicator YAML block
- [ ] Chapter 2 has 4-row GEM table, cuVSLAM 5-step prose, 2 Mermaid diagrams
- [ ] Chapter 3 has 5-row Nav2 topics table, YAML costmap config, 2 Mermaid diagrams
- [ ] All prerequisite admonitions present (ch1: Modules 1+2; ch2: ch1; ch3: ch2 + Module 1)
- [ ] All Summary tables have minimum 7 rows
- [ ] No bare XML angle brackets in prose or table cells
- [ ] All fenced blocks ASCII-only
- [ ] `npm run build` passes with zero errors and zero broken links

---

## Follow-ups and Risks

- **Risk 1**: Mermaid diagram complexity — Isaac ROS perception pipeline (Ch 2, diagram 2) shows parallel GEM processing; keep to max 8 nodes by grouping secondary GEMs.
- **Risk 2**: NITROS explanation depth — NITROS involves CUDA memory management concepts that are beyond most students. Mitigation: focus on the user-visible outcome (fps improvement, no CPU copies) not the implementation.
- **Risk 3**: Nav2 sequence diagram length — the obstacle avoidance + recovery sequence has many steps; keep participants to 4 (Goal, Nav2, LocalPlanner, Robot) and collapse detail.

---

## ADR Suggestion

No architecturally significant decisions in this plan. The content structure (Docusaurus category, MDX, Mermaid, position 3) follows the established Module 1 and Module 2 pattern exactly.
