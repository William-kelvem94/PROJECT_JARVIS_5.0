import os
import sys
from pathlib import Path

# FORCED ABSOLUTE PATHS
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SRC_PATH = PROJECT_ROOT / "src"

# Add SRC to path at pos 0
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Mock basic config if needed or let it load
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    from src.core.audio.advanced_speech_processor import advanced_speech_processor
    from src.core.intelligence.emotion_detector import emotion_detector

    print("✅ Core modules imported successfully.")
except Exception as e:
    print(f"❌ FAIL: Could not import core modules: {e}")
    sys.exit(1)


def run_tests():
    print("\n--- NEURAL EXPANSION PHASE 1 VERIFICATION ---")

    # Test 1: Emotion Analysis Logic
    print("\n1. Testing Voice Emotion Analysis...")
    # Using a dummy result as we don't need a real file for logic check
    dummy_audio = str(PROJECT_ROOT / "data" / "audio" / "non_existent.wav")
    result = advanced_speech_processor.analyze_speech_emotion(dummy_audio)
    print(f"   Result for missing file: {result}")

    # Test 2: Multimodal Fusion
    print("\n2. Testing Cross-Modal Fusion...")
    v_data = {"emotion": "angry", "score": 0.8}
    a_data = {"emotion": "happy", "confidence": 0.3}
    fused = emotion_detector.get_consolidated_emotion(v_data, a_data)
    print(
        f"   Fused (Angry 0.8 / Happy 0.3): {fused['emotion']} (Score: {fused['confidence']:.2f})"
    )

    # Test 3: Method Presence
    print("\n3. Testing Method Availability...")
    methods = [
        ("advanced_speech_processor", "transcribe_realtime"),
        ("advanced_speech_processor", "diarize"),
        ("emotion_detector", "get_consolidated_emotion"),
    ]
    for obj_name, attr in methods:
        obj = globals().get(obj_name)
        if obj and hasattr(obj, attr):
            print(f"   ✅ {obj_name}.{attr} exists.")
        else:
            print(f"   ❌ {obj_name}.{attr} MISSING.")

    print("\n--------------------------------------------")
    print("✨ PHASE 1 STRUCTURAL VERIFICATION COMPLETE")


if __name__ == "__main__":
    run_tests()
