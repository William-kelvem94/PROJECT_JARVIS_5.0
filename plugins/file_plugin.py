# Plugin de Gerenciamento de Arquivos

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.logger import logger

class FilePlugin:
    """
    Plugin para gerenciamento de arquivos:
    - Ler arquivos
    - Listar diretórios
    - Organizar arquivos
    - Buscar arquivos
    """
    
    def __init__(self):
        self.home_dir = Path.home()
        self.desktop_dir = self.home_dir / "Desktop"
        self.downloads_dir = self.home_dir / "Downloads"
        logger.info("FilePlugin inicializado")
    
    def read_file(self, file_path: str, max_lines: int = 100) -> Dict[str, Any]:
        """Lê um arquivo e retorna seu conteúdo."""
        try:
            path = Path(file_path)
            
            # Se caminho relativo, tentar locais comuns
            if not path.is_absolute():
                possible_paths = [
                    self.desktop_dir / file_path,
                    self.downloads_dir / file_path,
                    Path.cwd() / file_path,
                    self.home_dir / file_path
                ]
                for p in possible_paths:
                    if p.exists():
                        path = p
                        break
            
            if not path.exists():
                return {
                    "success": False,
                    "action": f"Ler arquivo: {file_path}",
                    "result": f"Arquivo não encontrado: {file_path}"
                }
            
            # Ler baseado na extensão
            if path.suffix.lower() == '.txt' or path.suffix.lower() == '.md':
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    content = ''.join(lines[:max_lines])
                    if len(lines) > max_lines:
                        content += f"\n... (arquivo tem {len(lines)} linhas, mostrando primeiras {max_lines})"
                    return {
                        "success": True,
                        "action": f"Ler arquivo: {path.name}",
                        "result": content
                    }
            
            elif path.suffix.lower() in ['.json', '.py', '.js', '.html', '.css', '.xml']:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:5000]  # Limitar tamanho
                    return {
                        "success": True,
                        "action": f"Ler arquivo: {path.name}",
                        "result": content
                    }
            
            else:
                return {
                    "success": False,
                    "action": f"Ler arquivo: {path.name}",
                    "result": f"Tipo de arquivo não suportado para leitura: {path.suffix}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return {
                "success": False,
                "action": f"Ler arquivo: {file_path}",
                "result": f"Erro: {str(e)}"
            }
    
    def list_directory(self, directory: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Lista arquivos e pastas em um diretório."""
        try:
            if not directory:
                directory = str(self.desktop_dir)
            
            path = Path(directory)
            
            # Tentar locais comuns se não for absoluto
            if not path.is_absolute():
                possible_paths = [
                    self.desktop_dir / directory,
                    self.downloads_dir / directory,
                    Path.cwd() / directory,
                    self.home_dir / directory
                ]
                for p in possible_paths:
                    if p.exists() and p.is_dir():
                        path = p
                        break
            
            if not path.exists():
                return {
                    "success": False,
                    "action": f"Listar diretório: {directory}",
                    "result": f"Diretório não encontrado: {directory}"
                }
            
            items = []
            for item in sorted(path.iterdir())[:limit]:
                item_type = "" if item.is_dir() else ""
                size = ""
                if item.is_file():
                    try:
                        size_bytes = item.stat().st_size
                        if size_bytes < 1024:
                            size = f" ({size_bytes} B)"
                        elif size_bytes < 1024 * 1024:
                            size = f" ({size_bytes / 1024:.1f} KB)"
                        else:
                            size = f" ({size_bytes / (1024 * 1024):.1f} MB)"
                    except:
                        pass
                
                items.append(f"{item_type} {item.name}{size}")
            
            result = "\n".join(items)
            if len(list(path.iterdir())) > limit:
                result += f"\n... (mostrando {limit} de {len(list(path.iterdir()))} itens)"
            
            return {
                "success": True,
                "action": f"Listar: {path.name}",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar diretório: {e}")
            return {
                "success": False,
                "action": f"Listar diretório: {directory}",
                "result": f"Erro: {str(e)}"
            }
    
    def organize_files(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """Organiza arquivos por tipo em pastas."""
        try:
            if not directory:
                directory = str(self.desktop_dir)
            
            path = Path(directory)
            if not path.exists():
                return {
                    "success": False,
                    "action": "Organizar arquivos",
                    "result": f"Diretório não encontrado: {directory}"
                }
            
            # Criar pastas por tipo
            folders = {
                "Imagens": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
                "Documentos": ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                "Videos": ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
                "Musicas": ['.mp3', '.wav', '.flac', '.ogg'],
                "Arquivos": ['.zip', '.rar', '.7z', '.tar', '.gz'],
                "Executaveis": ['.exe', '.msi', '.deb', '.rpm']
            }
            
            moved_count = 0
            for file in path.iterdir():
                if file.is_file():
                    ext = file.suffix.lower()
                    for folder_name, extensions in folders.items():
                        if ext in extensions:
                            folder_path = path / folder_name
                            folder_path.mkdir(exist_ok=True)
                            shutil.move(str(file), str(folder_path / file.name))
                            moved_count += 1
                            break
            
            return {
                "success": True,
                "action": "Organizar arquivos",
                "result": f"Arquivos organizados! {moved_count} arquivo(s) movido(s)."
            }
            
        except Exception as e:
            logger.error(f"Erro ao organizar arquivos: {e}")
            return {
                "success": False,
                "action": "Organizar arquivos",
                "result": f"Erro: {str(e)}"
            }
    
    def search_files(self, pattern: str, directory: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """Busca arquivos por nome."""
        try:
            if not directory:
                directory = str(self.home_dir)
            
            path = Path(directory)
            if not path.exists():
                return {
                    "success": False,
                    "action": f"Buscar: {pattern}",
                    "result": f"Diretório não encontrado: {directory}"
                }
            
            found = []
            pattern_lower = pattern.lower()
            
            for file in path.rglob('*'):
                try:
                    if pattern_lower in file.name.lower():
                        found.append(str(file))
                        if len(found) >= limit:
                            break
                except (PermissionError, OSError):
                    continue
            
            if found:
                result = "\n".join(found[:limit])
                if len(found) > limit:
                    result += f"\n... (encontrados {len(found)} arquivos, mostrando {limit})"
            else:
                result = f"Nenhum arquivo encontrado com padrão '{pattern}'"
            
            return {
                "success": True,
                "action": f"Buscar: {pattern}",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos: {e}")
            return {
                "success": False,
                "action": f"Buscar: {pattern}",
                "result": f"Erro: {str(e)}"
            }

