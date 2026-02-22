import mediapipe as mp

res = []
try:
    res.append(f"MediaPipe Version: {mp.__version__}")
    res.append(f"Has solutions: {hasattr(mp, 'solutions')}")
    res.append("Import mediapipe.solutions.hands: SUCCESS")
except Exception as e:
    res.append(f"Import Error: {e}")

try:
    res.append("Import mediapipe.python.solutions.hands: SUCCESS")
except Exception as e:
    res.append(f"Import mediapipe.python Error: {e}")

with open("tests/import_debug.txt", "w") as f:
    f.write("\n".join(res))
