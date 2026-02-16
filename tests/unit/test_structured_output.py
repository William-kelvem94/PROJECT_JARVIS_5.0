import sys
import json
import pytest
import logging
from unittest.mock import MagicMock

# ============================================================================
# MOCKING DEPENDENCIES
# ============================================================================
# Prevent the heavy initialization of src.core.intelligence.__init__
sys.modules['src.core.intelligence.ai_agent'] = MagicMock()
sys.modules['src.core.intelligence.decision_engine'] = MagicMock()
sys.modules['src.core.intelligence.memory'] = MagicMock()
sys.modules['src.core.intelligence.context_sanitizer'] = MagicMock()
sys.modules['src.core.intelligence.neural_systems'] = MagicMock()
sys.modules['src.core.intelligence.perception_engine'] = MagicMock()
sys.modules['src.core.intelligence.knowledge_graph'] = MagicMock()

# Also mock winreg for Linux environments just in case
if sys.platform != "win32":
    sys.modules["winreg"] = MagicMock()

# Import the module under test
from src.core.intelligence.structured_output import ResponseParser, AgentResponse

class TestResponseParser:
    """Tests for ResponseParser resilience to malformed JSON and various inputs."""

    def test_valid_json(self):
        """Test parsing valid JSON response."""
        valid_json = json.dumps({
            "thought": "Valid JSON thought",
            "actions": [{"action": "wait", "seconds": 1.0}],
            "final_answer": "Valid JSON answer"
        })
        response = ResponseParser.parse_llm_response(valid_json)
        assert isinstance(response, AgentResponse)
        assert response.thought == "Valid JSON thought"
        assert len(response.actions) == 1
        assert response.actions[0].action == "wait"
        assert response.final_answer == "Valid JSON answer"

    def test_markdown_json(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        markdown_json = """
        Here is the response:
        ```json
        {
            "thought": "Markdown thought",
            "actions": [],
            "final_answer": "Markdown answer"
        }
        ```
        """
        response = ResponseParser.parse_llm_response(markdown_json)
        assert response.thought == "Markdown thought"
        assert response.final_answer == "Markdown answer"

    def test_markdown_no_lang(self):
        """Test parsing JSON wrapped in generic markdown code blocks."""
        markdown_json = """
        ```
        {
            "thought": "Generic markdown thought",
            "actions": [],
            "final_answer": "Generic markdown answer"
        }
        ```
        """
        response = ResponseParser.parse_llm_response(markdown_json)
        assert response.thought == "Generic markdown thought"
        assert response.final_answer == "Generic markdown answer"

    def test_malformed_json_resilience(self):
        """Test fallback behavior when JSON is malformed."""
        malformed_json = "{ 'invalid': 'json' "  # Missing closing brace, single quotes

        # Should fallback to text response containing the raw input
        # NOTE: Current implementation returns "Resposta não estruturada (Fallback para Texto)" for JSON errors
        # Future improvement might use _fallback_text_parse
        response = ResponseParser.parse_llm_response(malformed_json)

        # Accept either the current specific error message OR the generic fallback
        assert any(msg in response.thought for msg in [
            "Resposta não estruturada",
            "Fallback",
            "Resposta direta"
        ])

        # If the code changes to use _fallback_text_parse, response.final_answer will be the cleaned text
        # If it uses the current JSONDecodeError block, it also uses cleaned text
        assert "invalid" in response.final_answer

    def test_empty_response(self):
        """Test handling of empty or whitespace-only response."""
        response = ResponseParser.parse_llm_response("")
        assert "Resposta vazia" in response.thought

        response_none = ResponseParser.parse_llm_response(None)
        assert "Resposta vazia" in response_none.thought

    def test_legacy_regex_fallback(self):
        """Test fallback to legacy regex parsing when JSON fails but legacy actions are present."""
        # This input triggers JSONDecodeError
        legacy_text = "I will click here [ACTION: click_at(100, 200)]"

        response = ResponseParser.parse_llm_response(legacy_text)

        # We expect the parser to be smart enough to fallback to regex
        # even if it failed JSON decoding.
        # If this fails, it means the code needs to be improved to use _fallback_text_parse on JSON error.
        assert len(response.actions) == 1
        assert response.actions[0].action == "click_at"
        assert response.actions[0].x == 100
        assert response.actions[0].y == 200

    def test_extra_fields_ignored(self):
        """Test that extra fields in JSON are ignored (or handled gracefully)."""
        json_extra = json.dumps({
            "thought": "Thought",
            "actions": [],
            "final_answer": "Answer",
            "extra_field": "Should be ignored"
        })
        response = ResponseParser.parse_llm_response(json_extra)
        assert response.thought == "Thought"

    def test_missing_fields_validation(self):
        """Test validation error when required fields are missing."""
        # Missing 'thought'
        json_missing = json.dumps({
            "actions": [],
            "final_answer": "Answer"
        })
        # Pydantic validation error raises Exception -> catch in parser -> fallback to text
        response = ResponseParser.parse_llm_response(json_missing)

        # The fallback logic for Exception uses _fallback_text_parse
        assert "Resposta direta" in response.thought or "Fallback" in response.thought
        assert "Answer" in response.final_answer

    def test_action_validation_error(self):
        """Test validation error for invalid action parameters."""
        # 'wait' requires 'seconds'
        json_invalid_action = json.dumps({
            "thought": "Invalid action",
            "actions": [{"action": "wait"}],
            "final_answer": "Answer"
        })

        response = ResponseParser.parse_llm_response(json_invalid_action)
        # Should fallback because Pydantic validation fails
        assert "Resposta direta" in response.thought or "Fallback" in response.thought

    def test_json_decode_error_logging(self, caplog):
        """Verify that JSONDecodeError is logged."""
        malformed = "{ invalid }"
        with caplog.at_level(logging.ERROR):
            ResponseParser.parse_llm_response(malformed)

        assert "JSON inválido do LLM" in caplog.text or "Erro ao validar resposta" in caplog.text
