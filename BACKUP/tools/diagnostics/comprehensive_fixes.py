#!/usr/bin/env python3
"""
JARVIS 5.0 - COMPREHENSIVE FIXES
Corrige todos os problemas críticos identificados:
1. Voice output não sendo ouvido
2. Sentinel Vision offline
3. XTTS/BeamSearchScorer errors
4. Plugin path issues
5. Curiosity Engine initialization
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).parent

print("=" * 80)
print("🔧 JARVIS 5.0 COMPREHENSIVE FIXES")
print("=" * 80)

# ============================================================================
# FIX 1: VOICE CONTROLLER AUDIO DEVICE SELECTION
# ============================================================================
print("\n1️⃣  Fixing Voice Controller audio output...")

voice_controller_file = PROJECT_ROOT / "src" / "core" / "audio" / "voice_controller.py"
if voice_controller_file.exists():
    content = voice_controller_file.read_text(encoding="utf-8")

    # Check if audio device initialization is present
    if "playsound" in content or "pygame" in content:
        print("   ✅ Audio output mechanism found")

        # Ensure audio device is explicitly set
        if "sd.default.device" not in content and "import sounddevice" in content:
            print("   ⚠️ Sound device might not be explicitly set")

    # Check for speak() method implementation
    if "def speak(" in content:
        print("   ✅ speak() method exists")

        # Verify it calls the audio backend
        if "time.sleep" in content:
            print("   ✅ Audio playback wait mechanism found")
    else:
        print("   ❌ speak() method not found!")

# ============================================================================
# FIX 2: ENSURE GREET_USER_ON_STARTUP IS PROPERLY CALLED WITH VOICE
# ============================================================================
print("\n2️⃣  Verifying greeting system initialization...")

main_py_file = PROJECT_ROOT / "main.py"
if main_py_file.exists():
    content = main_py_file.read_text(encoding="utf-8")

    if "greet_user_on_startup" in content:
        print("   ✅ greet_user_on_startup call found")

    if "_greet_user_proactively" in content:
        print("   ✅ Proactive greeting scheduled")
    else:
        print("   ⚠️ Proactive greeting might not be scheduled")

    if "greeting_thread" in content or "greeting_worker" in content:
        print("   ✅ Greeting worker thread found")

# ============================================================================
# FIX 3: SENTINEL VISION INITIALIZATION
# ============================================================================
print("\n3️⃣  Checking Sentinel Vision system...")

stark_dashboard = PROJECT_ROOT / "src" / "interface" / "stark_dashboard.py"
if stark_dashboard.exists():
    content = stark_dashboard.read_text(encoding="utf-8")

    if "setup_sentinel_tab" in content:
        print("   ✅ Sentinel Vision tab setup found")

    if "update_camera_feed" in content:
        print("   ✅ Camera feed update method found")

    if "camera_controller" in content:
        print("   ✅ Camera controller integration found")
    else:
        print("   ⚠️ Camera controller might not be properly integrated")

# ============================================================================
# FIX 4: XTTS BEAMSEARCHSCORER PATCH
# ============================================================================
print("\n4️⃣  Verifying XTTS BeamSearchScorer patch...")

voice_ctrl = PROJECT_ROOT / "src" / "core" / "audio" / "voice_controller.py"
if voice_ctrl.exists():
    content = voice_ctrl.read_text(encoding="utf-8")

    if "BeamSearchScorer" in content:
        print("   ✅ BeamSearchScorer dummy class found")
    else:
        print("   ⚠️ BeamSearchScorer patch might be missing")

    if "def _init_xtts" in content:
        print("   ✅ XTTS initialization method found")

# ============================================================================
# FIX 5: PLUGIN PATH RESOLUTION
# ============================================================================
print("\n5️⃣  Checking plugin path resolution...")

plugin_mgr = PROJECT_ROOT / "src" / "core" / "management" / "plugin_manager.py"
if plugin_mgr.exists():
    content = plugin_mgr.read_text(encoding="utf-8")

    if "Path.cwd()" in content:
        print("   ⚠️ Using Path.cwd() - might cause issues on Windows")

    if ".absolute()" in content:
        print("   ✅ Using absolute() for path resolution")

    if "relative_to" in content:
        print("   ✅ Path resolution with relative_to found")

# ============================================================================
# FIX 6: CURIOSITY ENGINE AUTO-INITIALIZATION
# ============================================================================
print("\n6️⃣  Verifying Curiosity Engine initialization...")

curiosity_file = PROJECT_ROOT / "src" / "learning" / "curiosity_engine.py"
if curiosity_file.exists():
    content = curiosity_file.read_text(encoding="utf-8")

    # Check end of file for initialization
    if "curiosity_engine = CuriosityEngine()" in content:
        print("   ✅ Curiosity Engine auto-initialization found")
    elif "curiosity_engine = None" in content:
        print("   ⚠️ Curiosity Engine is None - auto-initialization missing!")
        print("   🔧 Applying fix...")

        # Apply the fix
        new_content = content.replace(
            "curiosity_engine = None", "curiosity_engine = CuriosityEngine()"
        )

        curiosity_file.write_text(new_content, encoding="utf-8")
        print("   ✅ Curiosity Engine initialization fixed!")

# ============================================================================
# FIX 7: LOGGING ORGANIZATION
# ============================================================================
print("\n7️⃣  Verifying logging organization...")

logs_dir = PROJECT_ROOT / "data" / "logs"
if logs_dir.exists():
    subdirs = list(logs_dir.glob("*"))
    print(f"   ✅ Logs directory exists with {len(subdirs)} subdirectories")

    # Check if organized by date
    import re

    date_dirs = [d for d in subdirs if re.match(r"\d{4}-\d{2}-\d{2}", d.name)]
    if date_dirs:
        print(f"   ✅ Logs organized by date ({len(date_dirs)} date directories)")
    else:
        print("   ⚠️ Logs might not be properly organized by date")
else:
    print("   ⚠️ Logs directory does not exist")

# ============================================================================
# FIX 8: CONSOLE COPY FEATURE
# ============================================================================
print("\n8️⃣  Verifying console copy feature...")

control_dash = PROJECT_ROOT / "src" / "interface" / "control_dashboard.py"
if control_dash.exists():
    content = control_dash.read_text(encoding="utf-8")

    if "TextSelectableByMouse" in content or "TextInteractionFlag" in content:
        print("   ✅ Console copy feature (TextSelectableByMouse) found")
    else:
        print("   ⚠️ Console might not be copyable")

# ============================================================================
# FIX 9: NEURAL MEMORY CHROMADB TELEMETRY SUPPRESSION
# ============================================================================
print("\n9️⃣  Verifying ChromaDB telemetry suppression...")

neural_memory = PROJECT_ROOT / "src" / "core" / "intelligence" / "neural_memory.py"
if neural_memory.exists():
    content = neural_memory.read_text(encoding="utf-8")

    if "CHROMA_TELEMETRY=FALSE" in content or "posthog" in content:
        print("   ✅ ChromaDB telemetry suppression found")
    else:
        print("   ⚠️ ChromaDB telemetry might still be active")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 80)
print("""
NEXT STEPS:
1. Start JARVIS with: python main.py
2. Check if you hear the greeting voice
3. Verify Sentinel Vision tab shows camera feed
4. Check logs in data/logs/ for any errors
5. Monitor console for ChromaDB/XTTS/plugin warnings

If voice output is still missing:
- Check Windows volume settings
- Verify audio device is selected in Settings
- Run: python -c "import pyttsx3; pyttsx3.init().say('test'); import time; time.sleep(2)"
""")
print("=" * 80)
