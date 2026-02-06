"""
Indexador de Código para RAG (Knowledge Graph)
Varre o projeto para extrair conhecimento semântico e armazenar na memória neural.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from src.core.neural_memory import neural_memory
from src.utils.config import config

logger = logging.getLogger(__name__)

class CodebaseIndexer:
    """Class to scan and index project files for the Jarvis RAG system"""

    def __init__(self):
        self.project_root = Path(config.PROJECT_ROOT)
        self.supported_extensions = {'.py', '.md', '.json', '.txt', '.html', '.css', '.js'}
        self.exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.gemini', 'data'}

    def index_project(self):
        """Varre e indexa todos os arquivos suportados no projeto"""
        logger.info(f"Iniciando indexação do projeto: {self.project_root}")
        
        files_indexed = 0
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Filtrar diretórios excluídos
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.supported_extensions:
                        self._index_file(file_path)
                        files_indexed += 1
            
            logger.info(f"Indexação concluída. {files_indexed} arquivos processados.")
            return files_indexed
        except Exception as e:
            logger.error(f"Erro durante a indexação: {e}")
            return 0

    def _index_file(self, file_path: Path):
        """Lê e armazena o conteúdo de um arquivo na memória neural"""
        try:
            # Relativizar caminho para facilitar leitura da IA
            rel_path = file_path.relative_to(self.project_root)
            
            # Se for muito grande, quebrar em chunks (Simples por enquanto)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return

            # Dividir em chunks de ~1000 caracteres se necessário
            chunk_size = 1500
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source": str(rel_path),
                    "type": "codebase",
                    "chunk": i,
                    "language": file_path.suffix[1:]
                }
                
                header = f"Arquivo: {rel_path} (Fragmento {i+1})\n---\n"
                neural_memory.store_knowledge(str(rel_path), header + chunk, metadata)
                
        except Exception as e:
            logger.error(f"Erro ao indexar arquivo {file_path}: {e}")

# Instância global
codebase_indexer = CodebaseIndexer()

if __name__ == "__main__":
    # Teste de indexação
    logging.basicConfig(level=logging.INFO)
    codebase_indexer.index_project()
