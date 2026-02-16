
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to python path if not already there
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock modules globally for this test file
# This is necessary because some modules are imported at the top level
sys.modules['requests'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()
sys.modules['src.core.intelligence.brain_router'] = MagicMock()
sys.modules['src.core.intelligence.local_brain'] = MagicMock()
sys.modules['src.utils.config'] = MagicMock()

# Mock other modules to prevent side effects during package initialization
sys.modules['src.core.intelligence.ai_agent'] = MagicMock()
sys.modules['src.core.intelligence.memory'] = MagicMock()
sys.modules['src.core.intelligence.context_sanitizer'] = MagicMock()
sys.modules['src.core.intelligence.neural_systems'] = MagicMock()
sys.modules['src.core.intelligence.perception_engine'] = MagicMock()
sys.modules['src.core.intelligence.knowledge_graph'] = MagicMock()
sys.modules['src.core.intelligence.structured_output'] = MagicMock()

# Now import the module under test
from src.core.intelligence.decision_engine import DecisionEngine

class TestDecisionEngine:

    @pytest.fixture
    def decision_engine(self):
        """Fixture to provide a DecisionEngine instance with mocked dependencies"""
        # Mock config if needed by DecisionEngine.__init__
        with patch('src.core.intelligence.decision_engine.config', new=MagicMock()) as mock_config:
            # Setup mock config
            mock_config.GEMINI_API_KEY = "fake_key"
            mock_config.get_ai_config.return_value = "http://fake-ollama:11434"

            # Mock brain_router and local_brain to avoid import errors or side effects
            # Even though we mocked the modules, the attributes on the class instance might rely on them

            engine = DecisionEngine(provider='ollama')
            return engine

    def test_build_prompt_basic(self, decision_engine):
        """Test basic prompt construction with just a command"""
        command = "open calculator"
        context = {}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] open calculator" in prompt
        assert "[VISÃO]" not in prompt
        assert "[EMOÇÃO]" not in prompt
        assert "[TEXTO NA TELA]" not in prompt

    def test_build_prompt_with_vision(self, decision_engine):
        """Test prompt construction with vision context (user face)"""
        command = "hello"
        context = {"user_face": "John Doe"}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] hello" in prompt
        assert "[VISÃO] Usuário identificado: John Doe" in prompt

    def test_build_prompt_with_emotion(self, decision_engine):
        """Test prompt construction with emotion context (happy)"""
        command = "how are you"
        context = {"user_emotion": "happy"}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] how are you" in prompt
        assert "[EMOÇÃO] Usuário está: happy" in prompt

    def test_build_prompt_skip_neutral_emotion(self, decision_engine):
        """Test that 'neutral' emotion is skipped"""
        command = "status"
        context = {"user_emotion": "neutral"}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] status" in prompt
        assert "[EMOÇÃO]" not in prompt

    def test_build_prompt_with_memory(self, decision_engine):
        """Test prompt construction with memory context"""
        command = "remember this"
        context = {"memory_context": "User likes blue."}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] remember this" in prompt
        assert "User likes blue." in prompt

    def test_build_prompt_with_ocr(self, decision_engine):
        """Test prompt construction with OCR text"""
        command = "read screen"
        context = {"ocr_text": "Error: File not found"}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] read screen" in prompt
        assert "[TEXTO NA TELA] Error: File not found" in prompt

    def test_build_prompt_ocr_truncation(self, decision_engine):
        """Test that OCR text is truncated to 500 characters"""
        command = "summarize"
        long_text = "a" * 600
        context = {"ocr_text": long_text}

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] summarize" in prompt
        assert "[TEXTO NA TELA]" in prompt
        # The prompt should contain the first 500 chars of long_text
        assert "a" * 500 in prompt
        # And should NOT contain the full 600 chars
        assert "a" * 501 not in prompt

    def test_build_prompt_full_context(self, decision_engine):
        """Test prompt construction with all context elements"""
        command = "comprehensive test"
        context = {
            "user_face": "Jane",
            "user_emotion": "anxious",
            "memory_context": "Previously discussed X.",
            "ocr_text": "System Critical"
        }

        prompt = decision_engine._build_prompt(command, context)

        assert "[COMANDO] comprehensive test" in prompt
        assert "[VISÃO] Usuário identificado: Jane" in prompt
        assert "[EMOÇÃO] Usuário está: anxious" in prompt
        assert "Previously discussed X." in prompt
        assert "[TEXTO NA TELA] System Critical" in prompt

    def test_build_prompt_empty_context(self, decision_engine):
        """Test with None context or missing keys handled gracefully"""
        command = "just do it"
        # context could be empty
        context = {}
        prompt = decision_engine._build_prompt(command, context)
        assert "[COMANDO] just do it" in prompt
