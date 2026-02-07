# 🦎 JARVIS Chameleon Installer Documentation

## Overview

The **Chameleon Adaptive Installer** is an intelligent installation system that automatically detects your hardware capabilities and installs the appropriate version of JARVIS with the correct dependencies for your machine.

### Key Features

- ✅ **Automatic Hardware Detection** - Detects RAM, GPU, VRAM, CUDA without user input
- ✅ **Three Profiles** - LITE (CPU), HYBRID (Light GPU), ULTIMATE (Full ML)
- ✅ **Zero-Crash Guarantee** - Mock fallbacks prevent import errors
- ✅ **One-Click Installation** - No manual configuration needed
- ✅ **Graceful Degradation** - Works on ANY hardware

---

## Hardware Profiles

### LITE Profile (CPU-Only)
**Target Hardware:**
- Ultrabooks, laptops with integrated graphics
- No NVIDIA GPU or < 4GB VRAM
- 8GB+ RAM recommended

**Installed Features:**
- 45 packages (CPU-only)
- PyQt6 interface (HUD + Dashboard)
- Voice recognition (CPU)
- Face recognition (CPU)
- Vision (OpenCV, CPU-based)
- **NO** PyTorch
- **NO** ML training

**Use Case:** Daily assistant, voice commands, basic automation

---

### HYBRID Profile (Light GPU)
**Target Hardware:**
- GTX 1050 Ti, GTX 1650, RTX 2060
- 4-6GB VRAM
- 16GB+ RAM recommended

**Installed Features:**
- 58 packages (with GPU support)
- Everything from LITE +
- PyTorch with CUDA
- 4-bit quantization (bitsandbytes)
- GPU-accelerated vision (YOLO)
- Light training capability

**Use Case:** Inference + light model fine-tuning, GPU-accelerated tasks

---

### ULTIMATE Profile (Full ML Stack)
**Target Hardware:**
- RTX 3060+, RTX 4000 series, A100
- 8GB+ VRAM (12GB+ recommended)
- 32GB+ RAM recommended

**Installed Features:**
- 70 packages (full ML stack)
- Everything from HYBRID +
- Unsloth (2x faster training)
- PEFT/LoRA (parameter-efficient fine-tuning)
- DeepSpeed (distributed training)
- TRL (RLHF/DPO)
- Full model training capability

**Use Case:** Heavy ML training, research, model development

---

## Installation

### Windows (Recommended)

Simply run:
```bash
INICIAR_ADAPTATIVO.bat
```

This will:
1. Check Python installation
2. Run hardware detection
3. Install appropriate dependencies
4. Launch JARVIS

### Cross-Platform

```bash
python setup_adaptive.py
python main_singularity_integrated.py
```

---

## How It Works

### Step 1: Hardware Detection

The installer uses pure Python (no external dependencies) to detect:

**RAM Detection (ctypes):**
- Windows: `kernel32.GlobalMemoryStatusEx()`
- Linux: Read `/proc/meminfo`
- macOS: `sysctl hw.memsize`

**GPU Detection (nvidia-smi):**
```bash
nvidia-smi --query-gpu=name,memory.total,driver_version
```

If nvidia-smi is not found, assumes no NVIDIA GPU (LITE profile).

### Step 2: Profile Determination

```python
def determine_profile(ram_gb, gpu_info):
    if not gpu_info['available'] or gpu_info['vram_gb'] < 4:
        return "LITE"
    elif gpu_info['vram_gb'] < 8:
        return "HYBRID"
    else:
        return "ULTIMATE"
```

### Step 3: Dependency Installation

Installs the appropriate requirements file:
- **LITE**: `requirements_lite.txt`
- **HYBRID**: `requirements_hybrid.txt`
- **ULTIMATE**: `requirements_ultimate.txt`

**Critical:** All profiles enforce `numpy<2.0.0` for compatibility.

### Step 4: Config Generation

Creates `config/system_profile.json`:

```json
{
  "version": "1.0.0",
  "profile": "ULTIMATE",
  "hardware": {
    "os": "Windows",
    "cpu_cores": 16,
    "ram_gb": 32.0,
    "gpu_available": true,
    "gpu_name": "NVIDIA GeForce RTX 3080",
    "vram_gb": 10.0,
    "cuda_version": "12.1"
  },
  "features": {
    "training_enabled": true,
    "full_ml_stack": true,
    "gpu_acceleration": true
  }
}
```

---

## Safe Import System

### The Problem

Traditional imports crash on missing libraries:
```python
import unsloth  # ImportError on LITE profile!
```

### The Solution

Use the dependency manager:
```python
from src.core.dependency_manager import safe_import

unsloth = safe_import('unsloth', strategy='PROFILE_DEPENDENT')
model = unsloth.FastLanguageModel.from_pretrained("llama-3-8b")
# LITE: Returns mock, logs warning, NO CRASH
# ULTIMATE: Real training
```

### Import Strategies

**REQUIRED:**
```python
psutil = safe_import('psutil', strategy='REQUIRED')
# Must be available or raises ImportError
```

**OPTIONAL:**
```python
torch = safe_import('torch', strategy='OPTIONAL')
# Returns mock if unavailable
```

**PROFILE_DEPENDENT:**
```python
unsloth = safe_import('unsloth', strategy='PROFILE_DEPENDENT')
# Checks system_profile.json before importing
```

### Mock Objects

Mock objects accept any method call and return themselves:

```python
# On LITE profile (no unsloth installed)
unsloth = safe_import('unsloth')  # Returns MockObject

model = unsloth.FastLanguageModel.from_pretrained("model")
# Logs: "⚠️ Using mock for 'unsloth': Hardware insufficient"
# Returns: MockObject (no crash!)

result = model.train()  # Returns MockObject
print(result)  # <MockObject for 'unsloth' (Hardware insufficient)>
```

---

## Package Lists

### All Profiles Include

**Interface:**
- PyQt6, PyQt6-Qt6, pyqtgraph

**System:**
- psutil, pywin32, pyautogui, keyboard, mouse

**Vision (CPU):**
- opencv-python, Pillow, mss, face-recognition, dlib

**Audio:**
- pyaudio, sounddevice, soundfile, librosa, pyttsx3, gtts

**Utilities:**
- requests, aiohttp, python-dotenv, PyYAML, jsonlines, pandas

**Database:**
- chromadb

**Logging:**
- colorama, tqdm

### HYBRID Adds

**ML Core:**
- torch, torchaudio, torchvision
- bitsandbytes (4-bit quantization)
- transformers, accelerate, sentencepiece

**Vision (GPU):**
- ultralytics (YOLO)

**Audio (Advanced):**
- edge-tts

**Training:**
- datasets, evaluate, scikit-learn

### ULTIMATE Adds

**Advanced Training:**
- unsloth (2x faster fine-tuning)
- peft (LoRA/QLoRA)
- trl (RLHF/DPO)
- deepspeed (distributed)
- xformers, optimum, flash-attn

**Voice Biometrics:**
- resemblyzer

**Advanced ML:**
- xgboost, lightgbm, prophet, statsmodels

**Monitoring:**
- wandb, tensorboard

---

## Troubleshooting

### "Python not found"

**Solution:** Install Python 3.8+ from https://www.python.org/
- Check "Add Python to PATH" during installation
- Restart terminal after installation

### "nvidia-smi not found"

**This is normal if:**
- You don't have an NVIDIA GPU
- NVIDIA drivers not installed

**Result:** Installer will use LITE profile (CPU-only)

### "Some packages failed to install"

**Common causes:**
- Slow internet connection
- Package not available for your OS/Python version

**Solution:** Check `data/logs/singularity_setup.log` for details

### Wrong profile detected

**Check:**
```bash
python setup_adaptive.py
```

**Manual override:**
Edit `config/system_profile.json` to change profile, then:
```bash
pip install -r requirements_[lite|hybrid|ultimate].txt
```

### Imports still failing

**Verify safe_import usage:**
```python
from src.core.dependency_manager import safe_import, is_available

torch = safe_import('torch', strategy='PROFILE_DEPENDENT')
if is_available('torch'):
    # Use real torch
else:
    # Use alternative
```

---

## Developer Guide

### Adding New Dependencies

**For all profiles:**
Add to `requirements_lite.txt`, `requirements_hybrid.txt`, AND `requirements_ultimate.txt`

**For GPU-only:**
Add to `requirements_hybrid.txt` and `requirements_ultimate.txt`

**For training-only:**
Add to `requirements_ultimate.txt` only

### Profile-Aware Code

```python
from src.core.dependency_manager import get_profile, is_available

profile = get_profile()  # "LITE", "HYBRID", or "ULTIMATE"

if profile == "ULTIMATE":
    # Use advanced features
    from src.learning.trainer import LocalTrainer
    trainer = LocalTrainer()
    trainer.train()
elif profile == "HYBRID":
    # Use light features
    from src.learning.inference import run_inference
    run_inference()
else:
    # Use basic features
    print("Training not available on this hardware")
```

### Testing on Different Profiles

**Simulate LITE:**
```bash
# Temporarily rename config
mv config/system_profile.json config/system_profile.json.bak

# Create LITE config
echo '{"profile": "LITE", "features": {"training_enabled": false}}' > config/system_profile.json

# Test
python main_singularity_integrated.py
```

**Restore:**
```bash
mv config/system_profile.json.bak config/system_profile.json
```

---

## Performance

### Hardware Detection

- RAM detection: ~10ms
- GPU detection: ~100-500ms (nvidia-smi call)
- Total detection: ~500ms

### Installation Time

- **LITE**: 5-10 minutes (45 packages)
- **HYBRID**: 10-20 minutes (58 packages)
- **ULTIMATE**: 20-40 minutes (70 packages)

*Depends on internet speed and CPU*

### Runtime Overhead

- Safe import check: ~1ms per import
- Mock object call: <0.1ms
- **Total overhead: Negligible**

---

## FAQ

**Q: Can I manually choose a profile?**
A: Yes, edit `config/system_profile.json` and change the `profile` field.

**Q: Will LITE profile work for gaming?**
A: LITE is for AI assistance. The HUD/Dashboard will work, but ML features will be limited.

**Q: Can I upgrade from LITE to ULTIMATE later?**
A: Yes! Just run `python setup_adaptive.py` again after upgrading your GPU.

**Q: Does this work on Linux/Mac?**
A: Yes! Hardware detection is cross-platform. Some packages may differ.

**Q: Why numpy<2.0.0?**
A: Critical compatibility requirement for PyTorch, Whisper, and many ML libraries.

**Q: What if I have multiple GPUs?**
A: The installer detects the first GPU. Profile is based on weakest link (lowest VRAM).

---

## Summary

The Chameleon Installer ensures JARVIS runs **everywhere**:

| Hardware | Profile | Time | Features |
|----------|---------|------|----------|
| Ultrabook | LITE | 5-10min | Voice, Vision, HUD |
| Gaming PC | HYBRID | 10-20min | + GPU, Light Training |
| Workstation | ULTIMATE | 20-40min | + Full ML Stack |

**One command. Zero configuration. Maximum compatibility.** 🦎

---

*For support, see GitHub issues or documentation.*