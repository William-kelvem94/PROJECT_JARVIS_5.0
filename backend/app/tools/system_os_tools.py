import subprocess
import psutil
import json
import os
import asyncio
from .base import BaseTool
from loguru import logger

class SystemOSTools(BaseTool):
    async def execute_command(self, command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            asyncio.create_task(self._log_activity("Terminal", f"Comando: {command}", "cmd", "success" if result.returncode == 0 else "error"))
            return f"Saída:\n{output}"
        except Exception as e:
            return f"Erro: {str(e)}"

    async def get_system_stats(self):
        try:
            stats = {
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "N/A"
            }
            return json.dumps(stats)
        except Exception as e:
            return f"Erro: {e}"

    async def open_application(self, app_name: str):
        try:
            subprocess.Popen(app_name, shell=True)
            asyncio.create_task(self._log_activity("Abrir App", f"Iniciando: {app_name}", "cmd"))
            return f"App '{app_name}' iniciado."
        except Exception as e:
            return f"Erro: {e}"
            
    async def git_operation(self, action: str, message: str = ""):
        if action == "status":
            return await self.execute_command("git status")
        elif action == "commit":
            return await self.execute_command(f'git add . && git commit -m "{message}"')
        elif action == "push":
            return await self.execute_command("git push")
        return "Ação não suportada."
