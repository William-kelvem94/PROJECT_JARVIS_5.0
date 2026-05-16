import os
import subprocess
import pyautogui
import time
from loguru import logger

# Whitelist de prefixos de comandos seguros permitidos pelo JARVIS.
# Qualquer comando que nao comece com um destes prefixos sera bloqueado.
COMMAND_WHITELIST = [
    # Navegacao e arquivos
    "explorer", "notepad", "code",
    # Utilitarios do sistema (leitura)
    "ipconfig", "ping", "whoami", "hostname", "systeminfo", "tasklist",
    "dir", "echo", "type", "ver",
    # Midia e apps comuns
    "mspaint", "calc", "mplay32", "wmplayer", "spotify",
    # Python e Node (contexto dev)
    "python", "node", "pnpm", "npm",
    # Atalhos do Windows
    "start ", "cmd /c echo",
]

class SystemExecutor:
    """
    O braço físico do JARVIS no Windows.
    Permite abrir aplicativos, controlar janelas e gerenciar o sistema.
    """
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    def open_app(self, app_name: str):
        """Tenta abrir um aplicativo pelo nome via menu iniciar."""
        try:
            logger.info(f"🚀 JARVIS abrindo aplicativo: {app_name}")
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write(app_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            return f"Iniciando {app_name}, chefe."
        except Exception as e:
            logger.error(f"Erro ao abrir app: {e}")
            return "Falhei ao tentar acessar o sistema operacional."

    def run_command(self, command: str):
        """Executa um comando no sistema, validado contra whitelist de seguranca."""
        cmd_lower = command.strip().lower()

        # Bloqueia padroes destrutivos independentemente da whitelist
        BLOCKED_PATTERNS = [
            "rm ", "del ", "rmdir", "format", "reg delete", "rd /s",
            "shutdown", "taskkill", "net user", "netsh", "cipher /w",
            "powershell -enc", "powershell -e ", "cmd /c del",
        ]
        for blocked in BLOCKED_PATTERNS:
            if blocked in cmd_lower:
                logger.warning(f"🚫 Comando bloqueado por seguranca: {command}")
                return f"Comando recusado por politica de seguranca: padrao proibido detectado."

        # Verifica se comeca com prefixo permitido
        allowed = any(cmd_lower.startswith(prefix.lower()) for prefix in COMMAND_WHITELIST)
        if not allowed:
            logger.warning(f"🚫 Comando fora da whitelist: {command}")
            return (
                f"Comando '{command}' nao esta na lista de comandos permitidos. "
                "Se quiser executar algo especifico, me diga o que deseja fazer."
            )

        try:
            logger.info(f"💻 JARVIS executando comando: {command}")
            subprocess.Popen(command, shell=False)  # safer without shell
            return f"Comando '{command}' enviado ao terminal."
        except Exception as e:
            return f"Erro de execucao: {e}"

    def system_status_report(self):
        """Retorna um relatório proativo de saúde do PC."""
        import psutil
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        if cpu > 80:
            return "ALERTA: O processador está sob carga extrema. Recomendo fechar processos pesados."
        if ram > 90:
            return "ALERTA: A memória RAM está quase esgotada. Possível lentidão iminente."
        return "Sistemas operando dentro da normalidade."

system_executor = SystemExecutor()
