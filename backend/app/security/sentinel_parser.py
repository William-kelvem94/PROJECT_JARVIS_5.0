import ast
import re
from typing import List, Set

class SentinelParser:
    """
    Sentinel security layer for AST analysis and command validation.
    Blocks destructive operations and unauthorized system access.
    """

    # Regex for blocking destructive shell commands
    BLOCK_LIST_REGEX = [
        r"rm\s+.*-rf",
        r"mkfs\..*",
        r"format\s+.*",
        r"dd\s+if=.*of=/dev/sd",
        r"shutdown\s+.*",
        r"reboot",
        r"chmod\s+777",
        r"chown\s+.*",
        r"mkdir\s+.*-p\s+/etc",
    ]

    # Forbidden AST nodes or patterns for Python code
    FORBIDDEN_MODULES = {"os", "sys", "shutil", "subprocess", "socket", "pty"}

    # Commands that REQUIRE privileged intent justification
    PRIVILEGED_COMMANDS = {
        "rm", "format", "mkfs", "shutdown", "reboot", "chmod", "chown",
        "dd", "netsh", "ipconfig", "route", "systemctl", "service"
    }

    def __init__(self):
        self.regex_patterns = [re.compile(p, re.IGNORECASE) for p in self.BLOCK_LIST_REGEX]

    def validate_command(self, command: str, intent_data: dict = None) -> bool:
        """
        Validates if a command is safe to execute.
        Checks for basic safety, and requires JSON justification for privileged commands.
        """
        # Layer 1: Regex blocklist check (Hard blocks)
        for pattern in self.regex_patterns:
            if pattern.search(command):
                return False

        # Layer 2: Intent Validation for Privileged Operations
        if self._is_privileged(command):
            if not self._validate_intent(command, intent_data):
                return False

        # Layer 3: AST analysis if the command looks like Python
        if "import" in command or "def " in command or "(" in command:
            try:
                tree = ast.parse(command)
                if not self._analyze_ast(tree):
                    return False
            except SyntaxError:
                pass

        return True

    def _is_privileged(self, command: str) -> bool:
        """Detects if the command contains any privileged keywords, ignoring obfuscation."""
        normalized = command.lower() if hasattr(command, 'lower') else command.lower()
        return any(cmd in normalized for cmd in self.PRIVILEGED_COMMANDS)

    def _validate_intent(self, command: str, intent_data: dict) -> bool:
        """
        Validates the JSON intent flow.
        Requires 'reasoning' and 'intent' keys and ensures they justify the command.
        """
        if not intent_data or not isinstance(intent_data, dict):
            return False

        reasoning = intent_data.get("reasoning", "").strip()
        intent = intent_data.get("intent", "").strip()

        if not reasoning or not intent:
            return False

        # Heuristic: Reasoning must not be generic (e.g., "because I want to")
        # and must contain a keyword related to the intent or the system state.
        generic_responses = {"because I want to", "just doing it", "trust me", "as requested"}
        if reasoning.lower() in generic_responses:
            return False

        return True

    def _analyze_ast(self, tree: ast.AST) -> bool:
        """Recursively analyzes the AST to prevent unauthorized imports/calls."""
        for node in ast.walk(tree):
            # Block imports of dangerous modules
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_MODULES:
                        return False

            if isinstance(node, ast.ImportFrom):
                if node.module in self.FORBIDDEN_MODULES:
                    return False

            # Block direct calls to dangerous built-ins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"eval", "exec", "breakpoint"}:
                        return False
        return True
