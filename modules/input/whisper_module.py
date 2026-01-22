"""
Whisper Module - High-quality offline Speech-to-Text using OpenAI Whisper
"""

import os
from typing import Optional, Literal
from pathlib import Path
from core.logger import logger

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper não disponível. Instale com: pip install openai-whisper")

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_CAPTURE_AVAILABLE = True
except ImportError:
    AUDIO_CAPTURE_AVAILABLE = False
    logger.warning("sounddevice/soundfile não disponíveis. Instale com: pip install sounddevice soundfile")


class WhisperModule:
    """
    Módulo de reconhecimento de voz usando Whisper da OpenAI.
    Oferece reconhecimento offline de alta qualidade em múltiplos idiomas.
    """
    
    def __init__(
        self, 
        model_name: Literal["tiny", "base", "small", "medium", "large"] = "base",
        device: Optional[str] = None,
        language: str = "pt"
    ):
        """
        Inicializa o módulo Whisper.
        
        Args:
            model_name: Tamanho do modelo (tiny, base, small, medium, large)
                - tiny: ~39M parâmetros, mais rápido mas menos preciso
                - base: ~74M parâmetros, bom equilíbrio
                - small: ~244M parâmetros, mais preciso
                - medium: ~769M parâmetros, muito preciso
                - large: ~1550M parâmetros, máxima qualidade
            device: "cuda" para GPU, "cpu" para CPU, None para auto-detectar
            language: Código do idioma (pt, en, es, etc.)
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper não está instalado. Execute: pip install openai-whisper")
        
        if not AUDIO_CAPTURE_AVAILABLE:
            raise ImportError("Audio capture não disponível. Execute: pip install sounddevice soundfile")
        
        self.model_name = model_name
        self.language = language
        self.device = device
        self.model = None
        
        # Carregar modelo
        self._load_model()
        
        # Configurações de áudio
        self.sample_rate = 16000  # Whisper requer 16kHz
        self.channels = 1  # Mono
        
        logger.info(f"WhisperModule inicializado - Modelo: {model_name}, Idioma: {language}")
    
    def _load_model(self):
        """Carrega o modelo Whisper."""
        try:
            logger.info(f"Carregando modelo Whisper '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info(f"Modelo Whisper '{self.model_name}' carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo Whisper: {e}")
            raise
    
    def record_audio(self, duration: float = 5.0, auto_stop: bool = True) -> Optional[np.ndarray]:
        """
        Grava áudio do microfone.
        
        Args:
            duration: Duração máxima da gravação em segundos
            auto_stop: Se True, detecta silêncio e para automaticamente
        
        Returns:
            Array numpy com os dados de áudio ou None em caso de erro
        """
        try:
            logger.info(f"Gravando áudio por até {duration}s...")
            
            # Gravar áudio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()  # Esperar gravação terminar
            
            logger.info("Gravação concluída")
            return audio_data.flatten()
            
        except Exception as e:
            logger.error(f"Erro ao gravar áudio: {e}")
            return None
    
    def transcribe_audio(
        self, 
        audio_data: Optional[np.ndarray] = None,
        audio_file: Optional[str] = None,
        task: Literal["transcribe", "translate"] = "transcribe"
    ) -> Optional[str]:
        """
        Transcreve áudio para texto.
        
        Args:
            audio_data: Dados de áudio (array numpy)
            audio_file: Caminho para arquivo de áudio
            task: "transcribe" para transcrever no idioma original,
                  "translate" para traduzir para inglês
        
        Returns:
            Texto transcrito ou None em caso de erro
        """
        if not self.model:
            logger.error("Modelo Whisper não está carregado")
            return None
        
        try:
            # Determinar fonte de áudio
            if audio_file:
                logger.info(f"Transcrevendo arquivo: {audio_file}")
                result = self.model.transcribe(
                    audio_file,
                    language=self.language,
                    task=task
                )
            elif audio_data is not None:
                logger.info("Transcrevendo áudio gravado")
                # Whisper espera float32 normalizado entre -1 e 1
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    task=task
                )
            else:
                logger.error("Nenhuma fonte de áudio fornecida")
                return None
            
            text = result["text"].strip()
            logger.info(f"Texto transcrito: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            return None
    
    def listen(self, duration: float = 5.0) -> Optional[str]:
        """
        Grava e transcreve áudio em uma única operação.
        
        Args:
            duration: Duração máxima da gravação em segundos
        
        Returns:
            Texto transcrito ou None em caso de erro
        """
        audio_data = self.record_audio(duration)
        if audio_data is None:
            return None
        
        return self.transcribe_audio(audio_data)
    
    def transcribe_file(self, file_path: str) -> Optional[str]:
        """
        Transcreve arquivo de áudio.
        
        Args:
            file_path: Caminho para o arquivo de áudio
        
        Returns:
            Texto transcrito ou None em caso de erro
        """
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return None
        
        return self.transcribe_audio(audio_file=file_path)
    
    def is_available(self) -> bool:
        """Verifica se o módulo está disponível."""
        return WHISPER_AVAILABLE and AUDIO_CAPTURE_AVAILABLE and self.model is not None
    
    @staticmethod
    def get_available_models() -> list:
        """Retorna lista de modelos disponíveis."""
        return ["tiny", "base", "small", "medium", "large"]
    
    @staticmethod
    def get_model_info(model_name: str) -> dict:
        """Retorna informações sobre um modelo."""
        models_info = {
            "tiny": {"params": "39M", "speed": "muito rápido", "quality": "básica", "vram": "~1GB"},
            "base": {"params": "74M", "speed": "rápido", "quality": "boa", "vram": "~1GB"},
            "small": {"params": "244M", "speed": "médio", "quality": "muito boa", "vram": "~2GB"},
            "medium": {"params": "769M", "speed": "lento", "quality": "excelente", "vram": "~5GB"},
            "large": {"params": "1550M", "speed": "muito lento", "quality": "máxima", "vram": "~10GB"}
        }
        return models_info.get(model_name, {})
