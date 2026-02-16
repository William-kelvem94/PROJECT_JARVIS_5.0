"""Teste rápido de lazy loading"""

import time
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("🧪 TESTE: Lazy Loading de Neural Memory")
print("=" * 60)

# Teste 1: Import rápido
print("\n1️⃣ Testando import (deve ser rápido - sem carregar embeddings)...")
start = time.time()
from src.core.intelligence.neural_memory import neural_memory

elapsed = time.time() - start

print(f"⏱️  Tempo de import: {elapsed:.2f}s")
if elapsed < 5.0:
    print("✅ PASS: Import rápido (lazy loading funcionando)")
else:
    print(f"⚠️  SLOW: Import demorou {elapsed:.2f}s")

# Teste 2: Verificar estado inicial
print("\n2️⃣ Verificando estado inicial...")
print(f"   - Modelo carregado: {neural_memory.model is not None}")
print(
    f"   - ChromaDB disponível: {hasattr(neural_memory, 'client') and neural_memory.client is not None}"
)

if neural_memory.model is None:
    print("✅ PASS: Modelo NÃO carregado (lazy loading correto)")
else:
    print("⚠️  WARN: Modelo já carregado no import")

# Teste 3: Carregar sob demanda
print("\n3️⃣ Testando carregamento sob demanda...")
if hasattr(neural_memory, "_ensure_model_loaded"):
    start = time.time()
    success = neural_memory._ensure_model_loaded()
    elapsed = time.time() - start

    print(f"⏱️  Tempo de carregamento: {elapsed:.2f}s")
    if success:
        print("✅ PASS: Modelo carregado sob demanda com sucesso")
    else:
        print("⚠️  WARN: Modelo não disponível (modo degradado)")
else:
    print("⚠️  WARN: Método _ensure_model_loaded não encontrado")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO")
