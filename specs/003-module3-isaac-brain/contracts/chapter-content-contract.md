# Chapter Content Contract: Module 3 — The AI-Robot Brain (NVIDIA Isaac)

**Branch**: `003-module3-isaac-brain` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This document defines the required structure and content elements for each file in Module 3.
All chapter files MUST conform to this contract before the `npm run build` acceptance check.

---

## Frontmatter Schema (All Files)

```yaml
---
id: <file-slug>          # matches filename without .md extension
sidebar_position: <N>    # integer, unique within module-3-isaac-brain/
---
```

---

## Body Section Order (All Chapters)

| Order | Section | Required |
|---|---|---|
| 1 | `## Learning Objectives` (exactly 4 bullet points) | MUST |
| 2 | `:::info Prerequisites` admonition | MUST |
| 3–N | Content sections (prose + diagrams + code blocks) | MUST |
| Last | `## Summary` table (minimum 7 rows) | MUST |

---

## Contract: `_category_.json`

| Field | Required Value |
|---|---|
| `label` | `"Module 3: The AI-Robot Brain"` |
| `position` | `3` |
| `collapsible` | `true` |
| `collapsed` | `false` |
| `description` | `"NVIDIA Isaac Sim, Isaac ROS perception, and Nav2 navigation for humanoid robots"` |

---

## Contract: `index.md`

**Frontmatter**: `id: module-3-overview`, `sidebar_position: 0`

**Required sections** (in order):

| Section | Required Content |
|---|---|
| Opening narrative | Three-layer brain metaphor: train (Isaac Sim), perceive (Isaac ROS), navigate (Nav2) |
| Prerequisites admonition | Links to Module 1 and Module 2 |
| Chapter overview table | 3 rows: chapter title / tool / role |
| Module Learning Outcomes | Exactly 5 bullet points |
| CTA link | `[Chapter 1 — NVIDIA Isaac Sim →](./chapter-1-isaac-sim.md)` |

---

## Contract: `chapter-1-isaac-sim.md`

**Frontmatter**: `id: chapter-1-isaac-sim`, `sidebar_position: 1`

**Prerequisites admonition**: Links to Module 1 (hardware overview) and Module 2 (simulation foundations).

**Required content elements**:

| Element | Specification |
|---|---|
| Learning Objectives | Exactly 4 bullet points |
| Four pillars section | Omniverse, USD, RTX, PhysX — each defined |
| Isaac Sim vs Gazebo table | Exactly 6 rows: Rendering, Physics engine, Scene format, AI training, ROS 2 integration, Hardware requirement |
| Why Synthetic Data section | Data problem stated (expensive, slow, dangerous); synthetic data as solution |
| Replicator section | 4 randomization categories; label types table (min 5 rows); annotated YAML config block |
| Pipeline position section | Isaac Sim → trained model → Isaac ROS (reference to Chapter 2) |
| Mermaid diagram 1 | Replicator pipeline: IsaacSim → Replicator → DomainRandomization → SyntheticDataset → AIModelTraining (max 8 nodes) |
| Mermaid diagram 2 | Chapter narrative arc: IsaacSim → SyntheticData → IsaacROS → RealWorldPerception → Nav2 → AutonomousNavigation (max 8 nodes) |
| Summary table | Minimum 7 rows: Isaac Sim, Omniverse, USD, RTX, Replicator, Synthetic Data, Domain Randomization |

**Validation rules**:
- YAML config block uses `yaml` language tag with first-line comment identifying context
- All fenced block content ASCII-only
- No bare angle brackets in prose or table cells

---

## Contract: `chapter-2-isaac-ros.md`

**Frontmatter**: `id: chapter-2-isaac-ros`, `sidebar_position: 2`

**Prerequisites admonition**: Link to Chapter 1 (Isaac Sim synthetic data output).

**Required content elements**:

| Element | Specification |
|---|---|
| Learning Objectives | Exactly 4 bullet points |
| What is Isaac ROS section | ROS 2 GPU-accelerated packages; fps comparison: 5 fps (CPU) vs 60 fps (GPU) stated explicitly |
| NITROS section | Zero-copy transport; before/after memory copy explanation; 12x speedup rationale |
| GEM table | Exactly 4 rows: isaac_ros_visual_slam, isaac_ros_object_detection, isaac_ros_image_segmentation, isaac_ros_depth_segmentation |
| cuVSLAM section | Exactly 5-step pipeline in prose (Feature Extraction, Feature Matching, Visual Odometry, Map Update, Loop Closure) |
| ROS 2 interface | Input: /camera/image_raw; Output: /visual_slam/tracking/odometry → /odom |
| Bash launch block | `ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py` with comment; bash language tag |
| Mermaid diagram 1 | cuVSLAM pipeline: FeatureExtraction → FeatureMatching → VisualOdometry → MapUpdate → LoopClosure → /odom → Nav2 (max 8 nodes = exactly 7) |
| Mermaid diagram 2 | Isaac ROS perception pipeline graph LR with /camera, NITROS, cuVSLAM, ObjectDetection, /odom (max 8 nodes) |
| Summary table | Minimum 7 rows: Isaac ROS, GEM, NITROS, cuVSLAM, Feature Extraction, Loop Closure, Visual Odometry |

**Validation rules**:
- Bash block uses `bash` language tag
- GEM acronym defined on first use: "GPU-Enabled Module"
- NITROS acronym defined on first use: "NVIDIA Transport for ROS"
- No bare angle brackets in ROS 2 topic names in prose (use backticks)

---

## Contract: `chapter-3-nav2.md`

**Frontmatter**: `id: chapter-3-nav2`, `sidebar_position: 3`

**Prerequisites admonition**: Links to Chapter 2 (cuVSLAM pose output) and Module 1 (robot hardware).

**Required content elements**:

| Element | Specification |
|---|---|
| Learning Objectives | Exactly 4 bullet points |
| What is Nav2 section | ROS 2 navigation stack; successor to move_base; receives /odom from cuVSLAM; outputs /cmd_vel |
| Costmaps section | Global costmap (full map, Dijkstra planner) and local costmap (rolling window, DWB controller); inflation radius defined |
| Planners section | NavFn global planner (Dijkstra's algorithm); DWB Controller local planner (sample velocities, score, execute best) |
| Nav2 topics table | Exactly 5 rows: /map, /odom, /scan, /goal_pose, /cmd_vel; columns: Topic / Direction / Message Type / Purpose |
| Recovery behaviors | Spin, Back Up, Clear Costmap — each defined |
| Mermaid diagram 1 | Nav2 architecture LR: GlobalCostmap + LocalCostmap → NavFn → DWBController → /cmd_vel (max 8 nodes) |
| Mermaid diagram 2 | Navigation sequence diagram with 4 participants: Goal, Nav2, LocalPlanner, Robot |
| YAML costmap config | Annotated block with inflation_radius, resolution, update_frequency; yaml language tag; first-line comment |
| Summary table | Minimum 7 rows: Nav2, Global Costmap, Local Costmap, Inflation Radius, NavFn, DWB Controller, Recovery Behavior |

**Validation rules**:
- YAML block uses `yaml` language tag with first-line comment
- ROS 2 topic names in prose wrapped in backticks (not bare angle brackets)
- Sequence diagram participants limited to 4 (Goal, Nav2, LocalPlanner, Robot)

---

## Cross-Chapter Validation Checklist

- [ ] `_category_.json` position is `3`
- [ ] `index.md` `sidebar_position` is `0`; links to `./chapter-1-isaac-sim.md`
- [ ] Each chapter has exactly 4 Learning Objectives
- [ ] Chapter 1 has 6-row Isaac Sim vs Gazebo table and Replicator YAML block
- [ ] Chapter 2 has 4-row GEM table, 5-step cuVSLAM prose, bash launch block
- [ ] Chapter 3 has 5-row Nav2 topics table, YAML costmap config, recovery behaviors
- [ ] All prerequisite admonitions present (ch1: Modules 1+2; ch2: ch1; ch3: ch2 + Module 1)
- [ ] All Summary tables have minimum 7 rows
- [ ] No bare XML angle brackets in prose or table cells
- [ ] All fenced blocks ASCII-only
- [ ] `npm run build` passes with zero errors and zero broken links
