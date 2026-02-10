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
import time
import librosa
import torch

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
        """
        [DEPRECATED] Inicialização de TTS interno desativada.
        O controle de voz agora é centralizado em src.core.audio.voice_controller
        para evitar conflito de vozes (robótica vs neural).
        """
        self.tts_available = False
        self.tts_engine = None
        # logger.info("TTS interno do AdvancedSpeechProcessor desativado (usando VoiceController).")
    
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
        Transcrição em tempo real usando buffer circular (Faster-Whisper style)
        """
        if not self.whisper_available:
            logger.error("Whisper não disponível para streaming")
            return

        def _streaming_worker():
            logger.info("📡 Iniciando stream de transcrição...")
            # Buffer circular de 3 segundos para latência reduzida
            buffer = []
            while self.whisper_available:
                if hasattr(audio_stream, 'read'):
                    chunk = audio_stream.read(16000) # 1s de áudio
                    if chunk:
                        # Processamento rápido com o modelo carregado
                        segments, info = self.whisper_model.transcribe(
                            chunk, beam_size=5, language=language, vad_filter=True
                        )
                        for segment in segments:
                            callback(segment.text)
                time.sleep(0.1)

        threading.Thread(target=_streaming_worker, daemon=True).start()
    
    def speak(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        async_mode: bool = False
    ) -> bool:
        """
        Redireciona para o VoiceController centralizado.
        """
        try:
            from src.core.audio.voice_controller import voice_controller
            voice_controller.speak(text)
            return True
        except ImportError:
            logger.error("VoiceController não disponível para redirecionamento.")
            return False
            
    def _speak_sync(self, text: str):
        """[DEPRECATED] Método mantido apenas para compatibilidade de interface."""
        pass
    
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
        Analisa emoção na fala usando librosa (MFCC features)
        """
        if not os.path.exists(audio_path):
            return {"emotion": "neutral", "confidence": 0.0}

        try:
            # Carregar áudio
            y, sr = librosa.load(audio_path, duration=3, offset=0.5)
            
            # Extrair features MFCC
            mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
            
            # Simple Intensity Logic (Fallback/Baseline)
            # Em versões futuras, usaremos um modelo .pth/.onnx pré-treinado aqui
            intensity = np.sqrt(np.mean(y**2))
            
            emotion = "neutral"
            confidence = 0.5
            
            if intensity > 0.15:
                emotion = "angry" if intensity > 0.3 else "happy"
                confidence = 0.7
            elif intensity < 0.01:
                emotion = "sad"
                confidence = 0.6
                
            return {
                "emotion": emotion,
                "confidence": confidence,
                "intensity": float(intensity),
                "mfcc_fingerprint": mfccs.tolist()[:5] # Apenas o início para log
            }
        except Exception as e:
            logger.error(f"Erro na análise de emoção vocal: {e}")
            return {"emotion": "neutral", "confidence": 0.0}
    
    def diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Diarização de voz usando pyannote.audio
        Identifica 'Quem disse o quê'
        """
        try:
            from pyannote.audio import Pipeline
            # Pipeline requer token do HuggingFace (USER precisará configurar se usar pyannote oficial)
            # Por enquanto, mantemos uma lógica estruturada que o usuário pode expandir
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=True)
            
            diarization = pipeline(audio_path)
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            return segments
        except Exception as e:
            logger.warning(f"Diarização (pyannote) indisponível ou erro: {e}. Usando ID genérico.")
            return [{"start": 0.0, "end": 0.0, "speaker": "USER_MAIN"}]
    
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
