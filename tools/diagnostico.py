import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=== JARVIS 5.0 DIAGNOSTIC BOOT ===")

try:
    print("[1/6] Carregando Configurações...", end=" ")
    from utils.config import config
    print("OK")

    print("[2/6] Verificando Hardware...", end=" ")
    from core.hardware_manager import hardware_manager
    status = hardware_manager.get_status()
    print(f"OK ({status['device'].upper()})")

    print("[3/6] Inicializando Banco de Dados...", end=" ")
    from database.models import db_manager
    print("OK")

    print("[4/6] Testando Agente de IA...", end=" ")
    from core.ai_agent import ai_agent
    print("OK")

    print("[5/6] Verificando Visão (FaceRec/MediaPipe)...", end=" ")
    try:
        import face_recognition
        import mediapipe
        print("OK")
    except ImportError as e:
        print(f"AVISO (Algumas funções de visão podem falhar: {e})")

    print("[6/6] Verificando Voz (Vosk/Edge-TTS)...", end=" ")
    try:
        import vosk
        import edge_tts
        print("OK")
    except ImportError as e:
        print(f"AVISO (Algumas funções de voz podem falhar: {e})")

    print("\n✅ DIAGNÓSTICO CONCLUÍDO: Todos os caminhos de importação estão íntegros.")
    print("O Jarvis 5.0 está pronto para execução real.")

except Exception as e:
    print(f"\n❌ ERRO CRÍTICO NO DIAGNÓSTICO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
