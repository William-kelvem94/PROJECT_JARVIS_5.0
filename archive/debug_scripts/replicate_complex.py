
import os
import sys
import time
import threading

# Simulate Jarvis Environment
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"

print(f"PID: {os.getpid()}")
print("Loading libraries...")

import cv2
print(f"OpenCV: {cv2.__version__}")

import torch
print(f"Torch: {torch.__version__}")
print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

try:
    import face_recognition
    print("FaceRecognition: OK")
except ImportError:
    print("FaceRecognition: Skipped")

try:
    from faster_whisper import WhisperModel
    print("Faster-Whisper: OK")
except ImportError:
    print("Faster-Whisper: Skipped")

try:
    import easyocr
    print("EasyOCR: OK")
except ImportError:
    print("EasyOCR: Skipped")
    
def load_whisper():
    print("Loading Whisper...")
    try:
        model = WhisperModel("base", device="cpu", compute_type="float32", cpu_threads=4)
        print("Whisper Loaded!")
    except Exception as e:
        print(f"Whisper Fail: {e}")

def load_ocr():
    print("Loading EasyOCR...")
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        print("EasyOCR Loaded!")
    except Exception as e:
        print(f"EasyOCR Fail: {e}")

def load_faces():
    print("Loading Dlib/Face models...")
    try:
        # Simulate load
        import dlib
        detector = dlib.get_frontal_face_detector()
        print("Dlib Detector Loaded")
    except Exception as e:
        print(f"Face Fail: {e}")

print("--- Starting Parallel Load Test ---")

t1 = threading.Thread(target=load_whisper)
t2 = threading.Thread(target=load_ocr)
t3 = threading.Thread(target=load_faces)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()

print("--- Main Thread CV2 Work ---")
for i in range(10):
    img = cv2.imread("non_existent.jpg") # Just trigger cv2 internals
    time.sleep(0.1)

print("SUCCESS: No Crash.")
