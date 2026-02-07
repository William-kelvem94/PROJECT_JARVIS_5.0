# test_individual.py
print("🔍 Testando módulos individuais...")

tests = [
    ("PyTorch", "torch"),
    ("dlib", "dlib"),
    ("face_recognition", "face_recognition"),
    ("OpenCV", "cv2"),
    ("PyQt6", "PyQt6"),
    ("faster-whisper", "faster_whisper"),
    ("webrtcvad", "webrtcvad"),
]

for name, module in tests:
    try:
        __import__(module)
        print(f"✅ {name} OK")
    except ImportError as e:
        print(f"❌ {name} FALHOU: {e}")
    except Exception as e:
        print(f"❌ {name} ERRO INESPERADO: {e}")
