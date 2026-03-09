---
id: chapter-1-whisper
sidebar_position: 1
---

# Chapter 1: Voice-to-Action with Whisper

## Learning Objectives

By the end of this chapter you will be able to:

- Define Automatic Speech Recognition (ASR) and explain why it is the entry point of a VLA system
- Describe the OpenAI Whisper architecture and explain its training approach
- Select the appropriate Whisper model size for a robotics deployment given accuracy and speed constraints
- Explain how a ROS 2 node publishes a Whisper transcription to the `/voice_command` topic

---

:::info Prerequisites

This chapter builds on concepts from:

- **Module 1 -- ROS 2 Foundations**: ROS 2 publishers, subscribers, and `std_msgs/String`
- **Module 2 -- The Digital Twin**: Simulation concepts (used in later chapters)
- **Module 3 -- The AI-Robot Brain**: Isaac ROS and Nav2 (referenced in Chapter 3)

:::

---

## What is Automatic Speech Recognition?

**Automatic Speech Recognition (ASR)** is the task of converting an audio signal containing spoken language into a text string. The audio comes from a microphone; the output is a sequence of words that a computer can process.

For a VLA system, ASR is the first step in the pipeline. A robot cannot reason about what you said until it has a text representation of it. Without that text, there is nothing for the LLM planner (Chapter 2) to work with.

The key metric for ASR quality is **Word Error Rate (WER)**: the percentage of words in the transcription that are incorrect compared to the ground truth. Lower WER means higher accuracy.

---

## OpenAI Whisper

**Whisper** is an open-source ASR model released by OpenAI. It uses an **encoder-decoder transformer** architecture: the encoder processes the audio spectrogram and produces a representation of the speech, and the decoder generates the corresponding text token by token.

Whisper was trained on 680,000 hours of multilingual audio collected from the internet. This large and diverse training set makes it robust to different accents, background noise, and speaking styles -- which is important for a real-world robotics deployment.

Whisper is available as the `openai-whisper` Python package. You can run it locally on a GPU or CPU without sending audio data to an external API.

---

## Whisper Model Sizes

Whisper comes in five sizes. Each size trades accuracy for speed. For robotics, you want the best accuracy you can get while still fitting within your hardware budget and latency requirements.

| Model | Parameters | Relative Speed | English WER | Use Case |
|---|---|---|---|---|
| tiny | 39 M | ~32x | ~5.7% | Fastest -- on-device, low-latency prototyping |
| base | 74 M | ~16x | ~4.2% | Good balance for embedded systems |
| small | 244 M | ~6x | ~3.0% | Recommended for robotics (Jetson Orin class) |
| medium | 769 M | ~2x | ~2.4% | High accuracy, GPU recommended |
| large | 1550 M | 1x (reference) | ~2.0% | Highest accuracy, requires dedicated GPU |

**Notes**: WER = Word Error Rate; lower is better. Relative speed is relative to `large`. The `small` model is the recommended starting point for a robot running on a Jetson Orin or equivalent edge GPU: it achieves 3.0% WER at 6x the speed of `large`, which is fast enough for push-to-talk interaction.

---

## Transcribing Audio in Python

The `openai-whisper` package provides a simple two-step API: load the model once, then call `transcribe()` for each audio clip.

```python
import whisper                        # openai-whisper package
import sounddevice as sd             # audio capture from microphone
import numpy as np

# Load the model once (keep in memory for low latency between commands)
model = whisper.load_model("small")  # 244M params -- good robotics trade-off

def transcribe_command(duration_sec=4, sample_rate=16000):
    # Capture audio from the default microphone
    audio = sd.rec(
        int(duration_sec * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )
    sd.wait()                         # block until recording is complete
    audio_flat = audio.flatten()      # Whisper expects 1D float32 array

    # Transcribe -- returns dict with 'text', 'segments', 'language'
    result = model.transcribe(audio_flat, fp16=False)
    return result["text"].strip()     # return plain text transcription
```

Key points:
- `whisper.load_model("small")` loads the model into memory. Do this once at startup, not on every call -- model loading takes several seconds.
- `sd.rec()` captures audio from the default microphone for `duration_sec` seconds.
- `audio.flatten()` converts the 2D array (samples x channels) into the 1D array that Whisper expects.
- `model.transcribe(audio_flat, fp16=False)` runs ASR. Set `fp16=False` on CPU; set `fp16=True` on GPU for faster inference.
- `result["text"]` contains the transcription. The result dict also includes `segments` (word-level timing) and `language` (detected language).

---

## ROS 2 Voice Integration

In a ROS 2 system, Whisper runs inside a **ROS 2 node** called the Voice Node. The node:

1. Waits for a push-to-talk signal or a Voice Activity Detection (VAD) trigger
2. Captures audio from the microphone using `sounddevice`
3. Calls `model.transcribe()` to convert audio to text
4. Publishes the text string to `/voice_command` as a `std_msgs/String` message
5. The LLM Planner Node (Chapter 2) subscribes to `/voice_command` and receives the command

Here is a minimal ROS 2 publisher that adds the Whisper transcription into the ROS 2 graph:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import whisper
import sounddevice as sd

class VoiceNode(Node):
    def __init__(self):
        super().__init__("voice_node")
        self.pub = self.create_publisher(String, "/voice_command", 10)
        self.model = whisper.load_model("small")
        self.get_logger().info("Voice node ready -- waiting for commands")

    def capture_and_publish(self):
        # Record 4 seconds of audio at 16 kHz
        audio = sd.rec(64000, samplerate=16000, channels=1, dtype="float32")
        sd.wait()
        # Transcribe and publish
        result = self.model.transcribe(audio.flatten(), fp16=False)
        text = result["text"].strip()
        msg = String()
        msg.data = text
        self.pub.publish(msg)
        self.get_logger().info("Published: " + text)
```

The `/voice_command` topic is a simple `std_msgs/String` topic -- any node that needs the transcription just subscribes to it. This keeps the Voice Node decoupled from the rest of the pipeline.

---

## Voice-to-Action Pipeline

```mermaid
graph LR
    Microphone --> AudioBuffer
    AudioBuffer --> WhisperModel
    WhisperModel --> Transcription
    Transcription --> ROSPublisher
    ROSPublisher --> /voice_command
    /voice_command --> LLMPlannerNode
```

The pipeline is strictly linear: audio in, text out, published to a ROS 2 topic. Each step has a single input and a single output, which makes it easy to test each component in isolation.

---

## Summary

| Term | Definition |
|---|---|
| ASR | Automatic Speech Recognition -- converting audio to text |
| Whisper | OpenAI open-source ASR model; encoder-decoder transformer |
| Encoder-Decoder | Whisper architecture: encoder processes audio, decoder generates text |
| WER | Word Error Rate -- percentage of incorrectly transcribed words; lower is better |
| /voice_command | ROS 2 topic carrying the transcribed command as a `std_msgs/String` |
| std_msgs/String | ROS 2 message type used to publish plain text strings |

---

**Next**: [Chapter 2 -- Cognitive Planning with LLMs →](./chapter-2-llm-planner.md)
