try:
    import mediapipe as mp

    print(f"MediaPipe imported: {mp}")
    print(f"Dir(mp): {dir(mp)}")

    if hasattr(mp, "solutions"):
        print("mp.solutions found")
        print(f"mp.solutions.hands: {mp.solutions.hands}")
    else:
        print("mp.solutions NOT found")

    # Check for direct submodule import
    import mediapipe.python.solutions.hands as mp_hands

    print(f"Direct import success: {mp_hands}")

except Exception as e:
    print(f"Error: {e}")
