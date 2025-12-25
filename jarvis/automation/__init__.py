"""
Módulo de Automação Avançada do JARVIS 5.0
Controle total do sistema Windows e automação inteligente
"""

from .windows_controller import WindowsController
from .file_manager import AdvancedFileManager
from .web_automation import WebAutomation
from .system_monitor import SystemMonitor
from .task_scheduler import TaskScheduler

__all__ = [
    'WindowsController',
    'AdvancedFileManager',
    'WebAutomation', 
    'SystemMonitor',
    'TaskScheduler'
]
