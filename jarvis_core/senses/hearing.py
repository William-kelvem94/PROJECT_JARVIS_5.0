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
            # Lazy load Whisper
            if not self.whisper_model:
                from faster_whisper import WhisperModel
                logger.info(f"📥 Carregando Whisper {self.model_size}...")
                self.whisper_model = WhisperModel(self.model_size, device="cpu")
            
            # Gravar áudio (simulado por enquanto)
            audio_file = "data/temp/audio_input.wav"
            
            # Transcrever
            segments, info = self.whisper_model.transcribe(
                audio_file,
                language="pt",
                vad_filter=True
            )
            
            # Extrair texto
            text = " ".join([segment.text for segment in segments])
            
            if text:
                logger.info(f"👂 Ouvido: {text}")
                return text
            
            return None
            
        except FileNotFoundError:
            logger.warning("⚠️ Arquivo de áudio não encontrado")
            return None
        except ImportError:
            logger.error("❌ faster-whisper não instalado")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao ouvir: {e}")
            return None
    
    def detect_wake_word(self, audio_data: np.ndarray) -> bool:
        """Detecta wake word 'Jarvis'"""
        # Implementação simplificada
        # Em produção, usar Vosk ou similar
        return False
    
    def get_audio_level(self) -> float:
        """Retorna amplitude do áudio (0-1)"""
        # Para barge-in
        return 0.0


# Instância global
hearing = Hearing()
