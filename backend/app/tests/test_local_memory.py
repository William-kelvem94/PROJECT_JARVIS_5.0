import os
import tempfile
import unittest
from backend.app.local_memory import LocalMemory

class LocalMemoryTest(unittest.TestCase):
    def test_add_and_search_memory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "jarvis_local.db")
            memory = LocalMemory(db_path=db_path)
            self.assertTrue(memory.add_memory("user1", "Tenho gosto por música eletrônica."))
            self.assertFalse(memory.add_memory("user1", "Tenho gosto por música eletrônica."))

            results = memory.search("música eletrônica", user_id="user1")
            self.assertIsInstance(results, list)
            self.assertTrue(any("eletrônica" in item["memory"] for item in results))

            stats = memory.get_stats("user1")
            self.assertEqual(stats["total_memories"], 1)

if __name__ == "__main__":
    unittest.main()
