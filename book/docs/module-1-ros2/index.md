---
id: module-1-overview
title: "Module 1: The Robotic Nervous System"
sidebar_position: 0
description: "Overview of ROS 2 as the nervous system of humanoid robots — the middleware that connects AI software to physical hardware."
tags:
  - ros2
  - module-1
  - overview
---

# Module 1: The Robotic Nervous System

Humanoid robots are complex machines where dozens of sensors, actuators, and software
systems must work together in real time. At the center of this coordination sits a
middleware layer — the robotic equivalent of a nervous system — that relays signals
between the robot's "brain" (AI software) and its "body" (physical hardware).

In this module, we explore **ROS 2 (Robot Operating System 2)**, the open-source
middleware that has become the industry standard for modern robotics development.

---

## Prerequisites

Before starting this module, you should be comfortable with:

- **Python 3.10+**: writing functions, classes, and using libraries
- **Basic AI/ML concepts**: understanding that AI systems process inputs and produce decisions
- **Command-line basics**: navigating directories and running commands in a terminal

No prior robotics or ROS experience is required.

---

## What You'll Learn

This module consists of three chapters that build on each other:

### Chapter 1 — Introduction to ROS 2 and the Robotic Nervous System

You will learn what middleware is, why ROS 2 is the go-to framework for modern
humanoid robotics, how the ROS 2 architecture is organized, and how information
travels between robotic components using nodes, topics, and messages.

### Chapter 2 — ROS 2 Communication Model

You will implement your first ROS 2 Python nodes using the `rclpy` library, learn
the difference between topics (streaming data) and services (request-response), and
trace how an AI agent's decision becomes a hardware command delivered through ROS 2.

### Chapter 3 — Robot Structure and Description (URDF)

You will learn how a humanoid robot's physical body is described in the URDF
(Unified Robot Description Format) — an XML standard that defines every link and
joint of the robot — and how this description integrates with the ROS 2 runtime.

---

## Module Learning Outcomes

By the end of this module you will be able to:

1. Explain what ROS 2 is and why it is used in humanoid robotics
2. Describe the ROS 2 architecture and the role of the DDS transport layer
3. Implement a basic publisher and subscriber node in Python using `rclpy`
4. Read and interpret a URDF file for a humanoid robot
5. Explain how ROS 2 connects AI software to physical robot hardware

---

> **Ready to start?** Head to [Chapter 1 — Introduction to ROS 2 →](./chapter-1-intro.md)
