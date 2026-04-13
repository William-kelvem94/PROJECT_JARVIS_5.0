import os
import asyncio
from livekit import agents
from .base import BaseTool
from loguru import logger

class FileTools(BaseTool):
    @agents.llm.function_tool(description="Lista a estrutura de arquivos do COMPUTADOR ou de um diretório específico. Use caminhos absolutos para acessar qualquer pasta do sistema.")
    async def list_files(self, path: str = "."):
        try:
            items = os.listdir(path)
            structure = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    structure.append(f"📁 {item}/")
                else:
                    structure.append(f"📄 {item}")
            asyncio.create_task(self._log_activity("Explorar Sistema", f"Caminho: {path}", "info"))
            return "\n".join(structure)
        except Exception as e:
            return f"Erro: {str(e)}"

    @agents.llm.function_tool(description="Lê o conteúdo de um arquivo específico.")
    async def read_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                asyncio.create_task(self._log_activity("Ler Arquivo", f"Arquivo: {file_path}", "edit"))
                return content
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

    @agents.llm.function_tool(description="Escreve ou modifica o conteúdo de um arquivo.")
    async def write_file(self, file_path: str, content: str):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            asyncio.create_task(self._log_activity("Escrever Arquivo", f"Arquivo: {file_path}", "edit"))
            return f"Arquivo {file_path} atualizado."
        except Exception as e:
            return f"Erro ao escrever: {str(e)}"

    @agents.llm.function_tool(description="Aplica uma mudança cirúrgica: substitui um trecho por outro.")
    async def apply_code_change(self, file_path: str, old_code: str, new_code: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_code not in content:
                return f"Erro: trecho não encontrado em {file_path}"
            new_content = content.replace(old_code, new_code, 1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            asyncio.create_task(self._log_activity("Code Change", f"Alterado: {file_path}", "edit"))
            return f"Alteração aplicada em {file_path}."
        except Exception as e:
            return f"Erro: {e}"
