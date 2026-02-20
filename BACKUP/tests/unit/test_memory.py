"""
Test script for MemoryManager (Auto-Learning / RAG)
Tests memory storage, recall, and context generation
"""

from src.core.intelligence.memory_manager import memory_manager

print("=" * 70)
print("🧠 JARVIS AUTO-LEARNING - Memory Manager Test")
print("=" * 70)

# Test 1: Stats
print("\n1️⃣ MEMORY STATS:")
stats = memory_manager.get_stats()
for key, value in stats.items():
    print(f"   {key}: {value}")

# Test 2: Save memories
print("\n2️⃣ SALVANDO MEMÓRIAS DE TESTE:")
test_interactions = [
    ("qual é a capital do Brasil?", "A capital do Brasil é Brasília."),
    ("que horas são?", "São 19:30."),
    ("abra o navegador", "Abrindo o navegador Chrome."),
    ("qual é a capital da França?", "A capital da França é Paris."),
]

for cmd, resp in test_interactions:
    success = memory_manager.remember(cmd, resp)
    status = "✅" if success else "❌"
    print(f"   {status} '{cmd[:30]}...'")

# Test 3: Recall similar memories
print("\n3️⃣ BUSCANDO MEMÓRIAS SIMILARES:")
queries = [
    "qual é a capital de Portugal?",  # Similar a capital queries
    "abrir chrome",  # Similar a abrir navegador
    "horário atual",  # Similar a que horas são
]

for query in queries:
    print(f"\n   Query: '{query}'")
    memories = memory_manager.recall(query, top_k=2)

    if memories:
        for i, mem in enumerate(memories, 1):
            print(f"      {i}. [Sim: {mem['similarity']:.2f}] {mem['command'][:40]}...")
    else:
        print("      Nenhuma memória encontrada")

# Test 4: Get context for prompt
print("\n4️⃣ CONTEXTO PARA PROMPT:")
query = "qual é a capital da Alemanha?"
context = memory_manager.get_context(query, max_memories=2)
if context:
    print(context)
else:
    print("   Nenhum contexto disponível")

# Test 5: Final stats
print("\n5️⃣ STATS FINAIS:")
final_stats = memory_manager.get_stats()
print(f"   Total de memórias: {final_stats.get('total_memories', 0)}")

print("\n" + "=" * 70)
print("✅ TESTE COMPLETO!")
print("=" * 70)
