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
from .advanced_speech_processor import AdvancedSpeechProcessor
from .realtime_transcription import RealtimeTranscriber
from .enhanced_audio import EnhancedAudioSystem

__all__ = [
    'VoiceController',
    'VoiceFilter',
    'AdvancedSpeechProcessor',
    'RealtimeTranscriber',
    'EnhancedAudioSystem'
]
