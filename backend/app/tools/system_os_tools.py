import subprocess
import psutil
import json
import os
import asyncio
import shlex
from .base import BaseTool
from loguru import logger
from app.system_control import system_control_matrix


BLOCKED_TOKENS = {
    "rm",
    "del",
    "erase",
    "rmdir",
    "rd",
    "format",
    "shutdown",
    "taskkill",
    "reg",
    "netsh",
    "cipher",
}

SHELL_META = {"&&", "||", "|", ";", ">", ">>", "<"}

ALLOWED_COMMANDS = {
    "git": {"status", "diff", "log", "show", "branch", "rev-parse", "ls-files"},
    "python": {"-m"},
    "py": {"-m"},
    "node": {"--version", "-v"},
    "pnpm": {"--version", "-v", "test", "build", "exec", "run"},
    "npm": {"--version", "-v", "test", "run"},
    "where": None,
    "whoami": None,
    "hostname": None,
    "ipconfig": None,
    "ping": None,
}

ALLOWED_PYTHON_MODULES = {"pytest", "py_compile", "compileall"}
ALLOWED_APPLICATIONS = {"explorer", "notepad", "calc", "mspaint", "code"}


def _split_command(command: str) -> list[str]:
    return shlex.split(command, posix=(os.name != "nt"))


def _validate_command(command: str) -> list[str]:
    parts = _split_command(command)
    if not parts:
        raise ValueError("Comando vazio.")

    lowered = [part.lower() for part in parts]
    if any(token in SHELL_META for token in lowered):
        raise ValueError("Operadores de shell não são permitidos.")
    if any(token in BLOCKED_TOKENS for token in lowered):
        raise ValueError("Comando bloqueado por política de segurança.")

    executable = lowered[0]
    allowed_subcommands = ALLOWED_COMMANDS.get(executable)
    if executable not in ALLOWED_COMMANDS:
        raise ValueError(f"Comando não permitido: {parts[0]}")

    if allowed_subcommands is None:
        return parts

    if len(parts) < 2:
        raise ValueError(f"Subcomando obrigatório para {parts[0]}.")

    subcommand = lowered[1]
    if subcommand not in allowed_subcommands:
        raise ValueError(f"Subcomando não permitido: {parts[0]} {parts[1]}")

    if executable in {"python", "py"}:
        if len(parts) < 3 or lowered[2] not in ALLOWED_PYTHON_MODULES:
            raise ValueError("Apenas módulos Python de teste/compilação são permitidos.")

    return parts


class SystemOSTools(BaseTool):
    async def execute_command(self, command: str):
        try:
            result = subprocess.run(_validate_command(command), shell=False, capture_output=True, text=True, timeout=30)
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
            parts = _split_command(app_name)
            if not parts or parts[0].lower() not in ALLOWED_APPLICATIONS:
                return f"Aplicativo '{app_name}' não está na allowlist."
            subprocess.Popen(parts, shell=False)
            asyncio.create_task(self._log_activity("Abrir App", f"Iniciando: {app_name}", "cmd"))
            return f"App '{app_name}' iniciado."
        except Exception as e:
            return f"Erro: {e}"

    async def git_operation(self, action: str, message: str = ""):
        if action == "status":
            return await self.execute_command("git status")
        elif action == "commit":
            subprocess.run(["git", "add", "."], shell=False, check=False)
            result = subprocess.run(["git", "commit", "-m", message], shell=False, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            return f"Saída:\n{output}"
        elif action == "push":
            result = subprocess.run(["git", "push"], shell=False, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            return f"Saída:\n{output}"
        return "Ação não suportada."
