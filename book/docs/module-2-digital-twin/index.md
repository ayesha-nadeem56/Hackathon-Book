---
id: module-2-overview
sidebar_position: 0
---

# Module 2: The Digital Twin

Before you put software on a real robot, you test it in simulation. A crash in simulation costs nothing. A crash on a USD 200,000 humanoid costs time, parts, and sometimes safety.

A **digital twin** is a software replica of a physical robot -- one that mirrors the robot's geometry, dynamics, and sensor outputs in real time. In this module you will build that replica. You will learn how physics simulators model the forces that govern robot movement, how a high-fidelity rendering engine makes HRI (Human-Robot Interaction) research possible, and how simulated sensors produce the exact same ROS 2 message types that real sensors publish.

By the end of this module, your simulation and your real robot will speak the same language.

---

:::info Prerequisites

Before starting this module, you should have completed:

- **Module 1 -- ROS 2 Foundations**: ROS 2 topics, publishers, subscribers, and message types

:::

---

## Module Chapters

| Chapter | Tool | What You Will Learn |
|---|---|---|
| Chapter 1 -- Physics Simulation with Gazebo | Gazebo | How a physics engine models gravity, collisions, inertia, and friction to create a realistic robot body |
| Chapter 2 -- High-Fidelity Environments with Unity | Unity + ROS-TCP-Connector | How to build photorealistic HRI environments and bridge them to ROS 2 |
| Chapter 3 -- Simulating Robot Sensors | Gazebo Sensor Plugins | How LiDAR, RGBD cameras, and IMUs are simulated and how their output maps to standard ROS 2 message types |

---

## Module Learning Outcomes

By the end of this module you will be able to:

- Define a digital twin and explain why simulation is essential before hardware deployment
- Describe how Gazebo models gravity, collisions, inertia, and friction for a humanoid robot body
- Explain why Unity is used for HRI research and how ROS-TCP-Connector bridges Unity to ROS 2
- Name the ROS 2 message types for LiDAR, depth camera, and IMU sensor data
- Trace simulated sensor data from a Gazebo plugin through a ROS 2 topic to a subscriber node

---

[Chapter 1 -- Physics Simulation with Gazebo →](./chapter-1-gazebo.md)
