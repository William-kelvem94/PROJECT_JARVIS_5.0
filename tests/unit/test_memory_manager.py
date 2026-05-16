import unittest
from unittest.mock import patch, MagicMock
from backend.app.legacy_adapter import MemoryManagerAdapter

class TestMemoryManagerAdapter(unittest.TestCase):
    @patch('backend.app.legacy_adapter.UnifiedMemoryManager')
    def test_init(self, mock_unified):
        manager = MemoryManagerAdapter()
        mock_unified.assert_called_once()
        self.assertIsNotNone(manager._manager)

    @patch('backend.app.legacy_adapter.UnifiedMemoryManager')
    def test_get_stats(self, mock_unified):
        mock_instance = MagicMock()
        mock_instance.interactions = MagicMock()
        mock_instance.interactions.count.return_value = 5
        mock_instance.prompt_cache = {"a": 1, "b": 2}
        mock_instance.short_term = [1, 2, 3]
        mock_unified.return_value = mock_instance

        manager = MemoryManagerAdapter()
        stats = manager.get_stats()

        self.assertEqual(stats["total_memories"], 5)
        self.assertEqual(stats["cache_size"], 2)
        self.assertEqual(stats["short_term_size"], 3)
        self.assertTrue(stats["chromadb_available"])

if __name__ == '__main__':
    unittest.main()
