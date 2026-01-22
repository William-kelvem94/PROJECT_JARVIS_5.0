"""
Módulo de Voz - Conversação Bidirecional
Suporta Speech-to-Text (STT) e Text-to-Speech (TTS)
"""

import os
import platform
from typing import Optional, Callable
from pathlib import Path
from core.logger import logger

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition não disponível. Instale com: pip install SpeechRecognition")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 não disponível. Instale com: pip install pyttsx3")

try:
    from vosk import Model, SetLogLevel
    import json
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("vosk não disponível. Para melhor reconhecimento, instale: pip install vosk")

class VoiceModule:
    """
    Módulo de voz que oferece STT (Speech-to-Text) e TTS (Text-to-Speech).
    Suporta múltiplos backends:
    - STT: Whisper (OpenAI), VOSK, Google Speech Recognition
    - TTS: pyttsx3 (local), Coqui TTS, Piper
    """
    
    def __init__(self, stt_backend: str = "auto", tts_backend: str = "pyttsx3"):
        """
        Inicializa o módulo de voz.
        
        Args:
            stt_backend: "auto", "whisper", "vosk", ou "google"
            tts_backend: "pyttsx3", "coqui", ou "piper"
        """
        self.stt_backend = stt_backend
        self.tts_backend = tts_backend
        self.recognizer = None
        self.tts_engine = None
        
        # Inicializar STT
        self._init_stt()
        
        # Inicializar TTS
        self._init_tts()
        
        logger.info(f"VoiceModule inicializado - STT: {stt_backend}, TTS: {tts_backend}")
    
    def _init_stt(self):
        """Inicializa o engine de Speech-to-Text."""
        if self.stt_backend == "auto":
            if VOSK_AVAILABLE:
                self.stt_backend = "vosk"
            elif SPEECH_RECOGNITION_AVAILABLE:
                self.stt_backend = "google"
            else:
                logger.error("Nenhum backend de STT disponível")
                return
        
        if self.stt_backend == "vosk" and VOSK_AVAILABLE:
            # VOSK requer modelo baixado separadamente
            model_path = os.getenv("VOSK_MODEL_PATH", None)
            if model_path and os.path.exists(model_path):
                SetLogLevel(-1)
                self.vosk_model = Model(model_path)
                logger.info(f"VOSK modelo carregado: {model_path}")
            else:
                logger.warning("VOSK modelo não encontrado. Use VOSK_MODEL_PATH para especificar o caminho.")
                self.stt_backend = "google"  # Fallback
        
        if self.stt_backend == "google" and SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            logger.info("Google Speech Recognition inicializado")
    
    def _init_tts(self):
        """Inicializa o engine de Text-to-Speech."""
        if self.tts_backend == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Configurar voz (tentar português)
                voices = self.tts_engine.getProperty('voices')
                if platform.system() == "Windows":
                    # Procurar voz em português no Windows
                    for voice in voices:
                        if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
                # Configurar velocidade e volume
                self.tts_engine.setProperty('rate', 150)  # Velocidade padrão
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                
                logger.info("TTS pyttsx3 inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar pyttsx3: {e}")
                self.tts_engine = None
    
    def listen(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> Optional[str]:
        """
        Escuta e converte fala para texto.
        
        Args:
            timeout: Tempo máximo para iniciar o reconhecimento
            phrase_time_limit: Tempo máximo para a frase completa
        
        Returns:
            Texto transcrito ou None em caso de erro
        """
        if not self.recognizer and self.stt_backend != "vosk":
            logger.error("Reconhecedor de voz não inicializado")
            return None
        
        try:
            with sr.Microphone() as source:
                # Ajustar para ruído ambiente
                logger.info("Ajustando para ruído ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                logger.info("Escutando...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                # Reconhecer usando Google Speech Recognition
                logger.info("Reconhecendo...")
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                logger.info(f"Texto reconhecido: {text}")
                return text
                
        except sr.WaitTimeoutError:
            logger.warning("Tempo limite excedido aguardando fala")
            return None
        except sr.UnknownValueError:
            logger.warning("Não foi possível entender o áudio")
            return None
        except sr.RequestError as e:
            logger.error(f"Erro no serviço de reconhecimento: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao escutar: {e}")
            return None
    
    def speak(self, text: str, async_mode: bool = False):
        """
        Converte texto para fala.
        
        Args:
            text: Texto para falar
            async_mode: Se True, fala em modo assíncrono (não bloqueia)
        """
        if not self.tts_engine:
            logger.warning("TTS engine não disponível. Imprimindo texto:")
            print(f"JARVIS diz: {text}")
            return
        
        try:
            if async_mode:
                # Para modo assíncrono, usar thread separada
                import threading
                thread = threading.Thread(target=self._speak_sync, args=(text,))
                thread.daemon = True
                thread.start()
            else:
                self._speak_sync(text)
        except Exception as e:
            logger.error(f"Erro ao falar: {e}")
    
    def _speak_sync(self, text: str):
        """Fala de forma síncrona."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def set_voice_properties(self, rate: Optional[int] = None, volume: Optional[float] = None):
        """Configura propriedades da voz."""
        if not self.tts_engine:
            return
        
        if rate is not None:
            self.tts_engine.setProperty('rate', rate)
        if volume is not None:
            self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def is_available(self) -> bool:
        """Verifica se o módulo de voz está disponível."""
        return (self.recognizer is not None or self.stt_backend == "vosk") and self.tts_engine is not None

