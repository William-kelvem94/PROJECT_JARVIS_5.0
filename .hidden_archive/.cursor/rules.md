# JARVIS 5.0 - Project Rules

## 🧠 Core Philosophy
- **Modular Architecture**: All core logic resides in `src/core/`.
- **Absolute Imports**: Always import from `src` root (e.g., `from src.core.intelligence.ai_agent import AIAgent`).
- **Configuration Driven**: Use `src/utils/config.py` and `config/ai_config.yaml` for all configurable parameters. Hardcoding is forbidden.
- **Logging**: Use `src.utils.logger` for all output. `print()` is allowed for debugging only.

## 📂 Directory Structure
- `src/core/intelligence`: AI logic, LLM integration, Brain Router.
- `src/core/audio`: STT (Vosk/Whisper) and TTS (Edge-TTS) engines.
- `src/core/vision`: YOLO, MediaPipe, OCR.
- `src/interface`: PyQt6 GUI components.
- `data/`: All runtime data (logs, databases, memories). NEVER commit files here except `.gitkeep`.

## 🤖 AI Models
- **Local (Preferred)**: `ollama:gemma3:4b`, `ollama:qwen2.5:3b`.
- **Cloud**: `gemini-2.0-flash-exp`.
- **Vision**: `yolov8n.pt` (Object Detection), `MediaPipe` (Hand Tracking).

## 🛠️ Development Guidelines
- **Type Hinting**: Mandatory for all function signatures.
- **Docstrings**: Required for all public classes and methods (Google or NumPy style).
- **Error Handling**: Use `try/except` blocks with specific exceptions and log errors properly.
- **Async/Await**: Use for I/O bound operations (especially LLM and Audio calls).

## ⚠️ Important Constraints
- **Do NOT** use `sys.path.append` for imports. The environment is configured for `src` as root.
- **Do NOT** commit API keys. Use `.env`.
- **Verify** paths using `pathlib.Path` relative to `project_root`.

## 🧪 Testing
- Run tests using `pytest tests/`.
- Ensure mocks are used for external API calls in unit tests.
