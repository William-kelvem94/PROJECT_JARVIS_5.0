import sys
import os
import logging
from pathlib import Path

# Garantir output UTF-8 para emojis no Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

# Suprime logs excessivos para o teste de fumaça
logging.basicConfig(level=logging.ERROR)

# Adiciona diretórios ao path
# tools/diagnostics/smoke_test.py -> parent x3 = root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def smoke_test():
    print("\n🚀 JARVIS SMOKE TEST - FASE 0: FUNDAÇÃO (SINGULARITY)")
    print("=" * 60)

    results = {}

    # 1. System Manifest (A Constituição)
    try:
        from src.core.config.system_manifest import system_manifest

        print(f"✅ System Manifest: OK (v{system_manifest.version})")
        print(f"   Modo Debug: {system_manifest.debug_mode}")
        results["SystemManifest"] = True
    except Exception as e:
        print(f"❌ System Manifest falhou: {e}")
        results["SystemManifest"] = False

    # 2. Hardware Manager
    try:
        from src.core.management.hardware_manager import hardware_manager

        print(
            f"✅ Hardware Manager: OK ({hardware_manager.device} / {hardware_manager.gpu_name})"
        )
        results["HardwareManager"] = True
    except Exception as e:
        print(f"❌ Hardware Manager falhou: {e}")
        results["HardwareManager"] = False

    # 3. Blackbox Logger (Persistência)
    try:
        from src.core.config.blackbox_logger import blackbox_logger

        print(f"✅ Blackbox Logger: OK (DB Path: {blackbox_logger.db_path})")
        results["BlackboxLogger"] = True
    except Exception as e:
        print(f"❌ Blackbox Logger falhou: {e}")
        results["BlackboxLogger"] = False

    # 4. Vision System (Otimizado Zero-Disk)
    try:
        from src.core.vision.vision_system import get_vision_system

        vision = get_vision_system()
        print(f"✅ Vision System: OK (Zero-Disk Mode: {vision.zero_disk_mode})")
        results["VisionSystem"] = True
    except Exception as e:
        print(f"❌ Vision System falhou: {e}")
        results["VisionSystem"] = False

    # 5. Global Event Bus
    try:
        from src.core.infrastructure.async_event_bus import get_instance

        bus = get_instance()
        print("✅ Async Event Bus: OK")
        results["EventBus"] = True
    except Exception as e:
        print(f"❌ Event Bus falhou: {e}")
        results["EventBus"] = False

    # 6. Memory Store (Unified)
    try:
        from src.core.intelligence.vector_store import UnifiedVectorStore

        store = UnifiedVectorStore()
        print(f"✅ Vector Store: OK (Path: {store.db_path})")
        results["VectorStore"] = True
    except Exception as e:
        print(f"❌ Vector Store falhou: {e}")
        results["VectorStore"] = False

    print("\n" + "=" * 60)
    summary = all(results.values())
    if summary:
        print("🎉 FASE 0 CONCLUÍDA! TODOS OS COMPONENTES BÁSICOS ESTÃO ESTÁVEIS.")
    else:
        print("⚠️ ALGUNS COMPONENTES FALHARAM. VERIFIQUE OS LOGS EM data/logs/")

    return summary


if __name__ == "__main__":
    success = smoke_test()
    sys.exit(0 if success else 1)
