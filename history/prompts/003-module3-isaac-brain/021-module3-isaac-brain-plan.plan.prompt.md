---
id: "021"
title: Module 3 Isaac Brain Plan
stage: plan
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: 003-module3-isaac-brain
branch: 003-module3-isaac-brain
user: hp
command: /sp.plan
labels: ["plan","isaac-sim","isaac-ros","nav2","vslam","nitros","synthetic-data","module3"]
links:
  spec: specs/003-module3-isaac-brain/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-module3-isaac-brain/research.md
  - specs/003-module3-isaac-brain/plan.md
  - specs/003-module3-isaac-brain/data-model.md
  - specs/003-module3-isaac-brain/quickstart.md
  - specs/003-module3-isaac-brain/contracts/chapter-content-contract.md
tests:
  - Constitution Check: 5/5 PASS
  - Acceptance checks defined: 11 items
---

## Prompt

/sp.plan
Create Module 3 in the Docusaurus documentation structure with three chapters covering NVIDIA Isaac Sim photorealistic simulation, Isaac ROS GPU-accelerated perception pipelines, and Nav2 autonomous navigation.
Write the chapters in Markdown explaining Isaac Sim synthetic data generation, Isaac ROS GEMs and cuVSLAM visual SLAM, and Nav2 costmaps and path planning used in humanoid robot systems.

## Response snapshot

Phase 0 (Research) — 8 decisions resolved:
1. Isaac Sim architecture: 4 pillars (Omniverse, USD, RTX, PhysX)
2. Isaac Sim vs Gazebo comparison: 6-row table (rendering, physics, scene format, AI training, ROS 2 integration, hardware)
3. Replicator domain randomization: 4 categories (lighting, materials, object poses, camera params); 5 label types
4. Isaac ROS GEMs: 4 packages (visual_slam, object_detection, image_segmentation, depth_segmentation)
5. cuVSLAM: 5-step pipeline (feature extraction, matching, visual odometry, map update, loop closure)
6. NITROS: zero-copy GPU transport; 5 fps CPU vs 60 fps GPU = 12x speedup
7. Nav2 components: global costmap, local costmap, inflation radius, NavFn, DWB Controller + 5-topic interface
8. Recovery behaviors: Spin, Back Up, Clear Costmap

Phase 1 (Design) — 5 Phase 1 artifacts generated:
- research.md: all 8 unknowns resolved with rationale and alternatives considered
- plan.md: Constitution 5/5 PASS; full chapter architecture for Ch1 (Isaac Sim), Ch2 (Isaac ROS), Ch3 (Nav2); 11 acceptance checks; 3 risks
- data-model.md: 5 entities (Module, Chapter, YAML block, Bash block, Mermaid); content map table; state transitions
- quickstart.md: dev server workflow; 4 content validation checks; build validation; 6 common issues table
- contracts/chapter-content-contract.md: per-chapter contracts with exact required elements; cross-chapter validation checklist (11 items)

Source structure:
- book/docs/module-3-isaac-brain/_category_.json (position 3)
- book/docs/module-3-isaac-brain/index.md (sidebar_position: 0)
- book/docs/module-3-isaac-brain/chapter-1-isaac-sim.md (sidebar_position: 1)
- book/docs/module-3-isaac-brain/chapter-2-isaac-ros.md (sidebar_position: 2)
- book/docs/module-3-isaac-brain/chapter-3-nav2.md (sidebar_position: 3)

## Outcome

- OK Impact: Module 3 implementation plan created -- all 3 chapters architected, 8 research decisions resolved, 5 Phase 1 artifacts generated
- Tests: Constitution Check 5/5 PASS; 11 acceptance checks defined in plan.md
- Files: research.md + plan.md + data-model.md + quickstart.md + contracts/chapter-content-contract.md
- Next prompts: /sp.tasks for Module 3; then /sp.implement to create book/docs/module-3-isaac-brain/ files
- Reflection: cuVSLAM 7-node Mermaid pipeline (Ch2 diagram 1) is exactly at the 8-node limit -- verified safe. NITROS complexity risk mitigated by focusing on fps outcome rather than CUDA internals.

## Evaluation notes (flywheel)

- Failure modes observed: Write tool silent failure on Windows/OneDrive when parent directory missing -- fixed by pre-creating dirs with New-Item -Force before every Write call
- Graders run and results (PASS/FAIL): Constitution Check PASS (5/5); spec quality checklist 16/16 PASS
- Prompt variant (if applicable): none
- Next experiment: /sp.tasks for Module 3 to generate T001-T007 task list before implementation
