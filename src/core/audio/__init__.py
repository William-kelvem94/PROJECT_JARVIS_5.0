"""
🔊 JARVIS Audio System - Sistema de Áudio
========================================

Este módulo contém todas as funcionalidades de processamento de áudio do JARVIS,
incluindo reconhecimento de voz, síntese de fala, processamento avançado de áudio
e controle de voz em tempo real.

Módulos Principais:
- voice_controller: Controle de voz principal
- voice_filter: Filtragem e processamento de voz
- advanced_speech_processor: Processamento avançado de fala
- realtime_transcription: Transcrição em tempo real
- enhanced_audio: Áudio aprimorado

Exemplo de uso:
    from src.core.audio import VoiceController, VoiceFilter

    voice = VoiceController()
    filter = VoiceFilter()
"""

from .voice_controller import VoiceController
from .voice_filter import AtomicVoiceFilter as VoiceFilter

# Lazy imports for heavy components
def __getattr__(name):
    if name == "AdvancedSpeechProcessor":
        try:
            from .advanced_speech_processor import AdvancedSpeechProcessor
            return AdvancedSpeechProcessor
        except ImportError as e:
            print(f"WARNING: AdvancedSpeechProcessor not available: {e}")
            return None
    elif name == "RealtimeTranscriber":
        try:
            from .realtime_transcription import RealtimeTranscriber
            return RealtimeTranscriber
        except ImportError as e:
            print(f"WARNING: RealtimeTranscriber not available: {e}")
            return None
    elif name == "EnhancedAudioSystem":
        try:
            from .enhanced_audio import EnhancedAudioSystem
            return EnhancedAudioSystem
        except ImportError as e:
            print(f"WARNING: EnhancedAudioSystem not available: {e}")
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Note: Dynamic attributes via __getattr__ handle the imports lazily
# to avoid heavy dependencies at startup.

__all__ = [
    'VoiceController',
    'VoiceFilter',
    'AdvancedSpeechProcessor',
    'RealtimeTranscriber',
    'EnhancedAudioSystem'
]
