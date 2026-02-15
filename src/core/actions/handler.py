"""
JARVIS 5.0 - Unified Action Handler (Production Grade)
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from src.core.actions.executor import get_action_executor

logger = logging.getLogger(__name__)

class ActionHandler:
    """Orchestrates action parsing and execution."""
    
    def __init__(self):
        self.executor = get_action_executor()

    def handle_llm_output(self, raw_output: str) -> Dict[str, Any]:
        """Entry point for LLM response processing."""
        try:
            # 1. Try JSON Parse
            data = self._parse_json(raw_output)
            if data:
                actions = data.get("actions", [])
                results = self.executor.execute_actions(actions)
                return {
                    "success": True,
                    "thought": data.get("thought"),
                    "results": results,
                    "final_answer": data.get("final_answer")
                }
            
            # 2. Try Legacy Regex Parse if JSON fails
            legacy_actions = self.parse_legacy_actions(raw_output)
            if legacy_actions:
                results = self.executor.execute_actions(legacy_actions)
                return {"success": True, "results": results, "final_answer": raw_output}

            return {"success": False, "error": "No actions found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_actions_sync(self, actions: List[Any]) -> List[Dict[str, Any]]:
        """Unified async execution for AIAgent compatibility."""
        if not actions: return []
        
        processed_actions = []
        for action in actions:
            if isinstance(action, str):
                # If it's a raw LLM block, parse it
                res = self.handle_llm_output(action)
                if res.get("success"):
                     processed_actions.extend(res.get("results", []))
            else:
                # If it's already a structured object
                processed_actions.append(self.executor.execute_action(action))
        return processed_actions

    def _parse_json(self, text: str) -> Optional[Dict]:
        try:
            # Look for JSON blocks
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(text)
        except:
            return None

    def parse_legacy_actions(self, text: str) -> List[Dict[str, Any]]:
        """Extract [ACTION: ...] patterns."""
        actions = []
        matches = re.findall(r"\[ACTION: (.*?)\]", text)
        for cmd in matches:
            # Simple mapping for legacy commands
            if "click_at" in cmd:
                coords = re.findall(r"\d+", cmd)
                if len(coords) >= 2:
                    actions.append({"type": "click_at", "x": int(coords[0]), "y": int(coords[1])})
            elif "read_file" in cmd:
                path = re.search(r"['\"](.*?)['\"]", cmd)
                if path: actions.append({"type": "read_file", "path": path.group(1)})
            # ... add more legacy mappings as needed
        return actions

# Singleton
_handler = None
def get_action_handler():
    global _handler
    if _handler is None: _handler = ActionHandler()
    return _handler
