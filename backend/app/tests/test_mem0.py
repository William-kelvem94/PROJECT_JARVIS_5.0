import asyncio
import os
import tempfile
import unittest
from backend.app.mem0 import AsyncMemoryClient
from backend.app.local_memory import LocalMemory

class Mem0HybridTest(unittest.TestCase):
    def test_get_all_merges_cloud_and_local(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_local = LocalMemory(db_path=os.path.join(tmpdir, "jarvis_local.db"))
            client = AsyncMemoryClient()
            client._local = temp_local
            client._cloud.store = {}

            client._cloud.add([
                {"role": "user", "content": "Gosto de trabalhar com IA local."}
            ], user_id="Chefe")
            temp_local.add_memory("Chefe", "Prefere modelos locais e RAG.")

            merged = asyncio.run(client.get_all(user_id="Chefe"))
            self.assertTrue(any("IA local" in item["memory"] for item in merged))
            self.assertTrue(any("RAG" in item["memory"] for item in merged))

    def test_search_merges_cloud_and_local(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_local = LocalMemory(db_path=os.path.join(tmpdir, "jarvis_local.db"))
            client = AsyncMemoryClient()
            client._local = temp_local
            client._cloud.store = {}

            client._cloud.add([
                {"role": "user", "content": "Meu modelo favorito é Llama."}
            ], user_id="Chefe")
            temp_local.add_memory("Chefe", "Uso de memórias de sessão e IA local.")

            results = asyncio.run(client.search("memória", filters={"user_id": "Chefe"}))
            self.assertTrue(any("memórias" in item["memory"] for item in results["results"]))

if __name__ == "__main__":
    unittest.main()
