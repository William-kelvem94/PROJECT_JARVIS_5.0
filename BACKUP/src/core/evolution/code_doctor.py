import logging
import re
import os
from pathlib import Path
from typing import List, Dict, Optional
import difflib

from src.utils.config import config
from src.core.intelligence.brain_router import brain_router

# We need a safe way to edit files.
# Ideally use a specialized prompt for the LLM.

logger = logging.getLogger(__name__)


class CodeDoctor:
    """
    The System's Auto-Surgeon.
    Analyzes logs, identifies crashing code, and attempts to patch it autonomously.
    """

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(os.getcwd())
        self.logs_dir = self.project_root / "data" / "logs"
        self.max_fixes_per_cycle = 3

    def heal_system(self):
        """Main entry point for self-healing procedure."""
        logger.info("⚕️ CodeDoctor: Starting diagnostic scan...")

        errors = self._scan_logs_for_errors()
        if not errors:
            logger.info("✅ CodeDoctor: No critical errors found in recent logs.")
            return

        logger.info(f"found {len(errors)} unique errors. Attempting triage.")

        fixed_count = 0
        for error in errors[: self.max_fixes_per_cycle]:
            if self._attempt_fix(error):
                fixed_count += 1

        logger.info(f"⚕️ CodeDoctor: Cycle complete. Applied {fixed_count} fixes.")

    def _scan_logs_for_errors(self) -> List[Dict]:
        """Scans log files for Python tracebacks and extracting file paths."""
        unique_errors = {}

        # Look for jarvis logging files
        log_files = list(self.logs_dir.glob("*.log"))

        # Regex to find tracebacks: File "...", line X, in ...
        # traceback_pattern = re.compile(r'File "([^"]+)", line (\d+), in (.*)\n(.*)\n(\w+Error: .*)')

        # Simplified regex to capture the last frame of a traceback which is usually the culprit
        # We look for "File "src...", line X" and capture context

        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Split by error blocks (simplistic)
                # Find "Traceback (most recent call last):"
                traceback_blocks = content.split("Traceback (most recent call last):")

                for block in traceback_blocks[1:]:  # Skip preamble
                    # Extract the Last "File" entry before the Error Message
                    lines = block.strip().split("\n")

                    # Find the error message (last line usually)
                    error_msg = lines[-1]

                    # Find the last file reference that belongs to OUR project
                    # (src/)
                    culprit = None
                    for line in reversed(lines[:-1]):
                        if 'File "' in line and "src" in line:
                            # Parse: File "c:\...\src\...", line 123, infunc
                            match = re.search(r'File "([^"]+)", line (\d+)', line)
                            if match:
                                file_path = match.group(1)
                                line_num = int(match.group(2))
                                culprit = {
                                    "file": file_path,
                                    "line": line_num,
                                    "error": error_msg,
                                    "traceback": block[:500],  # Limit context
                                }
                                break

                    if culprit:
                        # Create unique key
                        key = f"{culprit['file']}:{culprit['line']}:{culprit['error']}"
                        if key not in unique_errors:
                            unique_errors[key] = culprit

            except Exception as e:
                logger.warning(f"Failed to read log {log_file}: {e}")

        return list(unique_errors.values())

    def _attempt_fix(self, error_info: Dict) -> bool:
        """Consults the LLM to fix the specific error."""
        file_path = Path(error_info["file"])

        if not file_path.exists():
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            code_context = "".join(lines)

            # Construct Prompt
            prompt = f"""
            SYSTEM ALERT: AUTOMONOUS REPAIR SEQUENCE

            I have encountered a CRITICAL ERROR in my source code.

            ERROR: {error_info['error']}
            LOCATION: {file_path} at line {error_info['line']}

            TRACEBACK SNIPPET:
            {error_info['traceback']}

            FULL FILE CONTENT:
            ```python
            {code_context}
            ```

            TASK:
            Return the FIXED version of the code.
            The fix must resolve the specific error mentioned.
            Do not remove functionality.

            OUTPUT FORMAT:
            Return ONLY the full python code block. No explanations.
            """

            # Call Brain (Synchronous for now, or assume async wrapper available)
            # We need to bridge to AIAgent or BrainRouter.
            # For simplicity, we assume we can call an LLM service here.

            # Import locally to avoid circular dep
            from src.core.intelligence.ai_agent import ai_agent
            import asyncio

            # Run LLM
            logger.info(f"Asking Brain for fix on {file_path.name}...")

            # Create a new event loop for this sync call if needed, or use
            # existing
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                # We are likely inside an async loop (DreamCycle might be async?)
                # If DreamCycle calls this from a thread, we can use run_until_complete on a new loop
                # If we are in the main thread loop, we must schedule it.
                # Assuming DreamCycle runs in a separate thread:
                fixed_code_raw = asyncio.run(
                    ai_agent._call_ollama_async(prompt, model="deepseek-r1:14b")
                )
            else:
                fixed_code_raw = loop.run_until_complete(
                    ai_agent._call_ollama_async(prompt, model="deepseek-r1:14b")
                )

            # Extract code from Markdown
            fixed_code = self._extract_code(fixed_code_raw)
            if not fixed_code:
                logger.warning("Brain returned no code.")
                return False

            if fixed_code == code_context:
                logger.info("Brain proposed no changes.")
                return False

            # SAFETY CHECK: Syntax
            try:
                compile(fixed_code, str(file_path), "exec")
            except SyntaxError as e:
                logger.error(f"Proposed fix has Syntax Error: {e}")
                return False

            # APPLY FIX
            backup_path = file_path.with_suffix(file_path.suffix + ".bak.doctor")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(code_context)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)

            logger.info(
                f"✅ APPLIED FIX to {file_path.name}. Backup at {backup_path.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Fix attempt failed: {e}")
            return False

    def _extract_code(self, text: str) -> str:
        pattern = r"```python(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: if no backticks, assume whole text if it looks like code
        if "def " in text or "import " in text:
            return text
        return ""


# Singleton
code_doctor = CodeDoctor()
