import logging
import threading
from typing import Dict, Any, Optional

from src.core.management.shutdown_manager import ShutdownManager
from src.core.management.fallback_system import FallbackSystem
from src.core.intelligence.context_sanitizer import ContextSanitizer
from src.core.audio.voice_filter import AtomicVoiceFilter
from src.core.security.security_manager import SecurityManager
from src.core.iot.iot_manager import IOTManager

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
            ("🔐 Security", self._init_security),
            ("🎤 Voice Filter", self._init_voice_filter),
            ("🛡️ Fallback System", self._init_fallback_system),
            ("🏠 IoT Manager", self._init_iot),
            ("⚙️ Management", self._init_management),
            ("🖥️ Interface Orchestration", self._init_interface_orchestration)
        ]
        
        success_count = 0
        critical_failures = []
        
        for name, init_func in initialization_sequence:
            try:
                # logger.info(f"⚡ [INIT] {name}...")
                init_func()
                # logger.info(f"✅ [OK] {name}")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ [FALHA] {name}: {e}")
                critical_failures.append((name, str(e)))
                # Não paramos a inicialização, mas logamos erro crítico
                
        self.is_ready = (success_count == len(initialization_sequence))
        
        if critical_failures:
            logger.warning(f"⚠️ Inicialização com falhas: {len(critical_failures)} componentes falharam")
            for name, error in critical_failures:
                logger.warning(f"   • {name}: {error}")
                
        logger.info(f"✨ Stark 2.0 Inicializado: {'Sucesso' if self.is_ready else 'Parcial'} ({success_count}/{len(initialization_sequence)})")
        
    def _init_sanitizers(self):
        # Sanitizers são estáticos/classe, mas podemos configurar algo se necessário
        # Se tivessem estado, instanciariamos aqui.
        pass
        
    def _init_security(self):
        """Inicializa o sistema de segurança"""
        try:
            self.security = SecurityManager()
            self.components["security"] = self.security
            logger.info("🔐 Sistema de Segurança inicializado")
        except Exception as e:
            logger.error(f"❌ Falha na inicialização do Security: {e}")
            raise
        
    def _init_voice_filter(self):
        pass
        
    def _init_iot(self):
        """Inicializa o gerenciador de dispositivos IoT"""
        try:
            self.iot_manager = IOTManager()
            self.components["iot"] = self.iot_manager
            if self.iot_manager.is_configured:
                logger.info("🏠 IoT Manager configurado e pronto")
            else:
                logger.warning("🏠 IoT Manager inicializado mas não configurado (adicione iot.ha_token)")
        except Exception as e:
            logger.error(f"❌ Falha na inicialização do IoT: {e}")
            # IoT não é crítico, então não interrompemos
        
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
                
            elif module_name == "security":
                if "security" in self.components:
                    return "ONLINE"
                return "DEGRADED"
                
            elif module_name == "iot":
                if "iot" in self.components:
                    iot_mgr = self.components["iot"]
                    if hasattr(iot_mgr, 'is_configured') and iot_mgr.is_configured:
                        return "ONLINE"
                    else:
                        return "DEGRADED"  # Inicializado mas não configurado
                return "OFFLINE"
                
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
        modules = ["vision", "audio", "intelligence", "actions", "security", "iot", "infrastructure"]
        return {module: self.get_module_status(module) for module in modules}
    
    def is_system_healthy(self) -> bool:
        """
        Verifica se o sistema está saudável (nenhum módulo OFFLINE)
        
        Returns:
            bool: True se todos módulos estão ONLINE ou DEGRADED
        """
        health = self.get_system_health()
        return all(status != "OFFLINE" for status in health.values())
    
    def restart_component(self, component_name: str) -> bool:
        """
        Reinicializa um componente específico
        
        Args:
            component_name: Nome do componente (security, iot, fallback, etc.)
            
        Returns:
            bool: True se reinicialização foi bem-sucedida
        """
        init_methods = {
            "security": self._init_security,
            "iot": self._init_iot,
            "fallback": self._init_fallback_system,
            "management": self._init_management,
        }
        
        if component_name not in init_methods:
            logger.error(f"❌ Componente '{component_name}' não reconhecido")
            return False
        
        try:
            logger.info(f"🔄 Reinicializando {component_name}...")
            # Remove componente anterior se existir
            if component_name in self.components:
                del self.components[component_name]
            
            # Reinicializa
            init_methods[component_name]()
            logger.info(f"✅ {component_name} reinicializado com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Falha na reinicialização de {component_name}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Retorna informações detalhadas sobre o sistema
        
        Returns:
            Dict com informações completas do sistema
        """
        return {
            "is_ready": self.is_ready,
            "components_count": len(self.components),
            "registered_components": list(self.components.keys()),
            "module_health": self.get_system_health(),
            "system_healthy": self.is_system_healthy(),
            "jarvis_core_available": self.jarvis is not None
        }
