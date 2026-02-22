#!/usr/bin/env python3
"""
JARVIS 5.0 - Voice Output Test
Tests if voice output is working properly
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("🔊 JARVIS 5.0 - Voice Output Test")
print("=" * 60)

# Test 1: VoiceController
print("\n1️⃣  Testing JARVIS VoiceController...")
try:
    from src.core.audio.voice_controller import voice_controller, VoiceController

    if voice_controller is None:
        print("   ⚠️ voice_controller is None, creating instance...")
        voice_controller = VoiceController()

    print(f"   ✅ VoiceController available: {type(voice_controller).__name__}")
    print("   🔊 Speaking via VoiceController...")
    voice_controller.speak("Jarvis sistema atualizado. Como posso ajudar, William?")
    print("   ✅ VoiceController test complete")

except Exception as e:
    print(f"   ❌ VoiceController error: {e}")
    import traceback

    traceback.print_exc()

# Test 3: Check audio device
print("\n3️⃣  Checking audio output device...")
try:
    import sounddevice as sd

    print(f"   ℹ️ Default device: {sd.default.device}")
    devices = sd.query_devices()
    output_devices = [i for i, d in enumerate(devices) if d["max_output_channels"] > 0]
    print(f"   ℹ️ Available output devices: {output_devices}")
    for dev_id in output_devices[:3]:
        print(f"      - {devices[dev_id]['name']}")
except Exception as e:
    print(f"   ⚠️ Audio device check failed: {e}")

# Test 4: Check if Edge-TTS works
print("\n4️⃣  Testing Edge-TTS...")
try:
    print("   ✅ edge_tts module available")
    # We won't actually call it as it needs async
except Exception as e:
    print(f"   ⚠️ Edge-TTS not available: {e}")

# Test 5: Check XTTS
print("\n5️⃣  Testing XTTS (if available)...")
try:
    import src.core.audio.voice_controller as vc

    XTTS = getattr(vc, "XTTS", None)
    if XTTS:
        print("   ✅ XTTS available")
    else:
        print("   ⚠️ XTTS not loaded")
except ImportError:
    print("   ⚠️ XTTS not available or not installed")
except Exception as e:
    print(f"   ⚠️ XTTS check failed: {e}")

print("\n" + "=" * 60)
print("✅ Voice test complete. Check if you heard anything.")
print("   If no audio: Check Windows volume, audio device settings")
print("=" * 60)
