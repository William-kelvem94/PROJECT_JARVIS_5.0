"""
Sistema de logging para JARVIS
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """Sistema de logging configurável para JARVIS"""
    
    def __init__(self, name: str = "JARVIS", level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """Configura handlers de console e arquivo"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo (se especificado)
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"Não foi possível criar arquivo de log: {e}")
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log de informação"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log de erro"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log crítico"""
        self.logger.critical(message)
    
    def voice_event(self, event_type: str, details: str = ""):
        """Log específico para eventos de voz"""
        self.info(f"VOICE_EVENT: {event_type} - {details}")
    
    def command_event(self, command: str, status: str = "executed"):
        """Log específico para comandos"""
        self.info(f"COMMAND: {command} - {status}")
    
    def performance_log(self, operation: str, duration: float):
        """Log de performance"""
        self.debug(f"PERFORMANCE: {operation} took {duration:.3f}s")


# Instância global padrão
default_logger = Logger()
