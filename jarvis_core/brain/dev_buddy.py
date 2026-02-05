"""
Brain - Dev Buddy
Monitora código e sugere correções
"""

import logging
from pathlib import Path
from typing import Optional, List
import subprocess
import shutil

logger = logging.getLogger(__name__)

class DevBuddy:
    """Assistente de desenvolvimento"""
    
    def __init__(self):
        self.project_path = Path.cwd()
        self.monitoring = False
        
        logger.info("✅ Dev Buddy inicializado")
    
    def monitor_project(self, path: Optional[Path] = None):
        """Monitora arquivos Python"""
        if path:
            self.project_path = path
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class CodeHandler(FileSystemEventHandler):
                def on_modified(self, event):
                    if event.src_path.endswith('.py'):
                        logger.info(f"📝 Arquivo modificado: {event.src_path}")
            
            observer = Observer()
            observer.schedule(CodeHandler(), str(self.project_path), recursive=True)
            observer.start()
            
            self.monitoring = True
            logger.info(f"👁️ Monitorando: {self.project_path}")
            
        except ImportError:
            logger.warning("⚠️ watchdog não instalado")
    
    def intercept_error(self, stderr: str) -> Optional[str]:
        """Captura e analisa Traceback"""
        if "Traceback" not in stderr:
            return None
        
        logger.warning(f"🐛 Erro detectado:\n{stderr}")
        
        # Extrair informações do erro
        lines = stderr.split('\n')
        error_type = ""
        error_msg = ""
        
        for line in lines:
            if "Error:" in line or "Exception:" in line:
                error_type = line.strip()
            if line.strip() and not line.startswith(' '):
                error_msg = line.strip()
        
        return f"Erro: {error_type}\n{error_msg}"
    
    def suggest_fix(self, error: str) -> str:
        """Sugere correção usando LLM"""
        # Integrar com neural_router
        suggestion = f"Analisando erro: {error}\n"
        suggestion += "Sugestão: Verifique a sintaxe e imports."
        
        return suggestion
    
    def inject_code(self, file_path: Path, fix: str) -> bool:
        """Reescreve arquivo com correção"""
        if not file_path.exists():
            return False
        
        # Backup
        backup_path = file_path.with_suffix('.py.bak')
        shutil.copy(file_path, backup_path)
        
        try:
            # Aplicar fix (simplificado)
            with open(file_path, 'a') as f:
                f.write(f"\n# Auto-fix: {fix}\n")
            
            logger.info(f"✅ Código injetado em: {file_path}")
            logger.info(f"📦 Backup em: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao injetar código: {e}")
            # Restaurar backup
            shutil.copy(backup_path, file_path)
            return False
    
    def run_tests(self) -> bool:
        """Executa pytest"""
        try:
            result = subprocess.run(
                ["pytest", "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ Todos os testes passaram!")
                return True
            else:
                logger.warning(f"⚠️ Testes falharam:\n{result.stdout}")
                return False
                
        except FileNotFoundError:
            logger.warning("⚠️ pytest não instalado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao executar testes: {e}")
            return False


# Instância global
dev_buddy = DevBuddy()
