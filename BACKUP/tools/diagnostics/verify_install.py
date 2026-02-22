import sys
import importlib

required_modules = [
    "pyautogui",
    "cv2",
    "speech_recognition",
    "pyttsx3",
    "edge_tts",
    "psutil",
    "pyaudio",
    "customtkinter",
    "mss",
    "pygame",
    "sqlalchemy",
    "transformers",
    "sentence_transformers",
    "chromadb",
    "PIL",
    "requests",
    "numpy",
    "googlesearch",
    "fer",
    "librosa",
    "pystray",
    "pytesseract",
    "spacy",
    "packaging",
    "reportlab",
    "pandas",
    "openpyxl",
]

print("Verificando dependencias...")
missing = []

for lib in required_modules:
    try:
        if lib == "cv2":
            import cv2
        elif lib == "PIL":
            import PIL
        else:
            importlib.import_module(lib)
        print(f"[OK] {lib}")
    except ImportError as e:
        print(f"[FALHA] {lib}: {e}")
        missing.append(lib)

if missing:
    print(f"\nFALTAM PACOTES: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\nTudo pronto! Pode rodar o JARVIS.")
    sys.exit(0)
