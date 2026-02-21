import logging
from typing import Callable, Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, Callable] = {}
        self._prefixes: Dict[str, Callable] = {}

    def register(self, keywords: List[str], is_prefix: bool = False):
        def decorator(func: Callable):
            for kw in keywords:
                kw_l = kw.lower().strip()
                if is_prefix:
                    self._prefixes[kw_l] = func
                else:
                    self._commands[kw_l] = func
            return func
        return decorator

    def find_command(self, text: str) -> Optional[tuple[Callable, str]]:
        low = text.lower().strip()
        
        # Match exact commands first
        if low in self._commands:
            return self._commands[low], ""

        # Match prefixes
        for prefix, func in self._prefixes.items():
            if low.startswith(prefix):
                args = text[len(prefix):].strip()
                return func, args
        
        return None

# Global instance
registry = CommandRegistry()

def command(keywords: List[str], is_prefix: bool = False):
    return registry.register(keywords, is_prefix)
