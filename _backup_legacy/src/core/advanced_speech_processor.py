"""
Advanced Speech Processing - Processamento de Voz Neural
Integra Whisper para STT e prepara para XTTS-v2 TTS
"""

import logging
import os
import wave
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
import threading
import time

logger = logging.getLogger(__name__)

class AdvancedSpeechProcessor:
    """Processador avançado de voz com Whisper e TTS neural"""
    
    def __init__(self):
        self.whisper_available = False
        self.whisper_model = None
        self.whisper_model_size = "base"  # tiny, base, small, medium, large
        
        self.tts_available = False
        self.tts_engine = None
        
        self._init_whisper()
        self._init_tts()
    
    def _init_whisper(self):
        """Inicializa Whisper para STT"""
        try:
            import whisper
            
            # Tentar carregar modelo (começar com base)
            logger.info(f"Carregando Whisper modelo '{self.whisper_model_size}'...")
            self.whisper_model = whisper.load_model(self.whisper_model_size)
            self.whisper_available = True
            logger.info(f"✅ Whisper inicializado ({self.whisper_model_size})")
            
        except ImportError:
            logger.warning("⚠️ Whisper não disponível. Instale: pip install openai-whisper")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar Whisper: {e}")
    
    def _init_tts(self):
        """Inicializa TTS (preparação para XTTS-v2)"""
        try:
            # Por enquanto, usar pyttsx3 como fallback
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configurar voz em português se disponível
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # Configurar velocidade e volume
            self.tts_engine.setProperty('rate', 180)  # Velocidade
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            self.tts_available = True
            logger.info("✅ TTS inicializado (pyttsx3)")
            
        except Exception as e:
            logger.warning(f"⚠️ TTS não disponível: {e}")
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "pt",
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcreve áudio usando Whisper
        
        Args:
            audio_path: Caminho do arquivo de áudio
            language: Idioma ('pt', 'en', etc)
            task: 'transcribe' ou 'translate'
        
        Returns:
            Dicionário com texto e metadados
        """
        if not self.whisper_available:
            return {
                "error": "Whisper não disponível",
                "text": "",
                "fallback": True
            }
        
        try:
            logger.info(f"Transcrevendo áudio: {audio_path}")
            
            # Transcrever com Whisper
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                task=task,
                fp16=False  # CPU mode
            )
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "duration": self._get_audio_duration(audio_path),
                "model": self.whisper_model_size
            }
            
        except Exception as e:
            logger.error(f"Erro ao transcrever: {e}")
            return {
                "error": str(e),
                "text": "",
                "fallback": True
            }
    
    def transcribe_realtime(
        self,
        audio_stream,
        callback,
        language: str = "pt"
    ):
        """
        Transcrição em tempo real (experimental)
        
        Args:
            audio_stream: Stream de áudio
            callback: Função chamada com cada transcrição
            language: Idioma
        """
        # TODO: Implementar transcrição em tempo real
        # Requer buffer circular e processamento incremental
        logger.warning("Transcrição em tempo real ainda não implementada")
    
    def speak(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        async_mode: bool = False
    ) -> bool:
        """
        Sintetiza fala a partir de texto
        
        Args:
            text: Texto para falar
            voice: Voz a usar
            speed: Velocidade (0.5 - 2.0)
            async_mode: Se True, não bloqueia
        
        Returns:
            True se sucesso
        """
        if not self.tts_available:
            logger.warning("TTS não disponível")
            return False
        
        try:
            # Ajustar velocidade
            base_rate = 180
            self.tts_engine.setProperty('rate', int(base_rate * speed))
            
            if async_mode:
                # Falar em thread separada
                thread = threading.Thread(target=self._speak_sync, args=(text,))
                thread.daemon = True
                thread.start()
            else:
                self._speak_sync(text)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao sintetizar fala: {e}")
            return False
    
    def _speak_sync(self, text: str):
        """Fala síncrona (bloqueante)"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Erro na síntese de fala: {e}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Retorna duração do áudio em segundos"""
        try:
            with wave.open(audio_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                return duration
        except:
            return 0.0
    
    def analyze_speech_emotion(self, audio_path: str) -> Dict[str, Any]:
        """
        Analisa emoção na fala (preparação futura)
        
        Returns:
            Dicionário com emoção detectada
        """
        # TODO: Implementar análise de emoção
        # Pode usar librosa + modelo de classificação
        return {
            "emotion": "neutral",
            "confidence": 0.0,
            "note": "Análise de emoção ainda não implementada"
        }
    
    def diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Diarização de voz (identificar quem está falando)
        
        Returns:
            Lista de segmentos com speaker ID
        """
        # TODO: Implementar diarização
        # Pode usar pyannote.audio
        return [{
            "start": 0.0,
            "end": 0.0,
            "speaker": "SPEAKER_00",
            "note": "Diarização ainda não implementada"
        }]
    
    def upgrade_model(self, model_size: str = "small"):
        """
        Faz upgrade do modelo Whisper
        
        Args:
            model_size: tiny, base, small, medium, large
        """
        if not self.whisper_available:
            logger.error("Whisper não disponível")
            return False
        
        try:
            import whisper
            logger.info(f"Fazendo upgrade para modelo '{model_size}'...")
            self.whisper_model = whisper.load_model(model_size)
            self.whisper_model_size = model_size
            logger.info(f"✅ Upgrade concluído: {model_size}")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upgrade: {e}")
            return False


# Instância global
advanced_speech_processor = AdvancedSpeechProcessor()


# Função de conveniência
def transcribe_audio(audio_path: str, language: str = "pt") -> str:
    """Transcreve áudio e retorna apenas o texto"""
    result = advanced_speech_processor.transcribe(audio_path, language)
    return result.get("text", "")
