import sys
import os
import asyncio
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from src.core.infrastructure.system_manifest import manifest
from src.core.infrastructure.async_event_bus import AsyncEventBus, EventType
from src.core.infrastructure.priority_scheduler import PriorityScheduler, TaskPriority

async def verify_foundation():
    print("🏗️  Verificando Fundação JARVIS 5.0...")
    
    # 1. Verificar SystemManifest (A Constituição)
    print("\n📜 1. Verificando Constituição (SystemManifest)...")
    try:
        tiers = manifest.tiers
        limits = manifest.complexity_limits
        
        print(f"   ✅ Configuração carregada com sucesso.")
        print(f"   ℹ️  Tiers de Modelos: {list(tiers.keys())}")
        print(f"   ℹ️  Limites de Complexidade: {limits}")
        
        if not tiers or not limits:
            print("   ❌ ERRO: Configuração incompleta ou vazia.")
            return False
    except Exception as e:
        print(f"   ❌ FATAL: Falha ao carregar manifesto: {e}")
        return False

    # 2. Verificar AsyncEventBus
    print("\n📡 2. Verificando AsyncEventBus...")
    bus = AsyncEventBus(enable_persistence=False)
    await bus.start()
    
    received_events = []
    
    async def sub_callback(event):
        print(f"      📩 Evento recebido: {event.type.value}")
        received_events.append(event)
        
    sub_id = bus.subscribe(EventType.SYSTEM_STARTUP, sub_callback)
    bus.publish(EventType.SYSTEM_STARTUP, {"msg": "Hello Foundation"})
    
    # Aguarda processamento
    await asyncio.sleep(0.5)
    
    await bus.stop()
    
    if len(received_events) == 1:
        print("   ✅ EventBus operacional.")
    else:
        print(f"   ❌ EventBus falhou. Eventos recebidos: {len(received_events)}")
        return False

    # 3. Verificar PriorityScheduler
    print("\n⚙️  3. Verificando PriorityScheduler...")
    scheduler = PriorityScheduler()
    await scheduler.start()
    
    task_executed = False
    
    async def test_task():
        nonlocal task_executed
        print("      🏃 Tarefa executada!")
        task_executed = True
        
    scheduler.schedule_task("test_foundation", test_task, TaskPriority.CRITICAL)
    
    # Aguarda execução
    await asyncio.sleep(0.5)
    
    await scheduler.stop()
    
    if task_executed:
        print("   ✅ PriorityScheduler operacional.")
    else:
        print("   ❌ PriorityScheduler falhou na execução da tarefa.")
        return False

    print("\n✅✅ FUNDAÇÃO APROVADA ✅✅")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(verify_foundation())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erro não tratado: {e}")
        sys.exit(1)
