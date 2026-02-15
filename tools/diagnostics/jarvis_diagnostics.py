
import sys
import os
import subprocess
import logging
import importlib
from pathlib import Path

# Configuração de paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print("=" * 70)
print("🔍 JARVIS SINGULARITY - DIAGNÓSTICO DE SISTEMA")
print("=" * 70)

def check_import(module_name, friendly_name):
    try:
        importlib.import_module(module_name)
        print(f"✅ {friendly_name:30} : OK")
        return True
    except ImportError as e:
        print(f"❌ {friendly_name:30} : FALTANDO ({e})")
        return False
    except Exception as e:
        print(f"⚠️ {friendly_name:30} : ERRO ({e})")
        return False

print("\n📦 VERIFICANDO DEPENDÊNCIAS CRÍTICAS:")
critical = [
    ("PyQt6", "Interface Gráfica"),
    ("speech_recognition", "Reconhecimento de Voz"),
    ("pyttsx3", "Voz Offline"),
    ("edge_tts", "Voz Online (Microsoft)"),
    ("vosk", "Voz Offline (Vosk)"),
    ("requests", "Comunicação API"),
    ("cv2", "Visão (OpenCV)"),
    ("numpy", "Cálculo Numérico"),
]
for mod, name in critical:
    check_import(mod, name)

print("\n🧠 VERIFICANDO MÓDULOS JARVIS CORE:")
core_mods = [
    ("src.core.ai_agent", "AI Agent Coordinator"),
    ("src.core.voice_controller", "Voice Controller"),
    ("src.core.screen_capture", "Screen Capture"),
    ("src.core.action_controller", "Action Controller"),
    ("src.core.system_controller", "System Controller (God Mode)"),
    ("src.core.memory_manager", "Memory Manager (RAG)"),
    ("src.core.code_generator", "Code Generator"),
    ("src.core.vision_enhancer", "Vision Enhancer (YOLO)"),
]
for mod, name in core_mods:
    check_import(mod, name)

print("\n🎤 TESTANDO HARDWARE ÁUDIO:")
try:
    import speech_recognition as sr
    mic_list = sr.Microphone.list_microphone_names()
    if not mic_list:
        print("❌ Microfone: Nenhum dispositivo detectado!")
    else:
        print(f"✅ Microfone: {len(mic_list)} dispositivos encontrados")
        for i, name in enumerate(mic_list[:3]):
            print(f"   - [{i}] {name}")
except Exception as e:
    print(f"❌ Microfone: Erro ao listar dispositivos: {e}")

print("\n🌐 VERIFICANDO CONECTIVIDADE:")
try:
    import requests
    resp = requests.get("http://localhost:11434", timeout=2)
    if resp.status_code == 200:
        print("✅ Ollama Local: ONLINE")
    else:
        print(f"⚠️ Ollama Local: STATUS {resp.status_code}")
except:
    print("❌ Ollama Local: OFFLINE (Certifique-se que o Ollama está rodando)")

try:
    if os.environ.get("GOOGLE_API_KEY"):
        print("✅ Gemini API Key: CONFIGURADA")
    else:
        print("⚠️ Gemini API Key: NÃO ENCONTRADA (Usará modo local)")
except:
    pass

print("\n" + "=" * 70)
print("🏁 DIAGNÓSTICO CONCLUÍDO")
print("=" * 70)
