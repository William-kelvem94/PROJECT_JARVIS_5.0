"""
Leitor de Tela Inteligente - Pacote Principal
Sistema avançado para captura, processamento e análise de dados da tela
"""

__version__ = "1.0.0"
__author__ = "Desenvolvedor"
__description__ = "Sistema avançado para captura, processamento e análise inteligente de dados da tela"

# Imports principais para facilitar uso
from .utils.config import config
from .core.screen_capture import screen_capture
from .core.ocr_processor import ocr_processor
from .core.data_analyzer import data_analyzer
from .core.data_organizer import data_organizer

__all__ = [
    'config',
    'screen_capture',
    'ocr_processor',
    'data_analyzer',
    'data_organizer'
]
