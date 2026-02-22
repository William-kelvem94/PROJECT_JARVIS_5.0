import os
import logging
from pathlib import Path
from ..utils.config import config
from ..core.agent import JarvisAgent

logger = logging.getLogger("JARVIS-SELF-FIX")

class SelfEvolution:
    """
    JARVIS Auto-Evolution Engine.
    Analyzes its own source code and applies fixes/improvements.
    """
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.agent = JarvisAgent() # Dedicated agent for self-analysis
        self.evolution_model = config.get("evolution_model", "deepseek-coder")

    def run_nightly_maintenance(self):
        """Analyzes logs and critical files for potential improvements."""
        logger.info("Starting Auto-Evolution cycle...")
        
        # 1. Check for logged errors
        errors = self._get_recent_errors()
        if errors:
            logger.info("Errors detected. Attempting self-repair...")
            self._attempt_repair(errors)
        else:
            logger.info("No critical errors found. JARVIS is stable.")

    def _get_recent_errors(self) -> str:
        log_path = self.root / "data" / "logs" / "errors.log"
        if log_path.exists():
            with open(log_path, 'r', encoding='utf-8') as f:
                return "".join(f.readlines()[-20:]) # Last 20 lines
        return ""

    def _attempt_repair(self, error_log: str):
        # This is where we'd send the code + error to the LLM
        # For the MVS, we log the attempt. Evolution will refine this.
        logger.warning(f"Self-repair logic triggered for errors: {error_log[:50]}...")
        # Future: agent.process("Repair this code based on error...")

# Function to be called during idle time
def start_evolution():
    ev = SelfEvolution(os.getcwd())
    ev.run_nightly_maintenance()
