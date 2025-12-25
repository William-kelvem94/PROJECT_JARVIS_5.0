"""
JARVIS 5.0 - Assistente de Voz Inteligente
Um assistente de voz modular e extensível
"""

__version__ = "5.0.0"
__author__ = "JARVIS Team"
__description__ = "Assistente de voz inteligente com reconhecimento e síntese de fala natural"

from .core.assistant import JarvisAssistant
from .core.config import ConfigManager
from .voice.speech_engine import SpeechEngine
from .voice.recognition_engine import RecognitionEngine

__all__ = [
    'JarvisAssistant',
    'ConfigManager', 
    'SpeechEngine',
    'RecognitionEngine'
]
