import os
import subprocess
import pyautogui
import time
from loguru import logger

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
        """Executa um comando direto no CMD/PowerShell."""
        try:
            logger.info(f"💻 JARVIS executando comando: {command}")
            subprocess.Popen(command, shell=True)
            return f"Comando '{command}' enviado ao terminal."
        except Exception as e:
            return f"Erro de execução: {e}"

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
