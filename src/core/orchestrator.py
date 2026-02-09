import logging
import threading
from typing import Dict, Any, Optional

from src.core.management.shutdown_manager import ShutdownManager
from src.core.management.fallback_system import FallbackSystem
from src.core.intelligence.context_sanitizer import ContextSanitizer
from src.core.audio.voice_filter import AtomicVoiceFilter

logger = logging.getLogger(__name__)

class StarkOrchestrator:
    """
    Orquestrador Supremo da Arquitetura Stark 2.0.
    Responsável pela inicialização ordenada, injeção de dependências e health-check.
    """
    
    def __init__(self, jarvis_core):
        self.jarvis = jarvis_core
        self.components: Dict[str, Any] = {}
        self.is_ready = False
        
    def initialize_stark_system(self):
        """Inicializa todo o sistema Stark 2.0 em ordem de dependência"""
        logger.info("🚀 Inicializando Protocolo Stark 2.0...")
        
        initialization_sequence = [
            ("🛡️ Sanitizer", self._init_sanitizers),
            ("🎤 Voice Filter", self._init_voice_filter),
            ("🛡️ Fallback System", self._init_fallback_system),
            ("⚙️ Management", self._init_management),
            ("🖥️ Interface Orchestration", self._init_interface_orchestration)
        ]
        
        success_count = 0
        
        for name, init_func in initialization_sequence:
            try:
                # logger.info(f"⚡ [INIT] {name}...")
                init_func()
                # logger.info(f"✅ [OK] {name}")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ [FALHA] {name}: {e}")
                # Não paramos a inicialização, mas logamos erro crítico
                
        self.is_ready = (success_count == len(initialization_sequence))
        logger.info(f"✨ Stark 2.0 Inicializado: {'Sucesso' if self.is_ready else 'Parcial'}")
        
    def _init_sanitizers(self):
        # Sanitizers são estáticos/classe, mas podemos configurar algo se necessário
        # Se tivessem estado, instanciariamos aqui.
        pass
        
    def _init_voice_filter(self):
        pass
        
    def _init_fallback_system(self):
        self.fallback_system = FallbackSystem(self.jarvis)
        self.components["fallback"] = self.fallback_system
        
        # Injeta fallback no AIAgent se possível
        if hasattr(self.jarvis, 'ai_agent') and self.jarvis.ai_agent:
            self.jarvis.ai_agent.fallback_system = self.fallback_system
            
    def _init_management(self):
        # Shutdown Manager já é inicializado no main, mas podemos registrar aqui
        if hasattr(self.jarvis, 'shutdown_manager'):
            self.components["shutdown"] = self.jarvis.shutdown_manager
            
    def _init_interface_orchestration(self):
        if hasattr(self.jarvis, 'window_manager') and self.jarvis.window_manager:
            wm = self.jarvis.window_manager
            # Configura callbacks ou estados iniciais
            self.components["window_manager"] = wm
            
            # Se quisermos iniciar com o menu flutuante ou algo assim
            # wm.switch_mode(InterfaceMode.ORB) # Exemplo
