"""Teste pós-reset do ChromaDB"""

from src.core.intelligence.memory_manager import memory_manager
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("🔄 TESTE PÓS-RESET DO CHROMADB")
print("=" * 60)


print("\n✅ Memory Manager importado")
print(f"   ChromaDB disponível: {memory_manager.collection is not None}")

if memory_manager.collection:
    count = memory_manager.collection.count()
    print(f"   Memórias no banco: {count}")
    print("\n✅ CHROMADB FUNCIONANDO CORRETAMENTE")
else:
    print("\n⚠️  ChromaDB em modo fallback (RAM)")
    print("   Sistema continua operacional")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO")
