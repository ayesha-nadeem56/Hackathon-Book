---
id: module-4-overview
sidebar_position: 0
---

# Module 4: Vision-Language-Action

What if a robot could listen to what you say, reason about what you mean, and then go do it?

That is the promise of **Vision-Language-Action (VLA)** systems. This module closes the arc of the entire book by connecting the pieces you have built across Modules 1 to 3 into a single, coherent pipeline: a humanoid robot that receives a spoken command, plans a sequence of actions using a Large Language Model, and executes those actions using ROS 2, Nav2, and an arm controller.

This is not science fiction. It is software engineering -- and by the end of this module, you will be able to trace every step of that pipeline from the moment a person speaks to the moment a robot arm reaches out to grasp an object.

---

:::info Prerequisites

Before starting this module, you should have completed:

- **Module 1 -- ROS 2 Foundations**: ROS 2 topics, publishers, subscribers, and the `rclpy` API
- **Module 2 -- The Digital Twin**: Gazebo simulation, sensor simulation, and digital twin concepts
- **Module 3 -- The AI-Robot Brain**: NVIDIA Isaac Sim, Isaac ROS perception (cuVSLAM, object detection), and Nav2 autonomous navigation

:::

---

## Module Chapters

| Chapter | Tool | Role in the Pipeline |
|---|---|---|
| Chapter 1 -- Voice-to-Action | OpenAI Whisper | Converts spoken language into a text command on a ROS 2 topic |
| Chapter 2 -- Cognitive Planning with LLMs | LLM Planner | Interprets the text command and produces a structured action sequence |
| Chapter 3 -- Autonomous Humanoid Capstone | Full VLA Pipeline | Integrates Whisper, LLM planner, Nav2, Isaac ROS, and arm controller end-to-end |

---

## Module Learning Outcomes

By the end of this module you will be able to:

- Explain how OpenAI Whisper converts audio to text and publishes the result to a ROS 2 topic
- Describe why raw LLM output cannot directly drive a robot and how prompt engineering solves this
- Construct a system prompt that constrains LLM output to a robot action vocabulary
- Trace the complete VLA data flow from a spoken command to a physical robot action
- Identify which module (1, 2, 3, or 4) is responsible for each layer of the autonomous humanoid pipeline

---

[Chapter 1 -- Voice-to-Action with Whisper →](./chapter-1-whisper.md)
