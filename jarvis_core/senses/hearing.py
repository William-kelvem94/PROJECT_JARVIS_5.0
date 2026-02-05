"""
Senses - Hearing Module
VAD + Whisper STT
"""

import logging
import asyncio
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

class Hearing:
    """Sistema de audição com VAD e Whisper"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.whisper_model = None
        self.vad_model = None
        self.is_listening = False
        
        # Lazy loading
        logger.info(f"✅ Hearing inicializado (modelo: {model_size})")
    
    async def listen(self, timeout: int = 10) -> Optional[str]:
        """Escuta e transcreve áudio"""
        try:
            # Importar audio capture
            from jarvis_core.senses.audio_capture import audio_capture
            
            # Gravar áudio
            logger.info(f"👂 Ouvindo por {timeout}s...")
            audio_file = audio_capture.record_audio(duration=timeout)
            
            if not audio_file:
                logger.warning("⚠️ Falha ao gravar áudio")
                return None
            
            # Lazy load Whisper
            if not self.whisper_model:
                from faster_whisper import WhisperModel
                logger.info(f"📥 Carregando Whisper {self.model_size}...")
                self.whisper_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            
            # Transcrever
            segments, info = self.whisper_model.transcribe(
                audio_file,
                language="pt",
                vad_filter=True,
                beam_size=5
            )
            
            # Extrair texto
            text = " ".join([segment.text for segment in segments])
            
            if text:
                logger.info(f"👂 Ouvido: {text}")
                return text.strip()
            
            return None
            
        except ImportError:
            logger.error("❌ faster-whisper não instalado: pip install faster-whisper")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao ouvir: {e}")
            return None
    
    def detect_wake_word(self, audio_data: np.ndarray) -> bool:
        """Detecta wake word 'Jarvis'"""
        # Implementação simplificada
        # Em produção, usar Porcupine ou similar
        try:
            from jarvis_core.senses.audio_capture import audio_capture
            
            # Verificar nível de áudio
            level = audio_capture.get_audio_level()
            
            # Se houver áudio, considerar como wake word (simplificado)
            return level > 0.1
        except:
            return False
    
    def get_audio_level(self) -> float:
        """Retorna amplitude do áudio (0-1)"""
        try:
            from jarvis_core.senses.audio_capture import audio_capture
            return audio_capture.get_audio_level()
        except:
            return 0.0


# Instância global
hearing = Hearing()
