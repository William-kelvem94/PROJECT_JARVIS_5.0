import os
import asyncio
from pathlib import Path
from .base import BaseTool
from loguru import logger

class FileTools(BaseTool):
    _sandbox_root = Path(
        os.getenv("JARVIS_FILE_SANDBOX_ROOT", Path(__file__).resolve().parents[3])
    ).resolve()
    _blocked_parts = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".next",
        "__pycache__",
        ".pytest_cache",
    }

    def _safe_path(self, user_path: str) -> Path:
        candidate = Path(user_path)
        if not candidate.is_absolute():
            candidate = self._sandbox_root / candidate
        resolved = candidate.resolve(strict=False)
        root = self._sandbox_root
        if os.path.commonpath([str(root), str(resolved)]) != str(root):
            raise ValueError("Acesso fora do sandbox permitido.")
        if any(part in self._blocked_parts for part in resolved.parts):
            raise ValueError("Caminho bloqueado pelo sandbox.")
        return resolved

    async def list_files(self, path: str = "."):
        try:
            safe_path = self._safe_path(path)
            items = os.listdir(safe_path)
            structure = []
            for item in items:
                full_path = os.path.join(str(safe_path), item)
                if os.path.isdir(full_path):
                    structure.append(f"📁 {item}/")
                else:
                    structure.append(f"📄 {item}")
            asyncio.create_task(self._log_activity("Explorar Sistema", f"Caminho: {safe_path}", "info"))
            return "\n".join(structure)
        except Exception as e:
            return f"Erro: {str(e)}"

    async def read_file(self, file_path: str):
        try:
            safe_path = self._safe_path(file_path)
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read()
                asyncio.create_task(self._log_activity("Ler Arquivo", f"Arquivo: {safe_path}", "edit"))
                return content
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

    async def write_file(self, file_path: str, content: str):
        try:
            safe_path = self._safe_path(file_path)
            os.makedirs(safe_path.parent, exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            asyncio.create_task(self._log_activity("Escrever Arquivo", f"Arquivo: {safe_path}", "edit"))
            return f"Arquivo {safe_path} atualizado."
        except Exception as e:
            return f"Erro ao escrever: {str(e)}"

    async def apply_code_change(self, file_path: str, old_code: str, new_code: str):
        try:
            safe_path = self._safe_path(file_path)
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_code not in content:
                return f"Erro: trecho não encontrado em {safe_path}"
            new_content = content.replace(old_code, new_code, 1)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            asyncio.create_task(self._log_activity("Code Change", f"Alterado: {safe_path}", "edit"))
            return f"Alteração aplicada em {safe_path}."
        except Exception as e:
            return f"Erro: {e}"
