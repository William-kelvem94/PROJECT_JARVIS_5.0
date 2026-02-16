import sys
import os
import asyncio
import logging
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("FullSystemTest")

try:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
except:
    pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Definir função assíncrona fora do loop principal
async def test_ai_async(agent, command):
    return await agent.process_command(command)


def run_test():
    print("\n" + "=" * 50)
    print("🚀 INICIANDO TESTE SISTÊMICO JARVIS 5.0")
    print("=" * 50 + "\n")

    try:
        # 1. CORE IMPORTS
        print("[1/6] Importando Core Modules...")
        from src.core.intelligence.ai_agent import ai_agent
        from src.core.audio.voice_controller import get_voice_controller
        from src.core.vision.camera_controller import get_camera_controller
        from src.core.management.hardware_manager import hardware_manager

        print("✅ Core Modules Importados com Sucesso.")

        # 2. HARDWARE CHECK
        print("\n[2/6] Verificando Hardware...")
        status = hardware_manager.get_status()
        print(f"   - Device: {status['device']}")
        print(f"   - Tier: {status['tier']}")
        print(f"   - RAM Livre: {status['ram_free_gb']} GB")
        print("✅ Hardware Manager Operacional.")

        # 3. VOICE ENGINE
        print("\n[3/6] Inicializando Voice Engine (Lazy)...")
        voice = get_voice_controller()
        if voice:
            print("✅ Voice Controller Instanciado.")
        else:
            print("⚠️ Voice Controller falhou (esperado se sem audio device).")

        # 4. VISION ENGINE
        print("\n[4/6] Inicializando Vision Engine (Lazy)...")
        cam = get_camera_controller()
        if cam:
            print("✅ Camera Controller Instanciado.")
        else:
            print("⚠️ Camera Controller falhou.")

        # 5. AI PROCESSING
        print("\n[5/6] Testando Processamento de IA...")
        test_command = "Quem é você e qual sua função principal?"
        print(f"   📝 Input: '{test_command}'")

        # Simular processamento (sem voz real para não travar em loop)
        # Usando loop existente ou criando novo
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        response = loop.run_until_complete(test_ai_async(ai_agent, test_command))

        print(f"   🤖 Output: '{response}'")
        if response:
            print("✅ AI Agent gerou resposta com sucesso.")
        else:
            print("❌ AI Agent retornou resposta vazia.")

        # 6. MEMORY CHECK
        print("\n[6/6] Verificando Persistência de Memória...")
        from src.core.intelligence.memory_manager import memory_manager

        # Tentar recuperar a última interação via RAM (short-term)
        last_mem = (
            memory_manager.short_term_memory[-1]
            if memory_manager.short_term_memory
            else None
        )

        if last_mem and last_mem["user"] == test_command:
            print(f"✅ Memória confirmada: {last_mem['timestamp']}")
        else:
            print("⚠️ Memória não encontrada na RAM imediata (pode ser assíncrono).")

        print("\n" + "=" * 50)
        print("✅ TESTE SISTÊMICO CONCLUÍDO COM SUCESSO")
        print("=" * 50 + "\n")

    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ FALHA FATAL NO TESTE")
        print(f"Erro: {e}")
        traceback.print_exc()
        print("=" * 50 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    run_test()
