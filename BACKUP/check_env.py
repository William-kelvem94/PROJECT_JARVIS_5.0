import importlib
import sys

dependencies = [
    "speech_recognition", "pygame", "pyttsx3", "edge_tts", "requests", "bs4", "yaml"
]

def check_deps():
    print("--- JARVIS 5.0 DEPENDENCY CHECK ---")
    missing = []
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"[OK] {dep}")
        except ImportError:
            missing.append(dep)
            print(f"[MISSING] {dep}")
            
    if missing:
        print("\nAlgumas bibliotecas estão faltando. Execute:")
        print(f"pip install {' '.join(missing)}")
    else:
        print("\n✅ Todos os sistemas vitais estão instalados. JARVIS pode ser iniciado via 'python main.py'")

if __name__ == "__main__":
    check_deps()
