# JARVIS SINGULARITY - Architecture Documentation

## Vision Statement

JARVIS Singularity represents the evolution of the JARVIS AI assistant into a **100% local, privacy-focused, system-integrated AI** with human-like sensory capabilities and deep OS control.

## Core Principles

1. **Privacy First** - 100% local processing (Ollama/Llama3)
2. **Total Control** - Deep Windows integration (God Mode)
3. **Dual Interface** - HUD Overlay + Control Dashboard
4. **Biometric Security** - FaceID authentication
5. **Sensory Capabilities** - Vision, Audio, Screen Analysis

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   JARVIS SINGULARITY                        │
│                                                             │
│  ┌────────────────┐         ┌────────────────┐            │
│  │  HUD Overlay   │ ←──→   │   Dashboard    │            │
│  │  (Transparent) │         │  (Full Panel)  │            │
│  └────────────────┘         └────────────────┘            │
│           ↑                          ↑                     │
│           └──────────┬───────────────┘                     │
│                      │                                     │
│           ┌──────────▼──────────┐                         │
│           │   Window Manager    │                         │
│           └──────────┬──────────┘                         │
│                      │                                     │
│      ┌───────────────┴───────────────┐                   │
│      │                                │                   │
│ ┌────▼─────┐                    ┌────▼─────┐            │
│ │  Vision  │                    │  System  │            │
│ │  System  │                    │   God    │            │
│ │ (Omni-   │                    │   Mode   │            │
│ │ Vision)  │                    │          │            │
│ └──────────┘                    └──────────┘            │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## Component Documentation

### 1. Window Manager (`src/interface/window_manager.py`)

**Purpose:** Central controller for dual interface system.

#### Interface Modes

```python
class InterfaceMode(Enum):
    HUD_OVERLAY = "hud"      # Transparent overlay
    DASHBOARD = "dashboard"  # Full control panel
    HIDDEN = "hidden"        # All hidden
```

#### Features

**Mode Switching:**
- Seamless transition between modes
- Lazy loading of interfaces
- Automatic state management

**System Tray:**
- Quick mode switching menu
- Double-click toggle
- Status tooltips
- Exit option

**Keyboard Shortcuts:**
- `Ctrl+Shift+J` - Toggle Dashboard
- `Ctrl+Shift+H` - Toggle HUD
- `Ctrl+Shift+X` - Hide All

#### Usage

```python
from interface.window_manager import get_window_manager, InterfaceMode
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
wm = get_window_manager(app)

# Start in HUD mode
wm.switch_mode(InterfaceMode.HUD_OVERLAY)

# Switch to dashboard
wm.switch_mode(InterfaceMode.DASHBOARD)

# Update status
wm.update_status("ai_status", "Processing...")

# Show notification
wm.show_notification("JARVIS", "Task complete")
```

#### Signals

```python
mode_changed = pyqtSignal(InterfaceMode)
status_update = pyqtSignal(str, str)  # (type, message)
```

---

### 2. Vision System (`src/core/vision_system.py`)

**Purpose:** Omni-Vision capabilities with biometric security.

#### Capabilities

**Screen Capture (mss):**
```python
# Ultra-fast screen capture
screenshot = vision.capture_screen(monitor=1)
# ~0.01s latency
```

**FaceID Authentication:**
```python
# Start monitoring
vision.start_monitoring()

# Check authorization
if vision.is_authorized_user_present():
    execute_command()
    
# Register new face
vision.register_new_face("admin", "photo.jpg")
```

**OCR Text Extraction:**
```python
# Analyze screen with OCR
context = vision.analyze_screen(include_ocr=True)
print(context.screen_text)
```

**Object Detection (YOLO):**
```python
# Detect objects/UI elements
context = vision.analyze_screen(include_objects=True)
for obj in context.detected_objects:
    print(f"{obj['class']}: {obj['confidence']}")
```

#### VisionContext Data Class

```python
@dataclass
class VisionContext:
    timestamp: datetime
    screen_text: Optional[str]
    detected_objects: Optional[List[Dict]]
    face_detected: bool
    authorized_user: bool
    active_window: Optional[str]
    screenshot_path: Optional[Path]
```

#### Security Model

1. **FaceID Required** - Commands only processed from authorized faces
2. **Continuous Monitoring** - Background thread checks every second
3. **Audit Trail** - All vision operations logged
4. **Face Database** - Authorized faces stored in `data/faces/`

#### Performance

- Screen Capture: ~10ms (mss)
- Face Recognition: ~100ms (hog model)
- OCR: ~2-5s (first run, then cached)
- YOLO Detection: ~500ms (CPU), ~50ms (GPU)

---

### 3. System Integrator (`src/core/system_integrator.py`)

**Purpose:** God Mode Windows control via native APIs.

#### Capabilities

**1. Per-Application Volume Control**

```python
si = get_system_integrator()

# Set volume (0.0 to 1.0)
si.set_app_volume("chrome.exe", 0.5)

# Mute/Unmute
si.mute_app("spotify.exe")
si.unmute_app("discord.exe")

# Get current volume
volume = si.get_app_volume("chrome.exe")
```

**2. Process Management**

```python
# Kill process
si.kill_process("notepad.exe")

# Force kill (protected process)
si.kill_process("explorer.exe", force=True)

# Get process info
processes = si.get_process_info("chrome")
for proc in processes:
    print(f"{proc.name} - CPU: {proc.cpu_percent}%")
    print(f"Memory: {proc.memory_mb:.1f}MB")

# Check if running
if si.is_process_running("steam.exe"):
    print("Steam is running")
```

**3. Window Manipulation**

```python
# Get active window
title = si.get_active_window_title()

# Focus window
si.focus_window("Chrome")

# Minimize window
si.minimize_window("Notepad")

# Close window
si.close_window("Calculator")

# Get window info
window = si.get_window_by_title("Chrome")
print(f"PID: {window.pid}")
print(f"Minimized: {window.is_minimized}")
```

**4. System Information**

```python
info = si.get_system_info()

# Returns:
{
    'cpu': {
        'percent': 45.2,
        'count': 8,
        'freq': 3600.0
    },
    'memory': {
        'total_gb': 16.0,
        'available_gb': 8.5,
        'percent': 46.9
    },
    'disk': {
        'total_gb': 500.0,
        'free_gb': 150.0,
        'percent': 70.0
    },
    'network': {...},
    'battery': {...}  # If laptop
}
```

**5. Shell Command Execution**

```python
success, output = si.execute_shell_command(
    "systeminfo",
    timeout=30
)

if success:
    print(output)
```

#### Security Features

**Audit Logging:**
All privileged operations logged to `data/logs/god_mode_audit.log`:
```
[2026-02-06T12:00:00] kill_process | SUCCESS | chrome.exe (PID: 1234)
[2026-02-06T12:00:01] set_volume | SUCCESS | spotify.exe -> 50%
[2026-02-06T12:00:02] close_window | SUCCESS | Notepad
```

**Protected Processes:**
Cannot kill system-critical processes without `force=True`:
- system
- wininit.exe
- csrss.exe
- services.exe
- lsass.exe
- winlogon.exe
- explorer.exe
- smss.exe

**Operation Validation:**
- Volume range checks (0.0-1.0)
- Process existence verification
- Window title validation
- Command timeout enforcement

#### Platform Support

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| Volume Control | ✅ | ❌ | ❌ |
| Process Management | ✅ | ✅* | ✅* |
| Window Control | ✅ | ❌ | ❌ |
| System Info | ✅ | ✅ | ✅ |
| Shell Commands | ✅ | ✅ | ✅ |

*Limited functionality via psutil

---

## Integration Examples

### Example 1: FaceID-Protected Command

```python
from core.vision_system import get_vision_system
from core.system_integrator import get_system_integrator

vision = get_vision_system()
si = get_system_integrator()

# Start face monitoring
vision.start_monitoring()

def execute_command(command: str):
    # Check authorization
    if not vision.is_authorized_user_present():
        print("⚠️ Unauthorized user - command denied")
        return
        
    # Execute command
    if "mute chrome" in command.lower():
        si.mute_app("chrome.exe")
        print("✅ Chrome muted")
```

### Example 2: Screen Context for AI

```python
from core.vision_system import get_vision_system

vision = get_vision_system()

def get_screen_context():
    # Analyze screen
    context = vision.analyze_screen(
        include_ocr=True,
        include_objects=True
    )
    
    # Build context for AI
    prompt = f"""
Current Screen Context:
- Active Window: {context.active_window}
- Visible Text: {context.screen_text[:500]}...
- Detected Objects: {len(context.detected_objects)}
- User Authorized: {context.authorized_user}

Based on this, answer: {user_question}
"""
    
    return prompt
```

### Example 3: Dual Interface Workflow

```python
from interface.window_manager import get_window_manager, InterfaceMode
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
wm = get_window_manager(app)

# Register mode switch callback
def on_mode_switch(mode: InterfaceMode):
    if mode == InterfaceMode.DASHBOARD:
        print("Dashboard active - configuration mode")
    elif mode == InterfaceMode.HUD_OVERLAY:
        print("HUD active - monitoring mode")

wm.on_mode_switch = on_mode_switch

# Start in HUD mode
wm.switch_mode(InterfaceMode.HUD_OVERLAY)

# Get HUD and update
hud = wm.get_hud()
hud.update_state("listening")
hud.show_response("Waiting for command...")

# User presses Ctrl+Shift+J → Auto-switches to dashboard
```

---

## Configuration

### Directory Structure

```
PROJECT_JARVIS_5.0/
├── data/
│   ├── faces/              # Authorized face images
│   │   ├── admin.jpg
│   │   └── user.jpg
│   ├── screenshots/        # Captured screenshots
│   ├── models/            # AI models (YOLO, etc.)
│   └── logs/
│       └── god_mode_audit.log  # Audit log
├── src/
│   ├── interface/
│   │   ├── window_manager.py    # Dual interface controller
│   │   ├── modern_hud.py        # HUD overlay
│   │   └── control_dashboard.py # Control panel (TODO)
│   └── core/
│       ├── vision_system.py     # Omni-Vision
│       └── system_integrator.py # God Mode
└── requirements_singularity.txt
```

### Environment Variables

```bash
# Optional GPU acceleration
CUDA_VISIBLE_DEVICES=0

# Face recognition model
JARVIS_FACE_MODEL=hog  # or 'cnn' for GPU

# Audio device
JARVIS_AUDIO_DEVICE=0
```

---

## Performance Optimization

### Vision System

**CPU Mode (Default):**
- Face Detection: hog model (~100ms)
- OCR: EasyOCR CPU (~2-5s first run)
- YOLO: CPU inference (~500ms)

**GPU Mode (Recommended):**
- Face Detection: cnn model (~50ms)
- OCR: EasyOCR GPU (~500ms)
- YOLO: GPU inference (~50ms)

### System Integrator

**Audio Control:**
- Operation time: ~10ms
- Cache: 2-second TTL for session list

**Process Management:**
- List all processes: ~50ms
- Kill process: ~20ms
- Get process info: ~5ms per process

**Window Control:**
- Get active window: ~5ms
- Focus window: ~20ms
- Minimize/Close: ~15ms

---

## Troubleshooting

### Vision System

**Problem:** Face recognition too slow
```python
# Switch to HOG model
vision.face_detection_model = 'hog'
```

**Problem:** OCR not working
```bash
# Install EasyOCR dependencies
pip install easyocr
# May require additional system libraries
```

**Problem:** Screen capture fails
```bash
# Check mss installation
pip install mss==9.0.1
```

### System Integrator

**Problem:** Volume control not working
```bash
# Install pycaw
pip install pycaw
# May require comtypes
pip install comtypes
```

**Problem:** Window control fails
```bash
# Install pywin32
pip install pywin32==306
# Run post-install
python Scripts/pywin32_postinstall.py -install
```

**Problem:** Access denied errors
- Run as Administrator for system-level operations
- Check protected process list
- Review audit log for details

---

## Security Considerations

### FaceID Authentication

1. **Enrollment:** Only add trusted users to `data/faces/`
2. **Verification:** Check `is_authorized_user_present()` before sensitive operations
3. **Monitoring:** Face checks every ~1 second during monitoring
4. **Timeout:** Authorization expires after 5 seconds without face

### God Mode Operations

1. **Audit Log:** Review `god_mode_audit.log` regularly
2. **Protected Processes:** Never force-kill system processes
3. **Command Validation:** Always validate user commands
4. **Timeout:** Set appropriate timeouts for shell commands
5. **Permissions:** Some operations require Administrator rights

### Privacy

1. **Local Processing:** No data sent to cloud
2. **Screenshot Storage:** Automatic cleanup recommended
3. **Face Database:** Encrypted storage recommended
4. **Audit Logs:** Rotate and archive regularly

---

## Future Enhancements

### Phase 2 (Control Dashboard)

- [ ] Full PyQt6 admin panel
- [ ] Real-time configuration editing
- [ ] Hardware monitoring graphs (pyqtgraph)
- [ ] Memory browser (ChromaDB)
- [ ] Log viewer with filtering
- [ ] System metrics dashboard

### Phase 3 (Enhanced Audio)

- [ ] Faster-Whisper integration
- [ ] Silero-VAD voice activity detection
- [ ] Speaker verification system
- [ ] Voice signature storage
- [ ] Multi-speaker support

### Phase 4 (Advanced Features)

- [ ] Multi-monitor workspace awareness
- [ ] Application context understanding
- [ ] Proactive suggestions
- [ ] Workflow automation
- [ ] Screen recording for analysis

---

## API Reference

See individual module docstrings for complete API documentation:

```bash
# View documentation
python -m pydoc src.interface.window_manager
python -m pydoc src.core.vision_system
python -m pydoc src.core.system_integrator
```

---

## Support

For issues, feature requests, or contributions:

1. Check troubleshooting section
2. Review audit logs
3. Test modules independently
4. Report with system information

---

**JARVIS Singularity** - The future of AI assistants is local, private, and powerful.
