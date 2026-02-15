import sys
import os
import logging
from pathlib import Path

# Suprime logs excessivos
logging.basicConfig(level=logging.ERROR)

# Adiciona diretórios ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def smoke_test():
    print("\n🚀 JARVIS SMOKE TEST - COMPONENTES REAIS")
    print("=" * 60)
    
    results = {}

    # 1. Hardware Manager
    try:
        from src.core.management.hardware_manager import hardware_manager
        print(f"✅ Hardware Manager: {hardware_manager.device} / {hardware_manager.gpu_name}")
        results['HardwareManager'] = True
    except Exception as e:
        print(f"❌ Hardware Manager falhou: {e}")
        results['HardwareManager'] = False

    # 2. Config
    try:
        from src.utils.config import config
        print(f"✅ Config: Carregado")
        results['Config'] = True
    except Exception as e:
        print(f"❌ Config falhou: {e}")
        results['Config'] = False

    # 3. Audio System (Somente inicialização básica)
    try:
        from src.core.audio.enhanced_audio import EnhancedAudioSystem
        audio = EnhancedAudioSystem()
        print(f"✅ Audio System: Base OK")
        results['AudioSystem'] = True
    except Exception as e:
        print(f"❌ Audio System falhou: {e}")
        results['AudioSystem'] = False

    # 4. Vision System
    try:
        from src.core.vision.vision_system import VisionSystem
        vision = VisionSystem()
        print("✅ Vision System: Base OK")
        results['VisionSystem'] = True
    except Exception as e:
        print(f"❌ Vision System falhou: {e}")
        results['VisionSystem'] = False

    # 5. AI Agent
    try:
        from src.core.intelligence.ai_agent import ai_agent
        print(f"✅ AI Agent: Pronto (Instância Global)")
        results['AIAgent'] = True
    except Exception as e:
        print(f"❌ AI Agent falhou: {e}")
        results['AIAgent'] = False

    # 6. Learning Engine
    try:
        from src.learning.learning_engine import LearningEngine
        engine = LearningEngine(PROJECT_ROOT)
        print("✅ Learning Engine: Instanciado")
        results['LearningEngine'] = True
    except Exception as e:
        print(f"❌ Learning Engine falhou: {e}")
        results['LearningEngine'] = False

    # 7. Orchestrator
    try:
        from src.core.orchestrator import StarkOrchestrator
        orchestrator = StarkOrchestrator(None) # Passando None para Jarvis core por enquanto
        print("✅ Orchestrator: Criado")
        results['Orchestrator'] = True
    except Exception as e:
        print(f"❌ Orchestrator falhou: {e}")
        results['Orchestrator'] = False

    print("\n" + "=" * 60)
    summary = all(results.values())
    if summary:
        print("🎉 TODOS OS COMPONENTES BÁSICOS ESTÃO FUNCIONANDO!")
    else:
        print("⚠️ ALGUNS COMPONENTES FALHARAM NA INICIALIZAÇÃO.")
    
    return summary

if __name__ == "__main__":
    success = smoke_test()
    sys.exit(0 if success else 1)
