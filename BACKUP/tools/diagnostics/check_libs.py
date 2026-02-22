import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT / "venv" / "Lib" / "site-packages"))

print(f"Python: {sys.version}")
print(f"Path: {sys.path}")

try:
    import face_recognition

    print("✅ face_recognition IMPORTED SUCCESSFULY")
    print(f"Version: {face_recognition.__version__}")
except Exception as e:
    print(f"❌ face_recognition IMPORT FAILED: {e}")

try:
    import dlib

    print("✅ dlib IMPORTED SUCCESSFULY")
    print(f"DLIB_USE_CUDA: {dlib.DLIB_USE_CUDA}")
except Exception as e:
    print(f"❌ dlib IMPORT FAILED: {e}")

try:
    import cv2

    print("✅ cv2 IMPORTED SUCCESSFULY")
    print(f"Version: {cv2.__version__}")
except Exception as e:
    print(f"❌ cv2 IMPORT FAILED: {e}")
