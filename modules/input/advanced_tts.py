"""
Advanced TTS Module - High-quality Text-to-Speech using Coqui TTS and Piper
"""

import os
import tempfile
from typing import Optional, Literal, List
from pathlib import Path
from core.logger import logger

try:
    from TTS.api import TTS as CoquiTTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    logger.warning("Coqui TTS não disponível. Instale com: pip install TTS")

try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    AUDIO_PLAYBACK_AVAILABLE = False
    logger.warning("sounddevice não disponível. Instale com: pip install sounddevice soundfile")


class AdvancedTTSModule:
    """
    Módulo avançado de Text-to-Speech com múltiplos backends.
    Suporta Coqui TTS para voz de alta qualidade e naturalidade.
    """
    
    def __init__(
        self,
        backend: Literal["coqui", "piper"] = "coqui",
        model_name: Optional[str] = None,
        language: str = "pt",
        speaker: Optional[str] = None
    ):
        """
        Inicializa o módulo TTS avançado.
        
        Args:
            backend: "coqui" ou "piper"
            model_name: Nome do modelo (None para usar padrão)
            language: Código do idioma
            speaker: Nome/ID do speaker (para modelos multi-speaker)
        """
        self.backend = backend
        self.model_name = model_name
        self.language = language
        self.speaker = speaker
        self.tts_engine = None
        
        # Inicializar backend
        self._init_backend()
        
        logger.info(f"AdvancedTTSModule inicializado - Backend: {backend}, Model: {model_name or 'default'}")
    
    def _init_backend(self):
        """Inicializa o backend de TTS."""
        if self.backend == "coqui":
            self._init_coqui()
        elif self.backend == "piper":
            self._init_piper()
        else:
            logger.error(f"Backend desconhecido: {self.backend}")
    
    def _init_coqui(self):
        """Inicializa Coqui TTS."""
        if not COQUI_AVAILABLE:
            logger.error("Coqui TTS não está instalado")
            return
        
        try:
            # Se model_name não especificado, usar modelo padrão
            if self.model_name:
                logger.info(f"Carregando modelo Coqui: {self.model_name}")
                self.tts_engine = CoquiTTS(model_name=self.model_name)
            else:
                # Usar modelo padrão multilingual
                logger.info("Carregando modelo Coqui padrão")
                # Lista de modelos recomendados para português
                recommended_models = [
                    "tts_models/multilingual/multi-dataset/xtts_v2",  # Melhor qualidade, multi-speaker
                    "tts_models/pt/cv/vits",  # Português BR
                ]
                
                # Tentar carregar um modelo recomendado
                for model in recommended_models:
                    try:
                        logger.info(f"Tentando carregar: {model}")
                        self.tts_engine = CoquiTTS(model_name=model)
                        self.model_name = model
                        break
                    except Exception as e:
                        logger.warning(f"Não foi possível carregar {model}: {e}")
                
                if not self.tts_engine:
                    # Fallback para primeiro modelo disponível
                    logger.info("Usando modelo TTS padrão")
                    self.tts_engine = CoquiTTS()
            
            logger.info(f"Coqui TTS inicializado com sucesso - Modelo: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Coqui TTS: {e}")
    
    def _init_piper(self):
        """Inicializa Piper TTS."""
        # Piper requer instalação externa e uso via subprocess
        # Implementação simplificada
        logger.info("Piper TTS - implementação via subprocess")
        # TODO: Implementar integração com Piper quando disponível
    
    def speak(
        self,
        text: str,
        output_file: Optional[str] = None,
        play_audio: bool = True,
        speed: float = 1.0
    ) -> Optional[str]:
        """
        Converte texto em fala.
        
        Args:
            text: Texto para converter
            output_file: Arquivo de saída (None para arquivo temporário)
            play_audio: Se True, reproduz o áudio automaticamente
            speed: Velocidade da fala (1.0 = normal)
        
        Returns:
            Caminho do arquivo de áudio gerado ou None em caso de erro
        """
        if not self.tts_engine:
            logger.error("TTS engine não está inicializado")
            return None
        
        try:
            # Determinar arquivo de saída
            if output_file is None:
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                output_file = temp_file.name
                temp_file.close()
            
            # Gerar áudio
            logger.info(f"Gerando áudio: '{text[:50]}...'")
            
            if self.backend == "coqui":
                # Verificar se modelo suporta multi-speaker
                if self.speaker and hasattr(self.tts_engine, 'speakers'):
                    self.tts_engine.tts_to_file(
                        text=text,
                        file_path=output_file,
                        speaker=self.speaker
                    )
                else:
                    self.tts_engine.tts_to_file(
                        text=text,
                        file_path=output_file
                    )
            
            logger.info(f"Áudio gerado: {output_file}")
            
            # Reproduzir áudio se solicitado
            if play_audio:
                self.play_audio_file(output_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return None
    
    def play_audio_file(self, file_path: str):
        """
        Reproduz arquivo de áudio.
        
        Args:
            file_path: Caminho do arquivo de áudio
        """
        if not AUDIO_PLAYBACK_AVAILABLE:
            logger.warning("Audio playback não disponível")
            return
        
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return
        
        try:
            logger.info(f"Reproduzindo áudio: {file_path}")
            data, samplerate = sf.read(file_path)
            sd.play(data, samplerate)
            sd.wait()  # Esperar reprodução terminar
            logger.info("Reprodução concluída")
        except Exception as e:
            logger.error(f"Erro ao reproduzir áudio: {e}")
    
    def speak_async(self, text: str):
        """
        Fala em modo assíncrono (não bloqueia).
        
        Args:
            text: Texto para falar
        """
        import threading
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
    
    def get_available_speakers(self) -> List[str]:
        """Retorna lista de speakers disponíveis (para modelos multi-speaker)."""
        if not self.tts_engine:
            return []
        
        try:
            if hasattr(self.tts_engine, 'speakers'):
                return self.tts_engine.speakers
            return []
        except:
            return []
    
    def get_available_languages(self) -> List[str]:
        """Retorna lista de idiomas disponíveis."""
        if not self.tts_engine:
            return []
        
        try:
            if hasattr(self.tts_engine, 'languages'):
                return self.tts_engine.languages
            return []
        except:
            return []
    
    def is_available(self) -> bool:
        """Verifica se o módulo está disponível."""
        return self.tts_engine is not None
    
    @staticmethod
    def list_available_models() -> List[str]:
        """Lista modelos TTS disponíveis."""
        if not COQUI_AVAILABLE:
            logger.warning("Coqui TTS não está instalado")
            return []
        
        try:
            tts = CoquiTTS()
            return tts.list_models()
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    @staticmethod
    def get_recommended_models(language: str = "pt") -> List[str]:
        """Retorna modelos recomendados para um idioma."""
        recommendations = {
            "pt": [
                "tts_models/multilingual/multi-dataset/xtts_v2",
                "tts_models/pt/cv/vits"
            ],
            "en": [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/vctk/vits"
            ],
            "es": [
                "tts_models/es/css10/vits"
            ]
        }
        return recommendations.get(language, [])


# Fallback para TTS básico usando pyttsx3
class FallbackTTSModule:
    """TTS básico usando pyttsx3 como fallback."""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            logger.info("Fallback TTS (pyttsx3) inicializado")
        except:
            self.engine = None
            logger.error("pyttsx3 não disponível")
    
    def speak(self, text: str, play_audio: bool = True):
        """Fala texto."""
        if not self.engine:
            print(f"JARVIS: {text}")
            return
        
        if play_audio:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def is_available(self) -> bool:
        return self.engine is not None
