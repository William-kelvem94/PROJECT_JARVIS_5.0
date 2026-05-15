import asyncio
import os
import subprocess
from pathlib import Path
from .base import BaseTool
from .system_os_tools import _validate_command
from loguru import logger

class AITools(BaseTool):
    _sandbox_root = Path(
        os.getenv("JARVIS_FILE_SANDBOX_ROOT", Path(__file__).resolve().parents[3])
    ).resolve()

    def _safe_target_file(self, target_file: str) -> Path:
        candidate = Path(target_file)
        if not candidate.is_absolute():
            candidate = self._sandbox_root / candidate
        resolved = candidate.resolve(strict=False)
        if os.path.commonpath([str(self._sandbox_root), str(resolved)]) != str(self._sandbox_root):
            raise ValueError("Arquivo alvo fora do sandbox.")
        return resolved

    async def think_with_engineer_brain(self, task: str):
        from ..engineer_brain import brain
        asyncio.create_task(self._log_activity("Cérebro", f"Analisando: {task[:50]}", "info"))
        return await brain.reason(task)

    async def run_and_fix(self, command: str, target_file: str):
        safe_target = self._safe_target_file(target_file)
        command_parts = _validate_command(command)
        attempt = 1
        max_attempts = 3
        while attempt <= max_attempts:
            asyncio.create_task(self._log_activity("God Mode", f"Tentativa {attempt}: {command}", "cmd"))
            result = subprocess.run(command_parts, shell=False, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return f"Sucesso na tentativa {attempt}!"
            
            last_error = (result.stdout or "") + (result.stderr or "")
            from ..engineer_brain import brain
            correction = await brain.reason(f"Conserte o erro em {safe_target}:\n{last_error}")
            
            # Limpeza rápida de markdown
            if "```" in correction:
                correction = correction.split("```")[1].split("\n", 1)[1]
                if correction.endswith("```"): correction = correction[:-3]
            
            with open(safe_target, "w", encoding="utf-8") as f:
                f.write(correction.strip())
            attempt += 1
        return "Falha após 3 tentativas."
