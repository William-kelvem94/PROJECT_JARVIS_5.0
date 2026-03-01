import os
import subprocess
import psutil
import json
from loguru import logger
from livekit import agents
from typing import Optional
import datetime

class SystemTools:
    """
    Ferramentas de Sistema para o JARVIS.
    Permite ao agente interagir com o computador, ler arquivos e executar comandos.
    """

    def __init__(self, room: Optional[agents.Room] = None):
        self._room = room
        from .utils.log_manager import log_manager
        from .utils.workflow_engine import workflow_engine
        self._log_manager = log_manager
        self._workflow_engine = workflow_engine

    async def _log_activity(self, title: str, detail: str, log_type: str = "info", status: str = "success"):
        """Envia o log para o frontend via LiveKit e salva no disco."""
        entry = {
            "type": "activity_log",
            "title": title,
            "detail": detail,
            "log_type": log_type,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 1. Salva no disco (Persistência)
        self._log_manager.save_log(entry)
        
        # 2. Envia para o frontend (Real-time)
        if self._room and self._room.connection_state == "connected":
            try:
                await self._room.local_participant.publish_data(
                    json.dumps(entry),
                    topic="activity"
                )
            except Exception as e:
                logger.error(f"Falha ao publicar log de atividade: {e}")

    @agents.llm.function_tool(description="Lista a estrutura de arquivos do projeto ou de um diretório específico.")
    def project_structure(self, path: str = "."):
        try:
            items = os.listdir(path)
            structure = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    structure.append(f"📁 {item}/")
                else:
                    structure.append(f"📄 {item}")
            structure_str = "\n".join(structure)
            asyncio.create_task(self._log_activity("Listar Projeto", f"Caminho: {path}", "info"))
            return structure_str
        except Exception as e:
            logger.error(f"Erro ao listar diretório: {e}")
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Lê o conteúdo de um arquivo específico.")
    def read_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                asyncio.create_task(self._log_activity("Ler Arquivo", f"Arquivo: {file_path}", "edit"))
                return content
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            return f"Erro ao ler arquivo: {str(e)}"

    @agents.llm.function_tool(description="Escreve ou modifica o conteúdo de um arquivo.")
    def write_file(self, file_path: str, content: str):
        try:
            # Garantir que o diretório pai existe
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.success(f"Arquivo {file_path} escrito com sucesso.")
            asyncio.create_task(self._log_activity("Escrever Arquivo", f"Arquivo: {file_path}", "edit"))
            return f"Arquivo {file_path} atualizado."
        except Exception as e:
            logger.error(f"Erro ao escrever no arquivo {file_path}: {e}")
            return f"Erro ao escrever: {str(e)}"

    @agents.llm.function_tool(description="Executa um comando no terminal do sistema OPERACIONAL WINDOWS.")
    def execute_command(self, command: str):
        try:
            logger.info(f"Executando comando: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            asyncio.create_task(self._log_activity("Terminal", f"Comando: {command}", "cmd", "success" if result.returncode == 0 else "error"))
            return f"Saída do comando:\n{output}"
        except subprocess.TimeoutExpired:
            return "Erro: O comando demorou muito para responder (Timeout)."
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Obtém estatísticas de hardware do sistema (CPU, RAM, Bateria).")
    def get_system_stats(self):
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            batt_pct = battery.percent if battery else "N/A"
            
            stats = {
                "cpu_usage_percent": cpu,
                "ram_usage_percent": ram,
                "battery_percent": batt_pct,
                "os": os.name
            }
            return json.dumps(stats, indent=2)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Realiza operações básicas de Git (status, commit, push - use com cautela).")
    def git_operation(self, action: str, message: str = ""):
        if action == "status":
            return self.execute_command("git status")
        elif action == "commit":
            if not message: return "Erro: Mensagem de commit necessária."
            return self.execute_command(f'git add . && git commit -m "{message}"')
        elif action == "push":
            asyncio.create_task(self._log_activity("Git Push", "Enviando alterações...", "git"))
            return self.execute_command("git push")
        else:
            return "Ação Git não suportada."

    @agents.llm.function_tool(description="Registra uma nova macro (sequência de tarefas) para execução futura.")
    def register_macro(self, name: str, description: str, steps: str):
        """
        Steps deve ser uma string JSON contendo uma lista de comandos ou ferramentas.
        """
        try:
            steps_list = json.loads(steps)
            if self._workflow_engine.register_macro(name, steps_list):
                asyncio.create_task(self._log_activity("Macro Registrada", f"Nome: {name} - {description}", "info"))
                return f"Macro '{name}' salva e pronta para o combate."
            return "Erro ao salvar macro."
        except Exception as e:
            return f"Erro no formato das ferramentas: {str(e)}"

    @agents.llm.function_tool(description="Executa uma macro previamente registrada pelo nome.")
    async def run_macro(self, name: str):
        macro = self._workflow_engine.get_macro(name)
        if not macro:
            return f"Erro: Macro '{name}' não encontrada."
        
        asyncio.create_task(self._log_activity("Executando Macro", f"Iniciando sequência: {name}", "info"))
        
        results = []
        for step in macro:
            # Por simplicidade inicial, as macros executam comandos de terminal
            if isinstance(step, str):
                res = self.execute_command(step)
                results.append(f"Step: {step} -> {res[:50]}...")
            elif isinstance(step, dict) and "cmd" in step:
                res = self.execute_command(step["cmd"])
                results.append(f"Step: {step['cmd']} -> {res[:50]}...")
        

    @agents.llm.function_tool(description="Configura um monitoramento (watchdog) para um arquivo ou condição específica.")
    def set_watchdog(self, name: str, type: str, target: str):
        """
        type: 'file' (monitora alteração de data de modificação)
        target: caminho do arquivo
        """
        if self._workflow_engine.add_watchdog(name, {"type": type, "target": target}):
            asyncio.create_task(self._log_activity("Watchdog Ativado", f"Monitorando {type}: {target}", "info"))
            return f"Watchdog '{name}' configurado. Vou te avisar se algo mudar."
        return "Erro ao configurar watchdog."

