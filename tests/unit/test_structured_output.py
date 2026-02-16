"""
Tests for Structured Output Intelligence
"""

import sys
import os
import importlib.util
from unittest.mock import MagicMock

# Import the module directly by path to avoid triggering package initialization
# which pulls in heavy dependencies (PyQt6, psutil, winreg, etc.) via src.core.intelligence.__init__
file_path = os.path.abspath("src/core/intelligence/structured_output.py")
spec = importlib.util.spec_from_file_location("structured_output", file_path)
structured_output = importlib.util.module_from_spec(spec)
sys.modules["structured_output"] = structured_output
spec.loader.exec_module(structured_output)

# Now import from the loaded module
from structured_output import (
    ResponseParser, AgentResponse, ActionType,
    ClickAction, TypeTextAction, PressKeyAction, HotkeyAction
)

import pytest
import json

class TestResponseParser:
    """Tests for ResponseParser"""

    def test_parse_valid_json(self):
        """Test parsing a valid JSON response"""
        raw_response = json.dumps({
            "thought": "I need to click a button",
            "actions": [
                {"action": "click_at", "x": 100, "y": 200, "button": "left", "clicks": 1}
            ],
            "final_answer": "Clicked the button"
        })

        response = ResponseParser.parse_llm_response(raw_response)

        assert isinstance(response, AgentResponse)
        assert response.thought == "I need to click a button"
        assert len(response.actions) == 1
        assert isinstance(response.actions[0], ClickAction)
        assert response.actions[0].x == 100
        assert response.actions[0].y == 200
        assert response.final_answer == "Clicked the button"

    def test_parse_markdown_json(self):
        """Test parsing JSON wrapped in markdown code blocks"""
        raw_response = """
Here is the plan:
```json
{
    "thought": "Typing text",
    "actions": [
        {"action": "type_text", "text": "Hello World", "interval": 0.1}
    ],
    "final_answer": "Typed Hello World"
}
```
        """
        response = ResponseParser.parse_llm_response(raw_response)

        assert isinstance(response, AgentResponse)
        assert response.thought == "Typing text"
        assert len(response.actions) == 1
        assert isinstance(response.actions[0], TypeTextAction)
        assert response.actions[0].text == "Hello World"

    def test_parse_markdown_generic(self):
        """Test parsing JSON wrapped in generic markdown code blocks"""
        raw_response = """
```
{
    "thought": "Pressing a key",
    "actions": [
        {"action": "press_key", "key": "enter", "presses": 1}
    ],
    "final_answer": "Pressed enter"
}
```
        """
        response = ResponseParser.parse_llm_response(raw_response)

        assert isinstance(response, AgentResponse)
        assert response.thought == "Pressing a key"
        assert len(response.actions) == 1
        assert isinstance(response.actions[0], PressKeyAction)
        assert response.actions[0].key == "enter"

    def test_parse_empty_response(self):
        """Test parsing empty or None response"""
        response_none = ResponseParser.parse_llm_response(None) # type: ignore
        assert response_none.thought == "Resposta vazia do modelo"
        assert response_none.actions == []

        response_empty = ResponseParser.parse_llm_response("   ")
        assert response_empty.thought == "Resposta vazia do modelo"
        assert response_empty.actions == []

    def test_parse_invalid_json_fallback(self):
        """Test fallback for invalid JSON (plain text)"""
        raw_response = "This is not JSON but a plain text response."

        response = ResponseParser.parse_llm_response(raw_response)

        # When JSON parsing fails, it returns a specific thought and the text as final_answer
        assert response.thought == "Resposta não estruturada (Fallback para Texto)"
        assert response.final_answer == "This is not JSON but a plain text response."
        assert response.actions == []

    def test_action_limit(self):
        """Test validation limit of 10 actions"""
        actions = []
        for i in range(15):
            actions.append({"action": "wait", "seconds": 1.0})

        raw_response = json.dumps({
            "thought": "Many actions",
            "actions": actions,
            "final_answer": "Done"
        })

        response = ResponseParser.parse_llm_response(raw_response)

        assert len(response.actions) == 10
        assert response.actions[0].action == ActionType.WAIT

    def test_legacy_regex_direct(self):
        """Test legacy regex parsing by calling static method directly"""
        text = "Please [ACTION: click_at 100 200] and then [ACTION: type_text 'Hello']"

        response = ResponseParser._legacy_regex_parse(text)

        assert response.thought == "Raciocínio não estruturado (legado)"
        assert len(response.actions) == 2

        assert isinstance(response.actions[0], ClickAction)
        assert response.actions[0].x == 100
        assert response.actions[0].y == 200

        assert isinstance(response.actions[1], TypeTextAction)
        assert response.actions[1].text == "Hello"

        assert response.final_answer == "Please  and then" or "Please  and then" in response.final_answer

    def test_validation_error_fallback(self):
        """Test fallback when JSON is valid but schema is invalid"""
        # Valid JSON but missing required fields (e.g. final_answer)
        raw_response = json.dumps({
            "thought": "Missing final answer",
            "actions": []
        })

        response = ResponseParser.parse_llm_response(raw_response)

        # Should hit Exception -> _fallback_text_parse -> plain text
        assert response.thought == "Resposta direta sem raciocínio estruturado"
        assert response.actions == []
        # The fallback uses the raw response as final answer
        assert response.final_answer == raw_response
