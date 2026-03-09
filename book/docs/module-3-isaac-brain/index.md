---
id: module-3-overview
sidebar_position: 0
---

# Module 3: The AI-Robot Brain

Every humanoid robot needs a brain — a system that can learn what the world looks like, understand what it is seeing right now, and decide how to move through it safely. NVIDIA Isaac provides exactly that, organized into three layers that work together:

- **Train** — Isaac Sim generates photorealistic synthetic data so AI perception models can learn to see without spending months collecting dangerous real-world footage.
- **Perceive** — Isaac ROS runs those trained models on the GPU in real time, tracking the robot's position with Visual SLAM and detecting objects as the robot moves.
- **Navigate** — Nav2 consumes the robot's pose from Isaac ROS and executes autonomous motion — planning paths, avoiding obstacles, and recovering from unexpected situations.

This module walks through each layer in sequence, building your understanding from data generation through to autonomous movement.

:::info Prerequisites

This module assumes you have completed:

- [Module 1: Humanoid Robotics and ROS 2](../module-1-ros2/index.md) — ROS 2 topics, nodes, and the robot hardware stack
- [Module 2: The Digital Twin](../module-2-digital-twin/index.md) — simulation environments and sensor simulation

:::

## Chapter Overview

| Chapter | Tool | Role in the Pipeline |
|---|---|---|
| Chapter 1 — NVIDIA Isaac Sim | Isaac Sim + Replicator | Generate photorealistic synthetic training data for AI perception models |
| Chapter 2 — Isaac ROS Perception | Isaac ROS GEMs + cuVSLAM + NITROS | Run GPU-accelerated perception on real sensor data; estimate robot pose |
| Chapter 3 — Navigation with Nav2 | Nav2 + NavFn + DWB Controller | Plan paths and execute autonomous movement using the pose from Isaac ROS |

## Module Learning Outcomes

By the end of this module you will be able to:

- Explain why synthetic data generated in Isaac Sim is used to train AI perception models for real-world robots.
- Describe the cuVSLAM Visual SLAM pipeline — the five steps from raw camera frames to a robot pose estimate.
- Explain how NITROS zero-copy transport eliminates CPU bottlenecks in the Isaac ROS perception pipeline.
- Describe how Nav2 uses global and local costmaps to plan paths and avoid obstacles autonomously.
- Trace a single navigation request from spoken command through Isaac ROS pose estimation to Nav2 velocity output.

---

[Chapter 1 — NVIDIA Isaac Sim →](./chapter-1-isaac-sim.md)
