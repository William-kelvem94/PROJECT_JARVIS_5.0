
import sys
import os
import json
import importlib
from pathlib import Path

# Configuração de paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

results = {
    "dependencies": {},
    "core_modules": {},
    "hardware": {},
    "env": {}
}

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        return "OK"
    except ImportError as e:
        return f"MISSING: {e}"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"

# Dependências
for mod in ["PyQt6", "speech_recognition", "pyttsx3", "edge_tts", "vosk", "requests", "cv2", "numpy", "chromadb", "torch", "ultralytics"]:
    results["dependencies"][mod] = check_import(mod)

# Módulos Core
for mod in ["core.ai_agent", "core.voice_controller", "core.system_controller", "core.memory_manager", "core.vision_enhancer"]:
    results["core_modules"][mod] = check_import(f"src.{mod}")

# Hardware (Lite)
try:
    import speech_recognition as sr
    results["hardware"]["mics"] = sr.Microphone.list_microphone_names()
except Exception as e:
    results["hardware"]["mics_error"] = str(e)

# Env
results["env"]["GOOGLE_API_KEY"] = "SET" if os.environ.get("GOOGLE_API_KEY") else "MISSING"

print(json.dumps(results, indent=2))
