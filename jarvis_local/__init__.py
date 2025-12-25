"""
JARVIS 5.0 - Sistema Local Completo
Sistema de IA 100% local e gratuito
"""

__version__ = "5.0.0"
__author__ = "JARVIS Local Team"

from .jarvis_core import JarvisCore
from .vision_local import LocalVisionProcessor, LocalFaceRecognition, LocalObjectDetection, LocalGestureRecognition
from .audio_local import LocalAudioProcessor, LocalSpeechRecognition, LocalTextToSpeech, LocalSpeakerDiarization

__all__ = [
    'JarvisCore',
    'LocalVisionProcessor',
    'LocalFaceRecognition',
    'LocalObjectDetection',
    'LocalGestureRecognition',
    'LocalAudioProcessor',
    'LocalSpeechRecognition',
    'LocalTextToSpeech',
    'LocalSpeakerDiarization'
]
