"""
ActionValidator (O Sentinela)

- Intercepta/valida ações sensíveis (edição/exclusão/execução)
- Politica por padrão: "Automático + checks" (sintaxe, whitelist/blacklist, backup)
- Para ações críticas publica um evento ACTION_APPROVAL_REQUEST no EventBus
  (integração com UI/tests). Não aplica mudanças automaticamente sem aprovação.

API mínima:
- validate(action: dict) -> ValidationResult

Designed to be conservative and easy to unit-test.
"""
from __future__ import annotations

import ast
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.infrastructure.async_event_bus import (
    get_event_bus,
    Event,
    EventType,
    EventPriority,
)

logger = logging.getLogger(__name__)

DEFAULT_PROTECTED = [
    "main.py",
    "src",
    "config",
    "scripts",
    "requirements.txt",
]


@dataclass
class ValidationResult:
    approved: bool
    requires_approval: bool = False
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

class ActionValidator:
    def __init__(self, protected_paths: Optional[List[str]] = None):
        self.protected_paths = protected_paths or DEFAULT_PROTECTED

    def _is_path_protected(self, target: str) -> bool:
        try:
            p = Path(target)
            # quick name-based checks (supports both absolute & relative)
            s = str(p)
            for protected in self.protected_paths:
                if protected in s or s.endswith(protected):
                    return True
            return False
        except Exception:
            return True

    def _python_syntax_ok(self, code: str) -> tuple[bool, Optional[str]]:
        try:
            ast.parse(code)
            return True, None
        except Exception as e:
            return False, str(e)

    def _publish_approval_request(self, action: Dict[str, Any]) -> Optional[str]:
        bus = get_event_bus()
        try:
            # publish using the EventType enum directly (simpler / more robust)
            event_id = bus.publish(EventType.ACTION_APPROVAL_REQUEST, {"action": action}, source="action_validator", priority=EventPriority.CRITICAL)
            return event_id
        except Exception:
            # best-effort: if bus not running, still return requires_approval
            logger.debug("ActionValidator: failed to publish approval request (bus may be stopped)")
            return None

    def validate(self, action: Dict[str, Any]) -> ValidationResult:
        """Validate a proposed action.

        action: {
          "action_type": "file_modify"|"file_delete"|"exec_command",
          "target": "/abs/or/relative/path" or command string,
          "proposed_code": "..." (optional)
          ...
        }

        Returns ValidationResult. If requires_approval=True the caller should
        not apply the change until a human/operator approves via the EventBus/UI.
        """
        action_type = action.get("action_type")
        target = action.get("target")

        # Basic sanity
        if not action_type or not target:
            return ValidationResult(False, False, "invalid-action", {})

        # Protect critical paths
        protected = False
        try:
            protected = self._is_path_protected(str(target))
        except Exception:
            protected = True

        # Delete/rename on protected paths: block + require approval
        if action_type in ("file_delete", "file_rename") and protected:
            request_id = self._publish_approval_request(action)
            return ValidationResult(False, True, "protected-path", {"target": target}, request_id=request_id)

        # Modification of protected paths: require explicit approval
        if action_type == "file_modify" and protected:
            # allow only after explicit human approval
            request_id = self._publish_approval_request(action)
            return ValidationResult(False, True, "protected-path-modify", {"target": target}, request_id=request_id)

        # If modifying python files, run a syntax check
        if action_type == "file_modify" and (str(target).endswith(".py") or action.get("proposed_code")):
            code = action.get("proposed_code") or ""
            ok, err = self._python_syntax_ok(code)
            if not ok:
                return ValidationResult(False, False, f"syntax-error: {err}", {})

        # Exec commands: be conservative — require approval for commands touching FS
        if action_type == "exec_command":
            cmd = str(target)
            if any(tok in cmd for tok in ["rm ", "del ", "format ", "shutdown", "reboot"]):
                self._publish_approval_request(action)
                return ValidationResult(False, True, "dangerous-exec", {"cmd": cmd})

        # Default: pass automated checks and approve
        return ValidationResult(True, False, None, {})


# singleton
action_validator = ActionValidator()
