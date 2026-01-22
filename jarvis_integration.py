"""
JARVIS 5.0 Integration Manager
Centraliza e facilita o uso de todos os novos módulos
"""

from typing import Optional, Callable, Dict, Any
from core.logger import logger


class JarvisVoiceManager:
    """Gerenciador de voz - STT e TTS."""
    
    def __init__(
        self,
        use_whisper: bool = True,
        use_advanced_tts: bool = True,
        whisper_model: str = "base",
        tts_backend: str = "coqui"
    ):
        """
        Inicializa gerenciador de voz.
        
        Args:
            use_whisper: Usar Whisper para STT (True) ou Google STT (False)
            use_advanced_tts: Usar Coqui TTS (True) ou pyttsx3 (False)
            whisper_model: Modelo Whisper (tiny, base, small, medium, large)
            tts_backend: Backend TTS (coqui ou pyttsx3)
        """
        self.stt_module = None
        self.tts_module = None
        
        # Inicializar STT
        if use_whisper:
            try:
                from modules.input.whisper_module import WhisperModule
                self.stt_module = WhisperModule(model_name=whisper_model)
                logger.info("Whisper STT inicializado")
            except Exception as e:
                logger.warning(f"Falha ao inicializar Whisper: {e}. Usando fallback.")
                use_whisper = False
        
        if not use_whisper:
            try:
                from modules.input.voice_module import VoiceModule
                self.stt_module = VoiceModule()
                logger.info("Google STT inicializado")
            except Exception as e:
                logger.error(f"Falha ao inicializar STT: {e}")
        
        # Inicializar TTS
        if use_advanced_tts:
            try:
                from modules.input.advanced_tts import AdvancedTTSModule
                self.tts_module = AdvancedTTSModule(backend=tts_backend)
                logger.info("Coqui TTS inicializado")
            except Exception as e:
                logger.warning(f"Falha ao inicializar Coqui TTS: {e}. Usando fallback.")
                use_advanced_tts = False
        
        if not use_advanced_tts:
            try:
                from modules.input.advanced_tts import FallbackTTSModule
                self.tts_module = FallbackTTSModule()
                logger.info("Fallback TTS (pyttsx3) inicializado")
            except Exception as e:
                logger.error(f"Falha ao inicializar TTS: {e}")
    
    def listen(self, duration: float = 5.0) -> Optional[str]:
        """Escuta e transcreve fala."""
        if not self.stt_module:
            logger.error("STT module não disponível")
            return None
        
        return self.stt_module.listen(duration)
    
    def speak(self, text: str, async_mode: bool = False):
        """Fala texto."""
        if not self.tts_module:
            logger.error("TTS module não disponível")
            print(f"JARVIS: {text}")
            return
        
        if async_mode and hasattr(self.tts_module, 'speak_async'):
            self.tts_module.speak_async(text)
        else:
            self.tts_module.speak(text)
    
    def is_available(self) -> bool:
        """Verifica se módulos estão disponíveis."""
        return self.stt_module is not None and self.tts_module is not None


class JarvisIntegrationManager:
    """Gerenciador de integrações (Calendar, Email, etc)."""
    
    def __init__(self):
        """Inicializa gerenciador de integrações."""
        self.calendar = None
        self.email = None
        
        # Tentar inicializar integrações
        self._init_calendar()
        self._init_email()
    
    def _init_calendar(self):
        """Inicializa integração de calendário."""
        try:
            from modules.action.calendar_integration import CalendarIntegration
            self.calendar = CalendarIntegration(provider="google")
            if self.calendar.is_available():
                logger.info("Calendar integration disponível")
            else:
                self.calendar = None
        except Exception as e:
            logger.warning(f"Calendar integration não disponível: {e}")
    
    def _init_email(self):
        """Inicializa integração de email."""
        try:
            from modules.action.email_integration import EmailIntegration
            self.email = EmailIntegration(provider="gmail")
            if self.email.is_available():
                logger.info("Email integration disponível")
            else:
                self.email = None
        except Exception as e:
            logger.warning(f"Email integration não disponível: {e}")
    
    def has_calendar(self) -> bool:
        """Verifica se calendar está disponível."""
        return self.calendar is not None
    
    def has_email(self) -> bool:
        """Verifica se email está disponível."""
        return self.email is not None


class JarvisCore:
    """
    Classe principal do JARVIS 5.0 com todos os novos recursos integrados.
    """
    
    def __init__(
        self,
        use_whisper: bool = True,
        use_advanced_tts: bool = True,
        enable_wake_word: bool = False,
        enable_security: bool = True,
        enable_task_planning: bool = True
    ):
        """
        Inicializa JARVIS 5.0 completo.
        
        Args:
            use_whisper: Usar Whisper para STT
            use_advanced_tts: Usar Coqui TTS
            enable_wake_word: Habilitar wake word detector
            enable_security: Habilitar sistema de segurança
            enable_task_planning: Habilitar planejamento de tarefas
        """
        logger.info("Inicializando JARVIS 5.0...")
        
        # Voice Manager
        self.voice = JarvisVoiceManager(
            use_whisper=use_whisper,
            use_advanced_tts=use_advanced_tts
        )
        
        # Integration Manager
        self.integrations = JarvisIntegrationManager()
        
        # Persistent Memory
        from modules.memory.persistent_memory import PersistentMemory
        self.memory = PersistentMemory()
        
        # Security Manager
        if enable_security:
            from modules.system.security_module import SecurityManager
            self.security = SecurityManager()
        else:
            self.security = None
        
        # Task Planning
        if enable_task_planning:
            from modules.processing.task_decomposition import TaskDecomposer, TaskExecutor
            self.task_decomposer = TaskDecomposer()
            self.task_executor = TaskExecutor()
        else:
            self.task_decomposer = None
            self.task_executor = None
        
        # Wake Word Detector
        self.wake_word_detector = None
        if enable_wake_word:
            self._init_wake_word()
        
        logger.info("JARVIS 5.0 inicializado com sucesso!")
    
    def _init_wake_word(self):
        """Inicializa wake word detector."""
        try:
            from modules.input.wake_word_detector import SimpleWakeWordDetector
            self.wake_word_detector = SimpleWakeWordDetector(
                keywords=["jarvis", "hey jarvis"],
                callback=self._on_wake_word
            )
            logger.info("Wake word detector inicializado")
        except Exception as e:
            logger.warning(f"Wake word detector não disponível: {e}")
    
    def _on_wake_word(self, keyword: str):
        """Callback quando wake word detectada."""
        logger.info(f"Wake word detectada: {keyword}")
        self.voice.speak("Sim, senhor?")
        
        # Escutar comando
        command = self.voice.listen(duration=5.0)
        if command:
            self.process_command(command)
    
    def process_command(self, command: str) -> str:
        """
        Processa comando do usuário.
        
        Args:
            command: Comando em texto
        
        Returns:
            Resposta do sistema
        """
        logger.info(f"Processando comando: {command}")
        
        # Salvar na memória
        self.memory.save_conversation("user", command)
        
        # Verificar segurança
        if self.security:
            if not self.security.check_permission(command):
                response = "Você não tem permissão para executar esse comando."
                self.memory.save_conversation("assistant", response)
                return response
            
            is_safe, reason = self.security.is_safe_command(command)
            if not is_safe:
                response = f"Comando bloqueado por segurança: {reason}"
                self.memory.save_conversation("assistant", response)
                return response
        
        # TODO: Adicionar lógica de processamento de comando
        # Por enquanto, resposta genérica
        response = f"Comando recebido: {command}"
        
        # Salvar resposta
        self.memory.save_conversation("assistant", response)
        
        return response
    
    def speak_and_process(self, text: Optional[str] = None, duration: float = 5.0):
        """
        Modo interativo: escuta, processa e responde.
        
        Args:
            text: Texto para falar antes de escutar (opcional)
            duration: Duração máxima da escuta
        """
        # Falar prompt se fornecido
        if text:
            self.voice.speak(text)
        
        # Escutar
        command = self.voice.listen(duration)
        
        if command:
            # Processar
            response = self.process_command(command)
            
            # Falar resposta
            self.voice.speak(response)
            
            return response
        else:
            self.voice.speak("Desculpe, não entendi.")
            return None
    
    def start_wake_word_mode(self):
        """Inicia modo wake word (hands-free)."""
        if not self.wake_word_detector:
            logger.error("Wake word detector não está disponível")
            return False
        
        self.wake_word_detector.start()
        logger.info("JARVIS em modo wake word - diga 'Hey JARVIS'")
        return True
    
    def stop_wake_word_mode(self):
        """Para modo wake word."""
        if self.wake_word_detector:
            self.wake_word_detector.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema."""
        return {
            "voice_available": self.voice.is_available(),
            "calendar_available": self.integrations.has_calendar(),
            "email_available": self.integrations.has_email(),
            "security_enabled": self.security is not None,
            "task_planning_enabled": self.task_decomposer is not None,
            "wake_word_active": self.wake_word_detector and self.wake_word_detector.is_active(),
            "memory_stats": self.memory.get_stats()
        }


# Função de conveniência para inicialização rápida
def quick_start(
    mode: str = "full",
    wake_word: bool = False
) -> JarvisCore:
    """
    Inicialização rápida do JARVIS.
    
    Args:
        mode: "full" (todos os recursos), "basic" (recursos básicos), "voice" (apenas voz)
        wake_word: Habilitar wake word detector
    
    Returns:
        Instância do JarvisCore
    """
    if mode == "basic":
        return JarvisCore(
            use_whisper=False,
            use_advanced_tts=False,
            enable_wake_word=False,
            enable_task_planning=False
        )
    elif mode == "voice":
        return JarvisCore(
            use_whisper=True,
            use_advanced_tts=True,
            enable_wake_word=wake_word,
            enable_task_planning=False
        )
    else:  # full
        return JarvisCore(
            use_whisper=True,
            use_advanced_tts=True,
            enable_wake_word=wake_word,
            enable_task_planning=True
        )


if __name__ == "__main__":
    # Exemplo de uso
    print("Inicializando JARVIS 5.0...")
    jarvis = quick_start(mode="full", wake_word=False)
    
    # Ver status
    status = jarvis.get_status()
    print("\nStatus do Sistema:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Modo interativo
    print("\nModo Interativo (pressione Ctrl+C para sair)")
    try:
        while True:
            jarvis.speak_and_process("Como posso ajudar?", duration=5.0)
    except KeyboardInterrupt:
        print("\nEncerrando JARVIS...")
        jarvis.stop_wake_word_mode()
