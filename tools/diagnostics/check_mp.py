import mediapipe as mp
print(f"MediaPipe Version: {getattr(mp, '__version__', 'unknown')}")
print(f"Has solutions: {hasattr(mp, 'solutions')}")
if hasattr(mp, 'solutions'):
    print(f"Has solutions.hands: {hasattr(mp.solutions, 'hands')}")
print(f"Has tasks: {hasattr(mp, 'tasks')}")
