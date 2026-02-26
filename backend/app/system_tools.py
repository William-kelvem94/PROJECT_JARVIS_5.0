import subprocess
import os
import psutil
import platform
from livekit.agents import llm
from loguru import logger
from .engineer_brain import brain
from duckduckgo_search import DDGS

class SystemTools(llm.FunctionSet):
    """
    Ferramentas de sistema para o JARVIS controlar o hardware e o ambiente do usuário.
    """

    @llm.ai_callable(description="Executa um comando no terminal (PowerShell) do sistema.")
    def run_terminal_command(self, command: str):
        logger.info(f"JARVIS executando comando: {command}")
        try:
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return f"Comando executado com sucesso:\n{result.stdout}"
            else:
                return f"Erro ao executar comando:\n{result.stderr}"
        except Exception as e:
            return f"Falha catastrófica ao rodar o comando: {str(e)}"

    @llm.ai_callable(description="Retorna o status atual do hardware (CPU, RAM, Bateria).")
    def get_system_stats(self):
        logger.info("JARVIS coletando estatísticas do sistema.")
        cpu_pct = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        info = (
            f"Status do Sistema:\n"
            f"- CPU: {cpu_pct}%\n"
            f"- RAM: {ram.percent}% ({ram.used // (1024**2)}MB usados de {ram.total // (1024**2)}MB)\n"
        )
        if battery:
            info += f"- Bateria: {battery.percent}% ({'Carregando' if battery.power_plugged else 'Descarregando'})\n"
        
        info += f"- SO: {platform.system()} {platform.release()}"
        return info

    @llm.ai_callable(description="Lista os arquivos em uma pasta específica.")
    def list_files(self, path: str = "."):
        logger.info(f"JARVIS listando arquivos em: {path}")
        try:
            files = os.listdir(path)
            return f"Arquivos em {path}:\n" + "\n".join(files)
        except Exception as e:
            return f"Não consegui ler a pasta: {str(e)}"

    @llm.ai_callable(description="Lê o conteúdo de um arquivo de texto.")
    def read_file_content(self, file_path: str):
        logger.info(f"JARVIS lendo arquivo: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read(2000) # Aumentado para 2000 para dar mais contexto ao engenheiro
                return f"Conteúdo de {file_path}:\n{content}"
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

    @llm.ai_callable(description="Aplica uma alteração de código ou escreve um arquivo novo.")
    def apply_code_change(self, file_path: str, content: str, mode: str = "w"):
        """
        mode 'w' para sobrescrever, 'a' para anexar.
        """
        logger.info(f"JARVIS alterando arquivo: {file_path} (Modo: {mode})")
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            return f"Arquivo {file_path} atualizado com sucesso."
        except Exception as e:
            return f"Falha ao escrever no arquivo: {str(e)}"

    @llm.ai_callable(description="Executa operações Git (status, add, commit, push).")
    def git_operation(self, operation: str, message: str = ""):
        logger.info(f"JARVIS operando Git: {operation}")
        cmd = f"git {operation}"
        if operation == "commit" and message:
            cmd = f'git commit -m "{message}"'
        
        try:
            result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            return f"Git Output:\n{result.stdout}\n{result.stderr}"
        except Exception as e:
            return f"Erro no Git: {str(e)}"

    @llm.ai_callable(description="Consulta o Núcleo de Engenharia (OpenRouter) para resolver problemas complexos de código.")
    async def think_with_engineer_brain(self, task: str, file_context: str = ""):
        logger.info(f"JARVIS acionando raciocínio profundo para: {task}")
        # Se não houver contexto, tentamos ler os arquivos principais
        if not file_context:
            file_context = "Estrutura do projeto:\n" + self.list_files(".")
            
        reply = await brain.reason(task, file_context)
        return f"💡 Resposta do Núcleo de Engenharia:\n{reply}"

    @llm.ai_callable(description="Mapeia toda a estrutura de pastas do projeto JARVIS.")
    def project_structure(self):
        logger.info("JARVIS mapeando estrutura do projeto.")
        structure = []
        for root, dirs, files in os.walk("."):
            # Ignorar pastas irrelevantes
            if any(x in root for x in ["node_modules", ".git", "__pycache__", ".venv", "venv", ".next"]):
                continue
            level = root.replace(".", "").count(os.sep)
            indent = " " * 4 * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for f in files:
                structure.append(f"{sub_indent}{f}")
        
        return "Estrutura do Projeto:\n" + "\n".join(structure)

    @llm.ai_callable(description="Pesquisa na internet usando DuckDuckGo para obter informações atualizadas.")
    def web_search(self, query: str):
        logger.info(f"JARVIS pesquisando na web: {query}")
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=5):
                    results.append(f"Título: {r['title']}\nLink: {r['href']}\nResumo: {r['body']}\n")
            
            if not results:
                return "Não encontrei resultados relevantes na internet."
            return "\n---\n".join(results)
        except Exception as e:
            return f"Erro ao pesquisar na web: {str(e)}"
