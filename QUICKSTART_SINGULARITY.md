# JARVIS SINGULARITY - Quick Start Guide

## 🚀 Installation (Zero-Error Guarantee)

### Step 1: Auto-Install (Recommended)

Run the intelligent auto-installer:

```bash
python setup_singularity_auto.py
```

The installer will:
- ✅ Check Python version (3.8+ required, 3.11 recommended)
- ✅ Detect GPU capabilities (CUDA)
- ✅ Create directory structure
- ✅ Install all 52 dependencies automatically
- ✅ Generate configuration files
- ✅ Validate installation
- ✅ Provide next steps

Installation time: ~5-15 minutes (depending on internet speed)

### Step 2: Manual Configuration (Optional)

The auto-installer generates:
- `config/singularity_config.json` - Main configuration
- `config.yaml` - Legacy compatibility

Edit if needed, but defaults work great!

### Step 3: Add Authorized Faces (Optional)

For FaceID authentication:

```bash
# Place face images in data/faces/
# Format: username.jpg (e.g., admin.jpg, john.jpg)
# Requirements: Clear front-facing photo, good lighting, JPEG format
```

Or capture from webcam:
```bash
python -c "import cv2; cam = cv2.VideoCapture(0); ret, frame = cam.read(); cv2.imwrite('data/faces/admin.jpg', frame); cam.release(); print('✅ Face captured!')"
```

---

## 🎮 Running JARVIS

### Standard Mode (Recommended)

```bash
python main_singularity_integrated.py
```

This launches the complete integrated system with:
- Window Manager (dual interface)
- Vision System (FaceID + OCR + YOLO)
- Enhanced Audio (Faster-Whisper + VAD + Speaker Verification)
- System Integrator (God Mode)

### Legacy Mode

```bash
python main.py
```

---

## ⌨️ Keyboard Shortcuts

Global shortcuts (work anywhere):

- **Ctrl+Shift+J** - Toggle Control Dashboard
- **Ctrl+Shift+H** - Toggle HUD Overlay
- **Ctrl+Shift+X** - Hide All Interfaces

HUD shortcuts:
- **Ctrl+H** - Toggle HUD visibility
- **Escape** - Close current window

---

## 🎛️ Control Dashboard

The Control Dashboard provides full configuration and monitoring across 6 tabs:

### 1. 🧠 Brain (AI Configuration)
- Select LLM provider (Ollama, OpenAI, Anthropic, Gemini, Groq)
- Configure model name and API keys
- Set temperature and max tokens
- Edit system prompt

### 2. 🎤 Voice (Audio Settings)
- Choose STT engine (faster-whisper recommended)
- Select model size (tiny/base/small/medium/large)
- Configure TTS engine and voice
- Enable/configure Voice Activity Detection (VAD)
- Manage speaker verification
- Enroll authorized voices

### 3. 👁️ Vision (Visual Systems)
- Enable/disable FaceID authentication
- Select face detection model (hog for CPU, cnn for GPU)
- Manage authorized faces (add/remove)
- Configure OCR (text extraction)
- Set YOLO object detection parameters
- Adjust confidence thresholds

### 4. 📋 Logs (Real-time Viewer)
- View system logs in real-time
- Filter by text or log level
- Auto-scroll option
- Clear logs function

### 5. ⚙️ System (Resource Monitor)
- Real-time CPU/RAM/Disk usage
- Process list with details
- Refresh processes on demand

### 6. 💾 Memory (Conversation History)
- Browse conversation history
- Clear memory
- Export conversations

---

## 📁 Directory Structure

```
PROJECT_JARVIS_5.0/
├── main_singularity_integrated.py  # Integrated entry point ⭐
├── main.py             # Legacy entry point
├── setup_singularity_auto.py       # Auto-installer ⭐
├── requirements.txt    # Dependencies
│
├── src/
│   ├── interface/
│   │   ├── window_manager.py       # Dual interface controller ⭐
│   │   ├── control_dashboard.py    # Admin panel ⭐
│   │   ├── modern_hud.py          # Modern HUD overlay
│   │   └── hud.py                 # HUD wrapper
│   │
│   └── core/
│       ├── vision_system.py        # FaceID + OCR + YOLO ⭐
│       ├── enhanced_audio.py       # Audio processing ⭐
│       ├── system_integrator.py    # God Mode controls ⭐
│       └── ...                     # Other modules
│
├── data/
│   ├── faces/                     # Authorized face images
│   ├── voice_signatures/          # Speaker embeddings
│   ├── screenshots/               # Captured screens
│   ├── logs/                      # System logs
│   └── audio/                     # Audio temp files
│
├── config/
│   └── singularity_config.json    # Main configuration
│
└── docs/
    ├── SINGULARITY_ARCHITECTURE.md # Technical docs
    └── ...

⭐ = New in Singularity Phase 2
```

---

## 🔒 Security Features

### FaceID Authentication
- Only authorized faces can execute commands
- Continuous monitoring (checks every ~1 second)
- Authorization expires 5 seconds after face leaves frame
- Stored in: `data/faces/username.jpg`

### Speaker Verification
- Voice signature-based authentication
- Cosine similarity matching
- Configurable threshold (default: 0.75)
- Stored in: `data/voice_signatures/username.npy`

### God Mode Audit Log
- All privileged operations logged
- Location: `data/logs/god_mode_audit.log`
- Protected processes cannot be killed without force flag

---

## 🎯 Features Overview

### Dual Interface System
- **HUD Overlay**: Transparent, minimal, always-on-top display
- **Control Dashboard**: Full admin panel with configuration
- **System Tray**: Quick access to all features
- **Seamless Switching**: Instant mode changes

### Omni-Vision
- **Screen Capture**: Ultra-low latency (mss, ~10ms)
- **FaceID**: Biometric authentication
- **OCR**: Text extraction from screen (EasyOCR)
- **YOLO**: Object and UI element detection
- **Multi-threaded**: Non-blocking operation

### Enhanced Audio
- **STT**: Faster-Whisper (local, fast, accurate)
- **VAD**: Silero voice activity detection
- **Speaker Verification**: Voice-based authentication
- **Real-time Pipeline**: Live audio processing
- **Model Sizes**: tiny → large (speed vs accuracy)

### God Mode (Windows)
- **Volume Control**: Per-application audio control
- **Process Management**: Kill, list, monitor processes
- **Window Control**: Focus, minimize, close windows
- **System Info**: CPU, RAM, disk, network stats
- **Shell Commands**: Execute with timeout protection

---

## ⚡ Performance

### Typical Performance (CPU mode):
- Screen Capture: ~10ms
- Face Recognition: ~100ms
- OCR: ~2-5s (first run, then cached)
- YOLO Detection: ~500ms
- STT Transcription: ~1-3s (base model)
- VAD Check: ~10ms
- Speaker Verification: ~50ms

### With GPU (CUDA):
- Face Recognition: ~50ms
- YOLO Detection: ~50ms
- STT Transcription: ~0.5-1s

---

## 🐛 Troubleshooting

### Installation Issues

**Problem**: Dependencies fail to install
```bash
# Solution: Update pip and try again
python -m pip install --upgrade pip
python setup_singularity_auto.py
```

**Problem**: PyAudio installation fails (Windows)
```bash
# Solution: Install from wheel
pip install pipwin
pipwin install pyaudio
```

**Problem**: Torch/CUDA issues
```bash
# Solution: Install CPU version explicitly
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
```

### Runtime Issues

**Problem**: "No module named 'interface'"
```bash
# Solution: Run from project root
cd /path/to/PROJECT_JARVIS_5.0
python main_singularity_integrated.py
```

**Problem**: Qt warnings about DPI/screen
```
# These are already suppressed in code, but if you see them:
# They're harmless and don't affect functionality
```

**Problem**: Vision system errors
```bash
# Check if faces directory exists and has images
ls data/faces/
# Should show .jpg files

# Check if face_recognition is installed
python -c "import face_recognition; print('✅ OK')"
```

**Problem**: Audio not working
```bash
# Check microphone permissions
# Windows: Settings → Privacy → Microphone
# Linux: Check ALSA/PulseAudio configuration
```

---

## 📊 System Requirements

### Minimum:
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8+
- **RAM**: 4GB
- **Disk**: 2GB free space
- **CPU**: Modern dual-core

### Recommended:
- **OS**: Windows 11
- **Python**: 3.11
- **RAM**: 8GB+
- **Disk**: 5GB+ free space
- **CPU**: Quad-core or better
- **GPU**: NVIDIA with CUDA (optional but faster)

---

## 🔄 Updates & Maintenance

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Clear Logs
```bash
# Logs are in data/logs/
# Manually delete old .log files or use dashboard
```

### Reset Configuration
```bash
# Delete and regenerate
rm config/singularity_config.json
python setup_singularity_auto.py
```

---

## 📚 Documentation

- **Architecture**: `docs/SINGULARITY_ARCHITECTURE.md`
- **API Reference**: See module docstrings
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **Changelog**: `CHANGELOG.md`

---

## 🆘 Support

For issues:
1. Check logs: `data/logs/jarvis_singularity.log`
2. Check installation log: `singularity_setup.log`
3. Review troubleshooting section above
4. Check GitHub Issues

---

## 🎉 Quick Test

After installation, test the system:

```python
# Test Vision System
python src/core/vision_system.py

# Test Audio System
python src/core/enhanced_audio.py

# Test System Integrator
python src/core/system_integrator.py

# Test Window Manager
python src/interface/window_manager.py

# Test Control Dashboard
python src/interface/control_dashboard.py
```

All modules have built-in testing and will run demonstrations.

---

## ✅ Success Checklist

After setup, verify:
- [ ] `python setup_singularity_auto.py` completed successfully
- [ ] No errors in `singularity_setup.log`
- [ ] Config file exists: `config/singularity_config.json`
- [ ] Directories created: `data/faces/`, `data/logs/`, etc.
- [ ] At least one face added to `data/faces/` (optional)
- [ ] Can run: `python main_singularity_integrated.py`
- [ ] HUD appears on screen
- [ ] `Ctrl+Shift+J` opens Control Dashboard
- [ ] All dashboard tabs load without errors

---

**🚀 You're ready to use JARVIS Singularity!**

Start the system and explore the features. The auto-installer has configured everything for optimal performance on your system.
