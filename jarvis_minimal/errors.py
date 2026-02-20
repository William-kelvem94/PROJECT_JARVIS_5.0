import logging
import time
import os
import json
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ErrorCollector:
    def __init__(self, log_path: str = "data/error_report.json"):
        self.log_path = log_path
        self.errors = []

    def report(self, module: str, error: Exception, context: Dict = None):
        err_msg = str(error)
        entry = {
            "ts": time.time(),
            "module": module,
            "error": err_msg,
            "type": type(error).__name__,
            "context": context or {}
        }
        self.errors.append(entry)
        logger.error(f"[{module}] {entry['type']}: {err_msg}")
        self._save()
        self._check_for_autofix(entry)

    def _save(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(self.errors[-100:], f, indent=4, ensure_ascii=False)
        except:
            pass

    def _check_for_autofix(self, entry: Dict):
        # Logic to suggest fixes or write to autofix/ directory
        suggestion_dir = "autofix"
        os.makedirs(suggestion_dir, exist_ok=True)
        
        # Simple heuristic: if it's a module error, suggest pip install
        if "ModuleNotFoundError" in entry["type"]:
            pkg = entry["error"].split("'")[1]
            fix_msg = f"Sugestão: instale o pacote '{pkg}' usando 'pip install {pkg}'"
            with open(os.path.join(suggestion_dir, f"fix_{int(entry['ts'])}.txt"), "w") as f:
                f.write(fix_msg)

# Global instance
errors = ErrorCollector()
