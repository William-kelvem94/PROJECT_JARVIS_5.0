"""
Gerenciador de Arquivos e Documentos
Lê, organiza e gerencia arquivos de diferentes formatos
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from core.logger import logger

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 não disponível para leitura de PDFs")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx não disponível para leitura de Word")

class FileManager:
    """
    Gerenciador de arquivos com suporte a múltiplos formatos.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Inicializa o gerenciador de arquivos.
        
        Args:
            base_path: Diretório base para operações (padrão: diretório atual)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        logger.info(f"FileManager inicializado em: {self.base_path}")
    
    def read_file(self, file_path: str, max_chars: int = 10000) -> Dict[str, Any]:
        """
        Lê conteúdo de um arquivo.
        Suporta: .txt, .pdf, .docx, .json, .csv, .py, etc.
        
        Args:
            file_path: Caminho do arquivo
            max_chars: Número máximo de caracteres a retornar
        
        Returns:
            Conteúdo do arquivo
        """
        try:
            full_path = self.base_path / file_path if not os.path.isabs(file_path) else Path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {file_path}"
                }
            
            extension = full_path.suffix.lower()
            
            # Ler baseado na extensão
            if extension == ".pdf" and PDF_AVAILABLE:
                content = self._read_pdf(full_path)
            elif extension == ".docx" and DOCX_AVAILABLE:
                content = self._read_docx(full_path)
            elif extension in [".json"]:
                content = self._read_json(full_path)
            else:
                # Texto padrão
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Limitar tamanho
            if len(content) > max_chars:
                content = content[:max_chars] + "\n... (truncado)"
            
            return {
                "success": True,
                "content": content,
                "file_path": str(full_path),
                "size": len(content)
            }
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _read_pdf(self, file_path: Path) -> str:
        """Lê arquivo PDF."""
        content = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                content.append(page.extract_text())
        return "\n".join(content)
    
    def _read_docx(self, file_path: Path) -> str:
        """Lê arquivo DOCX."""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _read_json(self, file_path: Path) -> str:
        """Lê arquivo JSON."""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def list_directory(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Lista arquivos e diretórios.
        
        Args:
            directory: Diretório a listar (padrão: base_path)
        
        Returns:
            Lista de arquivos e diretórios
        """
        try:
            target_path = self.base_path / directory if directory else self.base_path
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Diretório não encontrado: {directory}"
                }
            
            items = []
            for item in sorted(target_path.iterdir()):
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "directory": str(target_path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            logger.error(f"Erro ao listar diretório: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def organize_files(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Organiza arquivos em pastas por tipo.
        
        Args:
            directory: Diretório a organizar (padrão: base_path)
        
        Returns:
            Resultado da organização
        """
        try:
            target_path = self.base_path / directory if directory else self.base_path
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Diretório não encontrado: {directory}"
                }
            
            # Mapeamento de extensões para pastas
            file_types = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
                "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
                "Music": [".mp3", ".wav", ".flac", ".ogg"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Code": [".py", ".js", ".html", ".css", ".java", ".cpp"],
            }
            
            moved = 0
            for item in target_path.iterdir():
                if item.is_file():
                    extension = item.suffix.lower()
                    
                    # Encontrar categoria
                    category = "Other"
                    for cat, exts in file_types.items():
                        if extension in exts:
                            category = cat
                            break
                    
                    # Criar pasta se não existir
                    category_path = target_path / category
                    category_path.mkdir(exist_ok=True)
                    
                    # Mover arquivo
                    destination = category_path / item.name
                    if destination.exists():
                        # Adicionar timestamp se já existir
                        stem = item.stem
                        destination = category_path / f"{stem}_{int(datetime.now().timestamp())}{item.suffix}"
                    
                    shutil.move(str(item), str(destination))
                    moved += 1
            
            return {
                "success": True,
                "action": "Organizar arquivos",
                "result": f"{moved} arquivos organizados em {str(target_path)}",
                "files_moved": moved
            }
        except Exception as e:
            logger.error(f"Erro ao organizar arquivos: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_files(self, pattern: str, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca arquivos por padrão.
        
        Args:
            pattern: Padrão de busca (nome ou extensão)
            directory: Diretório a buscar (padrão: base_path)
        
        Returns:
            Lista de arquivos encontrados
        """
        try:
            target_path = self.base_path / directory if directory else self.base_path
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Diretório não encontrado: {directory}"
                }
            
            found = []
            pattern_lower = pattern.lower()
            
            for item in target_path.rglob("*"):
                if item.is_file():
                    if pattern_lower in item.name.lower() or pattern_lower in item.suffix.lower():
                        found.append({
                            "path": str(item.relative_to(target_path)),
                            "name": item.name,
                            "size": item.stat().st_size
                        })
            
            return {
                "success": True,
                "pattern": pattern,
                "found": found,
                "count": len(found)
            }
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos: {e}")
            return {
                "success": False,
                "error": str(e)
            }

