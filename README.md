# 🤖 JARVIS 5.0 - Artificial Intelligence System

![JARVIS Status](https://img.shields.io/badge/Status-Production-brightgreen)
![Version](https://img.shields.io/badge/Version-5.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)

### A Cognitive Computing Framework for Autonomous Learning and System Automation.

---

## 🚀 Overview

JARVIS 5.0 is a highly modular, autonomous AI system designed to operate locally on Windows. It integrates advanced Voice recognition, Neural curiosity, Autonomous Research, and Continual Learning.

### Key Production Features:
- **🧠 Continuous Learning Engine**: Autonomous gap analysis and knowledge acquisition.
- **🌙 Dream Cycle**: Background processing for system optimization and training during idle periods.
- **🎙️ Natural Voice Interaction**: Low-latency STT and TTS engines (Edge-TTS, OpenAI Whisper).
- **👁️ Computer Vision**: Context-aware screen analysis and visual grounding.
- **🛡️ Hardware Integration**: Real-time monitoring and hardware-accelerated inference (OpenVINO).

---

## 🛠️ Project Structure

- `jarvis/`: Core package containing the Agent, LLM logic, and Voice/Vision modules.
- `src/`: Refactored high-level engines (Learning, Curiosity, Evolution).
- `config/`: Centralized control files (`ai_config.yaml`).
- `data/`: Persistence layer (Databases, logs, metrics).
- `tools/`: Diagnostic and maintenance scripts.
- `logs/`: System logs and execution reports.

---

## ⚙️ Installation & Usage

1. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Launch JARVIS**:
   ```powershell
   python main.py
   ```

3. **Options**:
   - `--text`: CLI input mode.
   - `--voice`: Microphone mode (Default).
   - `--both`: Parallel Voice and Text processing.
   - `--debug`: Verbose logging and real-time reflection.

---

## 🔧 Refactoring Phase (Current Stage)

The system is undergoing a transition to a **Production Architecture**:
1. ✅ **Phase 1**: Critical Fixes & Standardized Exception Handling.
2. ✅ **Phase 2**: Modularization of `DreamCycle` and `IdleDetector`.
3. 🔲 **Phase 3**: Decoupling with Strategy and Repository patterns.

---

## 📜 Professional Standard

Everything in this repository (except for the `BACKUP/` folder) is part of the **Official Production Code**. The system is built with high standards for modularity, privacy (local-first), and performance.

---

*“Sir, I’ve completed the system upgrade. We are now running at full capacity.”*
