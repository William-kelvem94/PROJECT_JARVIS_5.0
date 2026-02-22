from learning.dependency_manager import DependencyManager, DependencyStatus
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestDependencyManager(unittest.TestCase):
    def setUp(self):
        # We need to mock _check_all_dependencies to avoid real checks during
        # init
        with patch.object(DependencyManager, "_check_all_dependencies"):
            self.dm = DependencyManager()

    def test_is_available_missing_no_fallback(self):
        # Setup a missing dependency with no fallback
        self.dm._status["test_dep"] = DependencyStatus(
            available=False,
            error="Test Error",
            fallback_available=False,
            capabilities=set(),
        )

        # Should return False
        self.assertFalse(self.dm.is_available("test_dep"))

    def test_is_available_missing_with_fallback(self):
        # Setup a missing dependency with fallback
        self.dm._status["test_dep_fallback"] = DependencyStatus(
            available=False,
            error="Test Error",
            fallback_available=True,
            capabilities=set(),
        )

        # Should return True (current behavior)
        self.assertTrue(self.dm.is_available("test_dep_fallback"))

    def test_is_available_present(self):
        # Setup a present dependency
        self.dm._status["test_dep_present"] = DependencyStatus(
            available=True, version="1.0.0", capabilities={"cap1"}
        )

        # Should return True
        self.assertTrue(self.dm.is_available("test_dep_present"))
        # Capability check
        self.assertTrue(self.dm.is_available("test_dep_present", "cap1"))
        self.assertFalse(self.dm.is_available("test_dep_present", "cap2"))


if __name__ == "__main__":
    unittest.main()
