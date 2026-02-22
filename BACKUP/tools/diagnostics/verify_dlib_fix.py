import face_recognition
import numpy as np


def test_dlib_fix():
    print("Testing dlib fix...")

    # Create a dummy image (100x100 RGB)
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

    # Create a dummy face location (top, right, bottom, left)
    face_locations = [(10, 90, 90, 10)]

    try:
        print("Attempting face_encodings with num_jitters=0...")
        # Check if the function accepts num_jitters=0
        encodings = face_recognition.face_encodings(
            dummy_image, face_locations, num_jitters=0
        )
        print(f"Success! Encodings generated: {len(encodings)}")
        return True
    except TypeError as e:
        print(f"Failed with TypeError: {e}")
        return False
    except Exception as e:
        print(f"Failed with Exception: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    success = test_dlib_fix()
    if success:
        print("VERIFICATION PASSED: The dlib argument fix (num_jitters=0) is valid.")
    else:
        print("VERIFICATION FAILED: The fix did not resolve the issue.")
