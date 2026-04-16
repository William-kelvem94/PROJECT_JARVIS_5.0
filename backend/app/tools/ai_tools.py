import asyncio
import os
import subprocess
from ..livekit_stub import agents
from .base import BaseTool
from loguru import logger

class AITools(BaseTool):
    @agents.llm.function_tool(description="Consulta o Cérebro de Engenharia Local para tarefas complexas.")
    async def think_with_engineer_brain(self, task: str):
        from ..engineer_brain import brain
        asyncio.create_task(self._log_activity("Cérebro", f"Analisando: {task[:50]}", "info"))
        return await brain.reason(task)

    @agents.llm.function_tool(description="Modo God: Executa comando e auto-corrige código se falhar.")
    async def run_and_fix(self, command: str, target_file: str):
        attempt = 1
        max_attempts = 3
        while attempt <= max_attempts:
            asyncio.create_task(self._log_activity("God Mode", f"Tentativa {attempt}: {command}", "cmd"))
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return f"Sucesso na tentativa {attempt}!"
            
            last_error = (result.stdout or "") + (result.stderr or "")
            from ..engineer_brain import brain
            correction = await brain.reason(f"Conserte o erro em {target_file}:\n{last_error}")
            
            # Limpeza rápida de markdown
            if "```" in correction:
                correction = correction.split("```")[1].split("\n", 1)[1]
                if correction.endswith("```"): correction = correction[:-3]
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(correction.strip())
            attempt += 1
        return "Falha após 3 tentativas."
