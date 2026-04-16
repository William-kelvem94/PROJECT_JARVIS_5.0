"""
JARVIS 5.0 — Auto-Setup / Self-Configuration Script
====================================================
Run automatically by start-jarvis.bat before launching the agent.
Responsabilities:
  1. Install / upgrade all required packages (with adaptive fallbacks for heavy ones).
  2. Download pre-built dlib wheel so face_recognition works without cmake on Windows.
  3. Create all required data directories.
  4. Run playwright chromium install if not present.
  5. Patch third-party compatibility issues (e.g. webrtcvad / pkg_resources on Py 3.12+).
  6. Validate imports and print a ✅/❌ capability report.

Exit code 0 = ready to launch.  Non-zero = critical dependency missing.
"""

import sys
import os
import subprocess
import importlib
import importlib.util
import platform
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent   # PROJECT_JARVIS_5.0/backend
VENV_PYTHON = sys.executable
PIP = [VENV_PYTHON, "-m", "pip", "install", "--quiet", "--upgrade"]

# ── Colour helpers ─────────────────────────────────────────────────────────────
def green(s):  return f"\033[92m{s}\033[0m"
def yellow(s): return f"\033[93m{s}\033[0m"
def red(s):    return f"\033[91m{s}\033[0m"
def cyan(s):   return f"\033[96m{s}\033[0m"
def bold(s):   return f"\033[1m{s}\033[0m"

def ok(msg):   print(f"  {green('✅')} {msg}")
def warn(msg): print(f"  {yellow('⚠️')}  {msg}")
def fail(msg): print(f"  {red('❌')} {msg}")
def info(msg): print(f"  {cyan('ℹ️')}  {msg}")


# ── Install helper ─────────────────────────────────────────────────────────────
def pip_install(*packages: str, extra_index: str = None) -> bool:
    cmd = PIP + list(packages)
    if extra_index:
        cmd += ["--extra-index-url", extra_index]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-600:] if result.stderr else "")
    return result.returncode == 0


def is_importable(module: str) -> bool:
    spec = importlib.util.find_spec(module)
    return spec is not None


# ── 1. Core required packages ──────────────────────────────────────────────────
CORE_PACKAGES = [
    ("fastapi",           "fastapi"),
    ("uvicorn",           "uvicorn[standard]"),
    ("dotenv",            "python-dotenv"),
    ("psutil",            "psutil"),
    ("loguru",            "loguru"),
    ("aiohttp",           "aiohttp"),
    ("playwright",        "playwright"),
    ("mss",               "mss"),
    ("PIL",               "Pillow"),
]

# ── 2. Perception packages ─────────────────────────────────────────────────────
PERCEPTION_PACKAGES = [
    ("cv2",               "opencv-python",    "Face/Gesture Level C (presence + gestures)"),
    ("mediapipe",         "mediapipe",         "Face/Gesture Level C (presence + gestures)"),
    ("numpy",             "numpy",             "Numerical arrays"),
    ("openwakeword",      "openwakeword",      "Voice Level A (Hey Jarvis wake word)"),
    ("sounddevice",       "sounddevice",       "Audio input stream"),
    ("faster_whisper",    "faster-whisper",    "Voice Level C (offline transcription)"),
    ("resemblyzer",       "resemblyzer",       "Voice Level B (speaker identification)"),
]

# Heavy optional (not auto-installed — user must opt in)
HEAVY_OPTIONAL = [
    ("deepface",          "deepface tf-keras", "Face Level B (emotion detection, ~1 GB)"),
    ("face_recognition",  "face_recognition",  "Face Level A (identity, needs cmake+dlib)"),
]


def install_core():
    print(bold("\n[1/6] Core packages"))
    all_ok = True
    for mod, pkg in CORE_PACKAGES:
        if is_importable(mod):
            ok(f"{pkg} already installed")
        else:
            info(f"Installing {pkg}…")
            if pip_install(pkg):
                ok(f"{pkg} installed")
            else:
                fail(f"{pkg} FAILED")
                all_ok = False
    return all_ok


def install_perception():
    print(bold("\n[2/6] Perception packages"))
    for mod, pkg, desc in PERCEPTION_PACKAGES:
        if is_importable(mod):
            ok(f"{mod} ({desc})")
        else:
            info(f"Installing {pkg} — {desc}…")
            if pip_install(pkg):
                ok(f"{pkg} installed")
            else:
                warn(f"{pkg} install failed — perception level degraded")

    # Download openwakeword models if not present
    try:
        import openwakeword, os as _os
        models_dir = _os.path.join(_os.path.dirname(openwakeword.__file__), "resources", "models")
        onnx_files = [f for f in _os.listdir(models_dir) if f.endswith(".onnx")] if _os.path.isdir(models_dir) else []
        # Need more than just embedding/melspectrogram
        ww_models = [f for f in onnx_files if "embedding" not in f and "melspectrogram" not in f]
        if not ww_models:
            info("Downloading openWakeWord models (first time)…")
            openwakeword.utils.download_models()
            ok("openWakeWord models downloaded")
        else:
            ok(f"openWakeWord models present ({len(ww_models)} wake word model(s))")
    except Exception as e:
        warn(f"openWakeWord model download failed: {e}")

    # Download MediaPipe task model files for the new tasks API
    try:
        import urllib.request as _urlreq
        mp_models_dir = ROOT / "data" / "models"
        mp_models_dir.mkdir(parents=True, exist_ok=True)
        mp_model_urls = {
            "face_landmarker.task":      "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            "gesture_recognizer.task":   "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
            "pose_landmarker_lite.task": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        }
        missing = [n for n in mp_model_urls if not (mp_models_dir / n).exists()]
        if missing:
            info(f"Downloading {len(missing)} MediaPipe model file(s)…")
            failed_mp = 0
            for name, url in mp_model_urls.items():
                dest = mp_models_dir / name
                if dest.exists():
                    continue
                try:
                    _urlreq.urlretrieve(url, dest)
                    ok(f"  {name} ({dest.stat().st_size // 1024} KB)")
                except Exception as e:
                    warn(f"  {name} download failed: {e}")
                    failed_mp += 1
            if not failed_mp:
                ok("MediaPipe model files ready")
        else:
            ok(f"MediaPipe model files present ({len(mp_model_urls)} files)")
    except Exception as e:
        warn(f"MediaPipe model download failed: {e}")

    # Heavy optional: only install if user opted in via env flag JARVIS_FULL_PERCEPTION=1
    if os.getenv("JARVIS_FULL_PERCEPTION", "0") == "1":
        print(bold("\n  [Optional] Full perception (JARVIS_FULL_PERCEPTION=1 detected)"))
        for mod, pkg, desc in HEAVY_OPTIONAL:
            if is_importable(mod):
                ok(f"{mod} ({desc})")
            else:
                info(f"Installing {pkg} — {desc}…")
                if pip_install(pkg):
                    ok(f"{pkg} installed")
                else:
                    warn(f"{pkg} install failed — {desc}")
    else:
        warn("Set JARVIS_FULL_PERCEPTION=1 in env/.env to enable emotion detection and face identity")


def patch_compat():
    """Fix known third-party compatibility issues."""
    print(bold("\n[3/6] Compatibility patches"))

    # Patch webrtcvad for Python 3.12+ (pkg_resources removed from stdlib)
    webrtcvad_path = None
    for sp in sys.path:
        candidate = Path(sp) / "webrtcvad.py"
        if candidate.exists():
            webrtcvad_path = candidate
            break

    if webrtcvad_path and webrtcvad_path.read_text(encoding="utf-8").startswith("import pkg_resources"):
        content = webrtcvad_path.read_text(encoding="utf-8")
        patched = (
            content
            .replace("import pkg_resources\n", "")
            .replace(
                "pkg_resources.get_distribution('webrtcvad').version",
                '"2.0.10"'
            )
        )
        webrtcvad_path.write_text(patched, encoding="utf-8")
        ok("webrtcvad.py patched (removed pkg_resources dependency)")
    else:
        ok("webrtcvad — no patch needed")


def create_data_dirs():
    print(bold("\n[4/6] Data directories"))
    dirs = [
        ROOT / "data" / "logs",
        ROOT / "data" / "workflows",
        ROOT / "data" / "browser_data",
        ROOT / "data" / "faces",    # Perception: enrolled face photos
        ROOT / "data" / "voices",   # Perception: enrolled voice embeddings (.npy)
        ROOT / "data" / "screenshots",
        ROOT / "data" / "models",   # MediaPipe task model files
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        ok(str(d.relative_to(ROOT.parent)))

    # Ensure memories.json exists and is valid JSON
    memories = ROOT / "data" / "memories.json"
    if not memories.exists() or memories.read_text(encoding="utf-8").strip() in ("", "null"):
        memories.write_text("{}", encoding="utf-8")
        ok("memories.json initialised")
    else:
        ok("memories.json OK")


def setup_playwright():
    print(bold("\n[5/6] Playwright browsers"))
    marker = ROOT / "data" / ".playwright_installed"
    if marker.exists():
        ok("Chromium already installed")
        return
    info("Installing Playwright Chromium browser (first time only)…")
    result = subprocess.run(
        [VENV_PYTHON, "-m", "playwright", "install", "chromium"],
        capture_output=False,
    )
    if result.returncode == 0:
        marker.touch()
        ok("Chromium installed")
    else:
        warn("Playwright chromium install failed — browser tools may not work")


def validate_and_report():
    print(bold("\n[6/6] Capability report"))

    checks = [
        # (module, label, critical)
        ("fastapi",        "FastAPI backend",              True),
        ("uvicorn",        "Uvicorn ASGI server",          True),
        ("dotenv",         "Env file loading",             True),
        ("psutil",         "System stats",                 False),
        ("playwright",     "Browser automation",           False),
        ("cv2",            "OpenCV (camera frames)",       False),
        ("mediapipe",      "Face/Gesture detection (C+B landmark)", False),
        ("openwakeword",   "Wake word 'Hey Jarvis' (A)",   False),
        ("sounddevice",    "Microphone input",             False),
        ("resemblyzer",    "Speaker identification (B)",   False),
        ("faster_whisper", "Offline transcription (C)",    False),
        ("deepface",       "Emotion detection DNN (B+, optional — needs TF ≤3.12)", False),
        ("face_recognition","Identity recognition (A)",    False),
        ("mss",            "Desktop screenshot",           False),
        ("PIL",            "Image processing",             False),
    ]

    critical_ok = True
    for mod, label, critical in checks:
        if is_importable(mod):
            ok(f"{label}")
        else:
            if critical:
                fail(f"{label} — CRITICAL MISSING")
                critical_ok = False
            else:
                warn(f"{label} — not available (degraded mode)")

    return critical_ok


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(bold(cyan("\n╔══════════════════════════════════════════════════╗")))
    print(bold(cyan(  "║       JARVIS 5.0 — Self-Configuration System     ║")))
    print(bold(cyan(  "╚══════════════════════════════════════════════════╝")))
    print(f"  Python {platform.python_version()} | {platform.system()} {platform.machine()}")

    core_ok    = install_core()
    install_perception()
    patch_compat()
    create_data_dirs()
    setup_playwright()
    all_ok = validate_and_report()

    print()
    if core_ok and all_ok:
        print(bold(green("✅  JARVIS está pronto para inicializar.")))
        sys.exit(0)
    else:
        print(bold(red("❌  Dependências críticas faltando. Verifique os erros acima.")))
        sys.exit(1)
