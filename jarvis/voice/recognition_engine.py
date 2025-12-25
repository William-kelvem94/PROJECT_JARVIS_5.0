"""
Engine de reconhecimento de voz para JARVIS
"""

import speech_recognition as sr
from typing import Optional, Dict, Any
import time

from ..core.logger import default_logger


class RecognitionEngine:
    """Engine de reconhecimento de voz com tratamento robusto"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Inicializar recognizer
        self.recognizer = sr.Recognizer()
        
        # Configurar parâmetros
        self._configure_recognizer()
        
        self.logger.info("Engine de reconhecimento de voz inicializado")
    
    def _configure_recognizer(self):
        """Configura parâmetros do recognizer"""
        recognition_config = self.config.get('recognition', {})
        
        # Configurar threshold de energia
        if recognition_config.get('dynamic_energy_threshold', True):
            self.recognizer.dynamic_energy_threshold = True
        else:
            self.recognizer.energy_threshold = recognition_config.get('energy_threshold', 300)
        
        # Configurar outros parâmetros
        self.recognizer.pause_threshold = 0.8  # Pausa para considerar fim da fala
        self.recognizer.phrase_threshold = 0.3  # Mínimo de áudio para considerar fala
        self.recognizer.non_speaking_duration = 0.5  # Duração de silêncio para parar
        
        self.logger.debug("Recognizer configurado")
    
    def listen(self) -> Optional[str]:
        """
        Escuta e reconhece fala do microfone
        
        Returns:
            Texto reconhecido ou None se não conseguiu reconhecer
        """
        try:
            with sr.Microphone() as source:
                self.logger.voice_event("listen_start", "Ajustando para ruído ambiente...")
                print("Ouvindo...")
                
                # Ajustar para ruído ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.logger.voice_event("listen_recording", "Gravando áudio...")
                
                # Configurações de timeout
                recognition_config = self.config.get('recognition', {})
                timeout = recognition_config.get('timeout', 5)
                phrase_limit = recognition_config.get('phrase_limit', 10)
                
                # Escutar áudio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
                
                self.logger.voice_event("listen_processing", "Processando áudio...")
                
                # Reconhecer fala
                language = self.config.get('voice', {}).get('language', 'pt-BR')
                command = self.recognizer.recognize_google(audio, language=language)
                
                self.logger.voice_event("listen_success", f"Reconhecido: '{command}'")
                print(f"Você disse: {command}")
                
                return command.lower()
                
        except sr.WaitTimeoutError:
            self.logger.voice_event("listen_timeout", "Timeout - nenhuma fala detectada")
            return None
            
        except sr.UnknownValueError:
            self.logger.voice_event("listen_unknown", "Não foi possível entender a fala")
            return "não_entendi"
            
        except sr.RequestError as e:
            self.logger.error(f"Erro no serviço de reconhecimento: {e}")
            return "erro_conexao"
            
        except Exception as e:
            self.logger.error(f"Erro inesperado no reconhecimento: {e}")
            return None
    
    def listen_for_wake_word(self, wake_word: str, timeout: float = 30.0) -> bool:
        """
        Escuta por uma palavra de ativação específica
        
        Args:
            wake_word: Palavra de ativação
            timeout: Timeout em segundos
            
        Returns:
            True se palavra de ativação foi detectada
        """
        start_time = time.time()
        
        self.logger.info(f"Escutando por palavra de ativação: '{wake_word}'")
        
        while time.time() - start_time < timeout:
            command = self.listen()
            
            if command and wake_word.lower() in command:
                self.logger.voice_event("wake_word_detected", f"Palavra '{wake_word}' detectada")
                return True
            
            # Pequena pausa para não sobrecarregar
            time.sleep(0.1)
        
        self.logger.voice_event("wake_word_timeout", f"Timeout aguardando '{wake_word}'")
        return False
    
    def test_microphone(self) -> bool:
        """
        Testa se o microfone está funcionando
        
        Returns:
            True se microfone está funcionando
        """
        try:
            with sr.Microphone() as source:
                self.logger.info("Testando microfone...")
                
                # Tentar ajustar para ruído ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Tentar gravar um pequeno áudio
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=1)
                
                self.logger.info("Microfone funcionando corretamente")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro no teste de microfone: {e}")
            return False
    
    def get_microphone_list(self) -> list:
        """
        Retorna lista de microfones disponíveis
        
        Returns:
            Lista de microfones
        """
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            self.logger.error(f"Erro ao listar microfones: {e}")
            return []
    
    def set_microphone(self, device_index: Optional[int] = None):
        """
        Define microfone específico para usar
        
        Args:
            device_index: Índice do dispositivo de microfone
        """
        try:
            # Esta funcionalidade requer modificação na forma como usamos o Microphone
            # Por enquanto, apenas logamos a tentativa
            self.logger.info(f"Tentativa de definir microfone: {device_index}")
        except Exception as e:
            self.logger.error(f"Erro ao definir microfone: {e}")
    
    def calibrate(self) -> bool:
        """
        Calibra o recognizer para o ambiente atual
        
        Returns:
            True se calibração foi bem-sucedida
        """
        try:
            with sr.Microphone() as source:
                self.logger.info("Calibrando recognizer para ambiente atual...")
                print("Calibrando... Mantenha silêncio por alguns segundos.")
                
                # Calibração mais longa para melhor precisão
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
                
                self.logger.info("Calibração concluída")
                print("Calibração concluída!")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro na calibração: {e}")
            return False
