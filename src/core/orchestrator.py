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
    
    def get_module_status(self, module_name: str) -> str:
        """
        Retorna status real do módulo baseado em health checks
        
        Args:
            module_name: Nome do módulo (vision, audio, intelligence, actions, infrastructure)
        
        Returns:
            str: ONLINE (totalmente funcional), DEGRADED (parcial), OFFLINE (inoperante)
        """
        try:
            if module_name == "vision":
                from src.core.vision.vision_system import vision_system
                if vision_system and hasattr(vision_system, 'is_ready'):
                    # Verifica se componentes críticos estão disponíveis
                    has_ocr = hasattr(vision_system, 'ocr_reader') and vision_system.ocr_reader is not None
                    has_yolo = hasattr(vision_system, 'yolo_model') and vision_system.yolo_model is not None
                    if has_ocr and has_yolo:
                        return "ONLINE"
                    elif has_ocr or has_yolo:
                        return "DEGRADED"
                return "OFFLINE"
                
            elif module_name == "audio":
                from src.core.audio.voice_controller import voice_controller
                if voice_controller:
                    # Verifica se STT e TTS estão operacionais
                    has_stt = hasattr(voice_controller, 'recognizer')
                    has_tts = hasattr(voice_controller, 'tts_engine')
                    if has_stt and has_tts:
                        return "ONLINE"
                    elif has_stt or has_tts:
                        return "DEGRADED"
                return "OFFLINE"
                
            elif module_name == "intelligence":
                from src.core.intelligence.ai_agent import ai_agent
                if ai_agent and hasattr(ai_agent, 'brain_router'):
                    return "ONLINE"
                return "DEGRADED"
                
            elif module_name == "actions":
                from src.core.actions.action_controller import action_controller
                if action_controller:
                    return "ONLINE"
                return "DEGRADED"
                
            elif module_name == "infrastructure":
                # Verifica componentes básicos
                if self.is_ready and len(self.components) > 0:
                    return "ONLINE"
                return "DEGRADED"
                
            return "UNKNOWN"
            
        except ImportError as e:
            logger.warning(f"Módulo {module_name} não encontrado: {e}")
            return "OFFLINE"
        except Exception as e:
            logger.error(f"Erro ao verificar status de {module_name}: {e}")
            return "UNKNOWN"
    
    def get_system_health(self) -> Dict[str, str]:
        """
        Retorna status de todos os módulos principais
        
        Returns:
            Dict[str, str]: Dicionário com status de cada módulo
        """
        modules = ["vision", "audio", "intelligence", "actions", "infrastructure"]
        return {module: self.get_module_status(module) for module in modules}
    
    def is_system_healthy(self) -> bool:
        """
        Verifica se o sistema está saudável (nenhum módulo OFFLINE)
        
        Returns:
            bool: True se todos módulos estão ONLINE ou DEGRADED
        """
        health = self.get_system_health()
        return all(status != "OFFLINE" for status in health.values())
