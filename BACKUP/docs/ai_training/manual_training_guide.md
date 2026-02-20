# Manual Training Guide for JARVIS 5.0 AI

## Purpose
This document guides you on how to manually train the JARVIS 5.0 AI, allowing you to feed the system with new data, examples, corrections, and feedback to improve the performance of local models and neural memory.

---

## 1. Recommended Structure for Manual Training

### a) Text Data (Conversations, Q&A, Corrections, Contexts)
- **Location:** `data/learning/`, `data/knowledge/`, or `data/memories/`
- **Format:** `.jsonl`, `.csv`, or `.txt`
- **Recommended fields:**
  - `prompt`: User input or question
  - `response`: Ideal or corrected answer
  - `context` (optional): Situation, user profile, or system state
  - `tags` (optional): e.g. `["math", "troubleshooting", "hardware"]`
  - `feedback` (optional): User rating or notes
- **Example file:**
  - `data/learning/manual_training.jsonl`
  - Each line: `{ "prompt": "How to restart the system?", "response": "Use the command 'restart' in the dashboard.", "tags": ["system", "commands"] }`

### b) Image Data (Computer Vision, UI, FaceID, OCR)
- **Location:** `data/training_dataset/`, `data/vision/`, `data/faces/`, `data/exports/`
- **Format:** Folders by category, with optional metadata in `.json`
- **Recommended structure:**
  - `data/training_dataset/faces/username/` (face images per user)
  - `data/training_dataset/ui_elements/buttons/` (UI element screenshots)
  - `data/training_dataset/ocr_samples/` (images with ground-truth text)
  - Metadata: `{ "label": "button_ok", "bbox": [x, y, w, h], "text": "OK" }`

### c) Voice Data (Audio, Speaker Verification, Commands)
- **Location:** `data/voice/`, `data/voice_signatures/`, `data/voice/manual_samples/`
- **Format:** `.wav`, `.mp3` + metadata in `.json`
- **Recommended structure:**
  - `data/voice/manual_samples/username/` (audio samples per user)
  - `data/voice_signatures/user1.json` (speaker embedding, labels)
  - Metadata: `{ "transcript": "Turn on the lights", "intent": "activate_lights" }`

---

## 2. Manual Training Pipeline (Step-by-Step)

### Step 1: Data Preparation
- Organize data in the correct folders and subfolders by type and category.
- Use consistent file naming: `YYYYMMDD_description.ext` or `user_label.ext`.
- For text, ensure UTF-8 encoding and escape problematic characters.
- For images, prefer PNG/JPG, 256x256 or higher, clear and labeled.
- For audio, use 16kHz mono WAV for best compatibility.
- Document the source and quality of each dataset in a README inside the folder.

### Step 2: Data Validation
- Run `scripts/validate_dependencies.py` to check all Python and system dependencies.
- Use or create scripts in `scripts/` to check:
  - File format and encoding
  - Duplicates and missing values
  - Consistency between data and metadata
  - For images: check for corrupt files, correct dimensions
  - For audio: check duration, silence, clipping
- Example validation script for text:
```python
import json
with open('data/learning/manual_training.jsonl') as f:
    for i, line in enumerate(f, 1):
        try:
            item = json.loads(line)
            assert 'prompt' in item and 'response' in item
        except Exception as e:
            print(f"Error in line {i}: {e}")
```

### Step 3: Manual Ingestion into Neural Memory
- Use or create `scripts/manual_ingest.py` to import data into ChromaDB:
```python
from src.core.intelligence.neural_memory import neural_memory
import json
with open('data/learning/manual_training.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        neural_memory.store_interaction(item['prompt'], item['response'], metadata=item.get('tags', {}))
```
- For images and audio, use or adapt ingestion scripts in `scripts/` or modules in `src/core/intelligence/`.
- After ingestion, check logs in `data/logs/` for errors or warnings.

### Step 4: Local Model Training (Optional/Advanced)
- For fine-tuning language models:
  - Prepare a dataset in HuggingFace format (`.jsonl`, `.csv`)
  - Use `scripts/train_local_model.py` (create if needed) with HuggingFace Transformers or PyTorch Lightning
  - Example command:
    ```bash
    python scripts/train_local_model.py --data data/learning/manual_training.jsonl --epochs 3 --model qwen2.5:7b
    ```
- For vision models (YOLO, OCR):
  - Organize images and labels as required by Ultralytics YOLO or PaddleOCR
  - Use or adapt scripts in `scripts/optimization/` or `src/core/vision/`
- For voice models:
  - Use `data/voice/` and `data/voice_signatures/` as input for speaker adaptation or command recognition

### Step 5: Testing and Validation
- Run tests in `tests/` to validate learning and integration:
  - `tests/test_brain.py` (language understanding)
  - `tests/test_memory.py` (neural memory)
  - `tests/test_face_recognition.py` (vision)
  - `tests/test_vision.py` (OCR/UI)
  - `tests/test_mic.py` (audio)
- Add new test cases for your manual data if possible.
- Review logs in `data/logs/` and outputs in `data/exports/`.

---

## 3. Best Practices for JARVIS Training
- Always back up all data and models before training or ingestion.
- Document each training session: date, goal, data used, scripts run, results.
- Use user feedback (from `data/learning/feedbacks.jsonl` or interface) to refine prompts and responses.
- Prefer real, diverse, and recent data for better generalization.
- Avoid overfitting: do not repeat the same prompt/response pairs excessively.
- For sensitive data, anonymize or mask personal information.
- Use version control (Git) for scripts and data recipes.

---

## 4. Automation, Feedback Loop & Integration
- Automate ingestion and validation with scripts in `scripts/` and scheduled tasks.
- Integrate feedback from users via the HUD, dashboard, or logs:
  - Example: User corrects a response → feedback is logged → script ingests correction into memory
- Use `data/logs/` and `data/exports/` to monitor the impact of manual training.
- For advanced users: implement a feedback loop where the system suggests improvements based on user corrections.
- Consider using the `src/core/learning/` and `src/core/intelligence/` modules for custom pipelines.

---

## 5. Troubleshooting & Tips
- If ingestion fails, check for:
  - File encoding issues (use UTF-8)
  - Duplicated IDs or missing required fields
  - Corrupt or unsupported image/audio files
  - ChromaDB or model loading errors (see logs)
- If model performance drops after training:
  - Revert to previous backup
  - Check for data quality issues or overfitting
  - Retrain with more diverse data
- For large datasets, split ingestion into batches and monitor memory usage.
- Use the `scripts/auto_healer.py` for automated repair of common issues.

---

## 6. References & Further Reading
- [HuggingFace Documentation](https://huggingface.co/docs/transformers/training)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ultralytics YOLO Docs](https://docs.ultralytics.com/)
- [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [JARVIS Source Code: src/core/intelligence/](../../src/core/intelligence/)
- [JARVIS Source Code: src/core/learning/](../../src/core/learning/)

---

*This guide is continuously evolving. Expand it as new training routines, data types, and modules are added to the JARVIS project.*
