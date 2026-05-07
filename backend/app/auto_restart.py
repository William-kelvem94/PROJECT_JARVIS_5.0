"""
JARVIS 5.0 — Auto-Restart System on Improvements
================================================
Sistema de monitoramento e restart automático quando melhorias são detectadas.
Monitora arquivos críticos e reinicia o sistema quando mudanças são feitas.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Set, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from loguru import logger


class JarvisRestartHandler(FileSystemEventHandler):
    """Handler que monitora mudanças e reinicia o JARVIS."""
    
    def __init__(self, restart_callback):
        super().__init__()
        self.restart_callback = restart_callback
        self.last_restart = time.time()
        self.cooldown = 5  # segundos de cooldown entre restarts
        self.pending_restart = False
        
        # Padrões de arquivos críticos que devem acionar restart
        self.critical_patterns = {
            "*.py",  # Arquivos Python
            "requirements*.txt",  # Dependências
            ".env",  # Configurações
            "setup.py",  # Setup
        }
        
        # Arquivos/diretórios a ignorar
        self.ignore_patterns = {
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "venv",
            "node_modules",
            ".git",
            "logs",
            "temp_audio",
            "data/screenshots",
            "data/captures",
            ".pyc",
        }
    
    def should_ignore(self, path: str) -> bool:
        """Verifica se o arquivo deve ser ignorado."""
        path_obj = Path(path)
        
        # Ignora padrões específicos
        for pattern in self.ignore_patterns:
            if pattern in str(path_obj):
                return True
        
        return False
    
    def should_trigger_restart(self, path: str) -> bool:
        """Verifica se a mudança deve acionar restart."""
        if self.should_ignore(path):
            return False
        
        path_obj = Path(path)
        
        # Verifica se o arquivo corresponde aos padrões críticos
        for pattern in self.critical_patterns:
            if path_obj.match(pattern):
                return True
        
        return False
    
    def on_modified(self, event):
        """Chamado quando um arquivo é modificado."""
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            if self.should_trigger_restart(event.src_path):
                current_time = time.time()
                
                # Verifica cooldown
                if current_time - self.last_restart > self.cooldown:
                    logger.info(f"[AutoRestart] Critical file modified: {event.src_path}")
                    self.pending_restart = True
                    self.schedule_restart()
    
    def schedule_restart(self):
        """Agenda um restart do sistema."""
        if self.pending_restart:
            time.sleep(2)  # Wait a bit for file system to stabilize
            
            if self.pending_restart:  # Check again after wait
                logger.warning("[AutoRestart] Initiating system restart due to code changes...")
                self.last_restart = time.time()
                self.pending_restart = False
                self.restart_callback()


def restart_jarvis():
    """Reinicia o processo do JARVIS."""
    logger.info("[AutoRestart] Restarting JARVIS process...")
    
    try:
        # Get the original command that started JARVIS
        python_exe = sys.executable
        script_path = sys.argv[0]
        
        # If running in uvicorn, restart uvicorn
        if "uvicorn" in sys.argv[0] or any("uvicorn" in arg for arg in sys.argv):
            logger.info("[AutoRestart] Detected uvicorn, restarting server...")
            subprocess.Popen([python_exe, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        else:
            # Restart the script
            subprocess.Popen([python_exe, script_path] + sys.argv[1:])
        
        # Exit current process
        logger.info("[AutoRestart] Terminating old process...")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"[AutoRestart] Failed to restart: {e}")


def start_auto_restart_monitor(watch_paths: list = None):
    """
    Inicia o monitor de auto-restart.
    
    Args:
        watch_paths: Lista de caminhos para monitorar. Se None, monitora o diretório do backend.
    """
    if watch_paths is None:
        # Default: monitor backend directory
        backend_path = Path(__file__).resolve().parent
        watch_paths = [str(backend_path)]
    
    observer = Observer()
    handler = JarvisRestartHandler(restart_jarvis)
    
    for path in watch_paths:
        if os.path.exists(path):
            observer.schedule(handler, path, recursive=True)
            logger.info(f"[AutoRestart] Monitoring {path} for changes")
        else:
            logger.warning(f"[AutoRestart] Path does not exist: {path}")
    
    observer.start()
    logger.success("[AutoRestart] Auto-restart monitoring active")
    
    return observer


def create_restart_script():
    """Cria um script batch para reiniciar o JARVIS manualmente."""
    root_dir = Path(__file__).resolve().parents[2]
    restart_script_path = root_dir / "restart-jarvis.bat"
    
    script_content = """@echo off
echo ========================================
echo JARVIS 5.0 - Manual Restart Script
echo ========================================
echo.
echo Stopping current JARVIS processes...

REM Kill existing JARVIS processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq JARVIS*" 2>nul
taskkill /F /IM node.exe /FI "WINDOWTITLE eq JARVIS*" 2>nul

echo.
echo Waiting for cleanup...
timeout /t 3 /nobreak >nul

echo.
echo Starting JARVIS...
call start-jarvis.bat

echo.
echo JARVIS restart initiated!
pause
"""
    
    try:
        restart_script_path.write_text(script_content, encoding="utf-8")
        logger.success(f"[AutoRestart] Restart script created at: {restart_script_path}")
    except Exception as e:
        logger.error(f"[AutoRestart] Failed to create restart script: {e}")


# Global observer instance
_observer = None


def get_observer():
    """Retorna a instância global do observer."""
    global _observer
    return _observer


def enable_auto_restart():
    """Ativa o sistema de auto-restart."""
    global _observer
    
    if _observer is not None:
        logger.warning("[AutoRestart] Auto-restart already enabled")
        return
    
    # Create restart script
    create_restart_script()
    
    # Start monitoring
    backend_path = Path(__file__).resolve().parent
    root_path = backend_path.parent
    
    watch_paths = [
        str(backend_path),  # Backend code
        str(root_path / "scripts"),  # Scripts
        str(root_path / "env"),  # Environment configs
    ]
    
    _observer = start_auto_restart_monitor(watch_paths)


def disable_auto_restart():
    """Desativa o sistema de auto-restart."""
    global _observer
    
    if _observer is not None:
        _observer.stop()
        _observer.join()
        _observer = None
        logger.info("[AutoRestart] Auto-restart monitoring disabled")
    else:
        logger.warning("[AutoRestart] Auto-restart is not enabled")


# Check for environment variable to enable auto-restart
if os.getenv("JARVIS_AUTO_RESTART", "0") == "1":
    logger.info("[AutoRestart] JARVIS_AUTO_RESTART=1 detected, enabling auto-restart on startup")
