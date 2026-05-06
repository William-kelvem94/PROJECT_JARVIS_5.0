import subprocess
import psutil
import json
import os
import asyncio
from .base import BaseTool
from loguru import logger
from app.system_control import system_control_matrix

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
            # Use the Matrix for consistent hardware telemetry
            res = system_control_matrix.get_hardware_status()
            if res["status"] == "success":
                return json.dumps(res["data"])
            return f"Erro: {res.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Erro: {e}"

    async def set_system_volume(self, level: float):
        """Sets the master system volume (0.0 to 1.0)."""
        res = system_control_matrix.set_volume(level)
        return json.dumps(res)

    async def set_system_brightness(self, level: int):
        """Sets the system screen brightness (0 to 100)."""
        res = system_control_matrix.set_brightness(level)
        return json.dumps(res)

    async def capture_screens(self):
        """Captures all connected monitors."""
        res = system_control_matrix.capture_screens()
        return json.dumps(res)

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
