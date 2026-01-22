"""
Wake Word Detector - Detecção de palavras de ativação como "Hey JARVIS"
"""

import os
import threading
import time
from typing import Optional, Callable, List
from core.logger import logger

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    logger.warning("Porcupine não disponível. Instale com: pip install pvporcupine")

try:
    import sounddevice as sd
    import numpy as np
    AUDIO_CAPTURE_AVAILABLE = True
except ImportError:
    AUDIO_CAPTURE_AVAILABLE = False
    logger.warning("sounddevice não disponível. Instale com: pip install sounddevice")


class WakeWordDetector:
    """
    Detector de palavra de ativação (wake word) usando Porcupine.
    Permite ativar o JARVIS com comandos de voz como "Hey JARVIS".
    """
    
    def __init__(
        self,
        access_key: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        sensitivities: Optional[List[float]] = None,
        callback: Optional[Callable[[int], None]] = None
    ):
        """
        Inicializa o detector de wake word.
        
        Args:
            access_key: Chave de acesso do Porcupine (obtenha em https://console.picovoice.ai/)
            keywords: Lista de palavras-chave a detectar (padrão: ["jarvis"])
            sensitivities: Sensibilidade para cada palavra (0.0 a 1.0)
            callback: Função a chamar quando palavra for detectada
        """
        if not PORCUPINE_AVAILABLE:
            raise ImportError("Porcupine não instalado. Execute: pip install pvporcupine")
        
        if not AUDIO_CAPTURE_AVAILABLE:
            raise ImportError("sounddevice não disponível. Execute: pip install sounddevice")
        
        # Configuração
        self.access_key = access_key or os.getenv("PORCUPINE_ACCESS_KEY")
        self.keywords = keywords or ["jarvis"]
        self.sensitivities = sensitivities or [0.5] * len(self.keywords)
        self.callback = callback
        
        # Estado
        self.is_running = False
        self.detection_thread = None
        self.porcupine = None
        
        # Estatísticas
        self.total_detections = 0
        self.last_detection_time = None
        
        logger.info(f"WakeWordDetector inicializado - Keywords: {self.keywords}")
    
    def start(self) -> bool:
        """
        Inicia a detecção de wake word em background.
        
        Returns:
            True se iniciou com sucesso
        """
        if self.is_running:
            logger.warning("Detector já está rodando")
            return False
        
        if not self.access_key:
            logger.error("Access key não configurada. Defina PORCUPINE_ACCESS_KEY ou passe access_key")
            return False
        
        try:
            # Inicializar Porcupine
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=self.keywords,
                sensitivities=self.sensitivities
            )
            
            # Iniciar thread de detecção
            self.is_running = True
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            
            logger.info(f"Wake word detector iniciado - Aguardando: {self.keywords}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar detector: {e}")
            return False
    
    def stop(self):
        """Para a detecção de wake word."""
        if not self.is_running:
            return
        
        logger.info("Parando wake word detector...")
        self.is_running = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        
        logger.info("Wake word detector parado")
    
    def _detection_loop(self):
        """Loop principal de detecção (roda em thread separada)."""
        try:
            # Abrir stream de áudio
            audio_stream = sd.InputStream(
                channels=1,
                samplerate=self.porcupine.sample_rate,
                blocksize=self.porcupine.frame_length,
                dtype='int16'
            )
            
            audio_stream.start()
            logger.info("Stream de áudio iniciado, aguardando wake word...")
            
            while self.is_running:
                # Ler frame de áudio
                audio_frame, overflowed = audio_stream.read(self.porcupine.frame_length)
                
                if overflowed:
                    logger.warning("Overflow no buffer de áudio")
                
                # Processar frame
                audio_frame = audio_frame.flatten().astype('int16')
                keyword_index = self.porcupine.process(audio_frame)
                
                # Detectado?
                if keyword_index >= 0:
                    self._on_detection(keyword_index)
            
            audio_stream.stop()
            audio_stream.close()
            
        except Exception as e:
            logger.error(f"Erro no loop de detecção: {e}")
            self.is_running = False
    
    def _on_detection(self, keyword_index: int):
        """Chamado quando wake word é detectada."""
        keyword = self.keywords[keyword_index]
        self.total_detections += 1
        self.last_detection_time = time.time()
        
        logger.info(f"Wake word detectada: '{keyword}' (#{self.total_detections})")
        
        # Chamar callback se fornecido
        if self.callback:
            try:
                self.callback(keyword_index)
            except Exception as e:
                logger.error(f"Erro ao executar callback: {e}")
    
    def is_active(self) -> bool:
        """Verifica se o detector está ativo."""
        return self.is_running
    
    def get_stats(self) -> dict:
        """Retorna estatísticas de detecção."""
        return {
            "is_running": self.is_running,
            "keywords": self.keywords,
            "total_detections": self.total_detections,
            "last_detection_time": self.last_detection_time
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class SimpleWakeWordDetector:
    """
    Detector de wake word simplificado sem dependências externas.
    Usa reconhecimento básico de voz para detectar palavras-chave.
    Menos preciso mas não requer chave de API.
    """
    
    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        callback: Optional[Callable[[str], None]] = None
    ):
        """
        Inicializa detector simples.
        
        Args:
            keywords: Palavras-chave a detectar
            callback: Função a chamar quando detectada
        """
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.keywords = [k.lower() for k in (keywords or ["jarvis", "hey jarvis"])]
            self.callback = callback
            self.is_running = False
            self.detection_thread = None
            logger.info(f"SimpleWakeWordDetector inicializado - Keywords: {self.keywords}")
        except ImportError:
            raise ImportError("speech_recognition não disponível")
    
    def start(self) -> bool:
        """Inicia detecção."""
        if self.is_running:
            return False
        
        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        logger.info("Simple wake word detector iniciado")
        return True
    
    def stop(self):
        """Para detecção."""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        logger.info("Simple wake word detector parado")
    
    def _detection_loop(self):
        """Loop de detecção."""
        import speech_recognition as sr
        
        while self.is_running:
            try:
                with sr.Microphone() as source:
                    logger.debug("Aguardando wake word...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    
                    try:
                        text = self.recognizer.recognize_google(audio, language='pt-BR').lower()
                        logger.debug(f"Ouvido: {text}")
                        
                        # Verificar se contém palavra-chave
                        for keyword in self.keywords:
                            if keyword in text:
                                logger.info(f"Wake word detectada: '{keyword}'")
                                if self.callback:
                                    self.callback(keyword)
                                break
                    except sr.UnknownValueError:
                        pass  # Não entendeu, continuar
                    except sr.RequestError as e:
                        logger.error(f"Erro no serviço de reconhecimento: {e}")
                        time.sleep(1)
            
            except Exception as e:
                if self.is_running:  # Só logar se ainda estiver rodando
                    logger.debug(f"Erro na detecção: {e}")
                time.sleep(0.5)
    
    def is_active(self) -> bool:
        """Verifica se está ativo."""
        return self.is_running
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
