import os
import tempfile
import unittest
import importlib

class VaultMemoryTest(unittest.TestCase):
    def test_save_episodic_and_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["JARVIS_VAULT_ROOT"] = tmpdir
            import backend.app.vault_memory as vault_memory
            importlib.reload(vault_memory)

            self.assertTrue(vault_memory.is_vault_available())
            path = vault_memory.save_episodic(
                title="Teste de Memória",
                content="Este é um teste de gravação de memória.",
                project="TESTE",
                keywords=["teste", "memória"],
                importance="ALTA"
            )
            self.assertTrue(os.path.exists(path))

            stats = vault_memory.get_vault_stats()
            self.assertTrue(stats.get("available"))
            self.assertGreaterEqual(stats.get("episodicas", 0), 1)

if __name__ == "__main__":
    unittest.main()
