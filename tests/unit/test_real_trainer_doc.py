import unittest
import sys
import inspect
from pathlib import Path
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestRealTrainerDoc(unittest.TestCase):
    def setUp(self):
        # Mock heavy dependencies before import
        sys.modules["torch"] = MagicMock()
        sys.modules["transformers"] = MagicMock()
        sys.modules["peft"] = MagicMock()

        # Import inside test/setUp to ensure mocks are active
        try:
            from src.learning.real_trainer import train_with_real_learning
            self.train_with_real_learning = train_with_real_learning
        except ImportError:
            self.fail("Could not import train_with_real_learning")

    def test_docstring_content(self):
        """Verifies the docstring contains the expected description."""
        doc = self.train_with_real_learning.__doc__
        self.assertIsNotNone(doc, "Docstring should not be None")
        self.assertIn("Função principal para treinamento REAL", doc)
        self.assertIn("Usa conhecimento destilado + fine-tuning real", doc)

    def test_no_unreachable_code(self):
        """Verifies that the unreachable string literal is removed from source."""
        # Read the source file directly
        source_path = Path(__file__).parent.parent.parent / "src" / "learning" / "real_trainer.py"
        with open(source_path, "r", encoding="utf-8") as f:
            source = f.read()

        unreachable_fragment = 'if config is None:\n        config = {}\n    """'
        self.assertNotIn(unreachable_fragment, source, "Unreachable docstring pattern found in source code")

if __name__ == "__main__":
    unittest.main()
