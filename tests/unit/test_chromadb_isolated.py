"""
Teste isolado de ChromaDB para diagnóstico
"""

print("=" * 70)
print("🧪 TESTE ISOLADO - ChromaDB")
print("=" * 70)

try:
    import chromadb
    from chromadb.config import Settings
    from pathlib import Path

    print("\n1️⃣ ChromaDB importado com sucesso")

    # Tentar criar client
    print("2️⃣ Criando PersistentClient...")
    test_dir = Path("data/test_chromadb")
    test_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(test_dir),
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )

    print("3️⃣ Client criado! Testando collection...")

    collection = client.get_or_create_collection(name="test")

    print("4️⃣ Collection criada! Testando add...")

    collection.add(
        ids=["test1"], documents=["teste de documento"], metadatas=[{"source": "test"}]
    )

    print("5️⃣ Documento adicionado! Testando query...")

    results = collection.query(query_texts=["teste"], n_results=1)

    print(f"6️⃣ Query funcionou! Resultados: {len(results['ids'][0])}")

    print("\n" + "=" * 70)
    print("✅ CHROMADB FUNCIONA PERFEITAMENTE!")
    print("=" * 70)
    print("\n💡 O problema pode ser:")
    print("   - Conflict com outro módulo")
    print("   - Timing de inicialização")
    print("   - Versão específica")

except Exception as e:
    print(f"\n❌ ERRO: {type(e).__name__}: {e}")
    print("\n" + "=" * 70)
    print("❌ CHROMADB NÃO FUNCIONA - PRECISA SUBSTITUIÇÃO")
    print("=" * 70)
