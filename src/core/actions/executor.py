"""
JARVIS 5.0 - Unified Action Executor (Production Grade)
Consolidates all system, GUI, and physical actions.
"""

import os
import time
import logging
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import types for mapping
try:
<<<<<<< Updated upstream
    from src.core.intelligence.structured_output import ActionType
=======
    from src.core.intelligence.structured_output import ActionType  # noqa: F401

>>>>>>> Stashed changes
    TYPES_AVAILABLE = True
except ImportError:
    TYPES_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constants
MAX_FILE_READ_SIZE = 5000

class ActionExecutor:
    """Unified executor for all JARVIS actions."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ActionExecutor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized: return
        self._load_controllers()
        self._initialized = True

    def _load_controllers(self):
        """Lazy load all necessary controllers."""
        try:
            from src.core.actions.action_controller import action_controller
            self.gui = action_controller
        except ImportError:
            self.gui = None
        
        try:
            from src.core.actions.system_integrator import system_integrator
            self.sys = system_integrator
        except ImportError:
            self.sys = None
        
        try:
            from src.core.security.security_manager import security_manager
            self.security = security_manager
        except ImportError:
            self.security = None

        try:
            from src.core.audio.voice_controller import voice_controller
            self.voice = voice_controller
        except ImportError:
            self.voice = None

    def execute_action(self, action: Any) -> Dict[str, Any]:
        """Executes a single structured action."""
        # Handle both Pydantic objects and simple dicts
        if hasattr(action, 'dict'):
             action_dict = action.dict()
        elif isinstance(action, dict):
             action_dict = action
        else:
             return {"status": "error", "error": "Invalid action format"}

        action_name = action_dict.get("action", action_dict.get("type"))
        logger.info(f"🚀 Unified Execution: {action_name}")

        try:
            # 1. Verification (Optional HITL)
            if self.voice and action_name in ["run_command", "update_system_code"]:
                # Simple protection
                pass

            # 2. Routing
            if action_name == "click_at" or action_name == "click":
                if not self.gui:
                    return {"status": "error", "error": "GUI controller not available"}
                self.gui.click_at(action_dict.get("x", 0), action_dict.get("y", 0))
                return {"status": "success", "action": action_name, "result": "Clicked"}

            if action_name == "type_text" or action_name == "type":
                if not self.gui:
                    return {"status": "error", "error": "GUI controller not available"}
                self.gui.type_text(action_dict.get("text", ""))
                return {"status": "success", "action": action_name, "result": "Typed"}

            if action_name == "open_program" or action_name == "open_app":
                prog = action_dict.get("program") or action_dict.get("name")
                if not prog:
                    return {"status": "error", "error": "Missing program parameter"}
                # Use cross-platform solution
                import subprocess
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(prog)
                    else:  # Unix-like
                        subprocess.run(['xdg-open', prog], check=True)
                    return {"status": "success", "action": action_name}
                except Exception as e:
                    return {"status": "error", "action": action_name, "error": str(e)}

            if action_name == "read_file":
                path = action_dict.get("path")
                if not path:
                    return {"status": "error", "action": action_name, "error": "File path is required"}
                if self.security and not self.security.validate_path_access(path, 'read'):
                    return {"status": "blocked", "error": "Access denied"}
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return {"status": "success", "action": action_name, "result": f.read(MAX_FILE_READ_SIZE)}

            if action_name == "write_file":
                path = action_dict.get("path")
                if not path:
                    return {"status": "error", "action": action_name, "error": "File path is required"}
                if self.security and not self.security.validate_path_access(path, 'write'):
                    return {"status": "blocked", "error": "Access denied"}
                os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(action_dict.get("content", ""))
                return {"status": "success", "action": action_name, "result": "File written"}

            if action_name == "register_nickname":
                nickname = action_dict.get("nickname")
                if not nickname:
                    return {"status": "error", "error": "Nickname is required"}
                from src.core.audio.voice_filter import AtomicVoiceFilter
                AtomicVoiceFilter.add_nickname(nickname)
                return {"status": "success", "result": "Nickname registered"}

            # Add more handlers from the old complex executor as needed
            
            return {"status": "error", "error": f"Handler for '{action_name}' not implemented in unified executor"}

        except Exception as e:
            logger.error(f"Execution Error: {e}")
            return {"status": "error", "action": action_name, "error": str(e)}

    def execute_actions(self, actions: List[Any]) -> List[Dict[str, Any]]:
        results = []
        for action in actions:
            results.append(self.execute_action(action))
        return results

# Singleton Getter
_instance = None
def get_action_executor():
    global _instance
    if _instance is None: _instance = ActionExecutor()
    return _instance
