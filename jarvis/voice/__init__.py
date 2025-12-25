"""
Voice processing modules for JARVIS
"""

from .speech_engine import SpeechEngine
from .recognition_engine import RecognitionEngine
from .natural_speech import NaturalSpeechProcessor

__all__ = ['SpeechEngine', 'RecognitionEngine', 'NaturalSpeechProcessor']
