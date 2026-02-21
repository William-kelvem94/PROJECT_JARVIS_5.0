import mediapipe as mp

try:
    print(f"MediaPipe Version: {mp.__version__}")
    print(f"Has solutions: {hasattr(mp, 'solutions')}")
    print("Import mediapipe.solutions.hands: SUCCESS")
except Exception as e:
    print(f"Import Error: {e}")

try:
    print("Import mediapipe.python.solutions.hands: SUCCESS")
except Exception as e:
    print(f"Import mediapipe.python Error: {e}")
