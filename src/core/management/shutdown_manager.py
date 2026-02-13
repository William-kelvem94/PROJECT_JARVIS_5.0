import logging
import time
import threading
from PyQt6.QtCore import QTimer, QCoreApplication
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class ShutdownManager:
    """Gerencia shutdown ordenado de todos os componentes"""
    
    SHUTDOWN_SEQUENCE = [
        ("ðŸŽ¤ Audio System", "stop_listening", 1.0),
        ("ðŸ‘ï¸ Vision System", "stop_monitoring", 1.0),
        ("ðŸ§  Neural Systems", "shutdown", 2.0),
        ("ðŸ’¾ Memory Systems", "flush_and_close", 3.0),
        ("ðŸ–¥ï¸ GUI Systems", "shutdown", 1.0), # Alterado para chamar shutdown() do WindowManager
        ("ðŸ“Š Monitoring", "stop_all_monitors", 0.5),
        ("âš™ï¸ Core Engine", "shutdown_engine", 2.0),
    ]
    
    def __init__(self, jarvis_core):
        self.jarvis = jarvis_core
        self.shutdown_in_progress = False
        
    def graceful_shutdown(self, exit_code=0):
        """Executa shutdown ordenado"""
        if self.shutdown_in_progress:
            return
            
        self.shutdown_in_progress = True
        logger.info("ðŸš€ Iniciando shutdown ordenado...")
        
        # Desativa hotkeys primeiro
        if hasattr(self.jarvis, 'window_manager') and self.jarvis.window_manager:
            try:
                self.jarvis.window_manager.unregister_hotkeys()
            except Exception: pass
        
        # Executa sequÃªncia de shutdown
        for component_name, method_name, timeout in self.SHUTDOWN_SEQUENCE:
            try:
                self._shutdown_component(component_name, method_name, timeout)
            except Exception as e:
                logger.error(f"âŒ Erro em {component_name}: {e}")
                continue
        
        logger.info("âœ… Shutdown completado com sucesso. Encerrando aplicaÃ§Ã£o Qt...")
        
        # Fecha aplicaÃ§Ã£o Qt com seguranÃ§a
        if QApplication.instance():
            QApplication.instance().quit()
            
    def _shutdown_component(self, name: str, method: str, timeout: float):
        """Desliga um componente especÃ­fico"""
        logger.info(f"ðŸ”„ Desligando {name}...")
        
        # Mapeamento de componentes para atributos do JarvisSingularity
        component_map = {
            "ðŸŽ¤ Audio System": "audio_system",
            "ðŸ‘ï¸ Vision System": "vision_system",
            "ðŸ§  Neural Systems": "neural_systems",
            "ðŸ’¾ Memory Systems": "memory_manager",
            "ðŸ–¥ï¸ GUI Systems": "window_manager",
            "ðŸ“Š Monitoring": "proactive_monitor",
            # Core Engine geralmente refere-se ao prÃ³prio loop ou integraÃ§Ã£o, pode nÃ£o ter um mÃ©todo direto
        }
        
        attr_name = component_map.get(name)
        if not attr_name:
            return

        component = getattr(self.jarvis, attr_name, None)
        
        if component:
            try:
                # Se o mÃ©todo existir, chama
                if hasattr(component, method):
                    func = getattr(component, method)
                    func()
                elif hasattr(component, 'stop'): # Fallback comum
                     component.stop()
                elif hasattr(component, 'cleanup'): # Outro fallback comum
                     component.cleanup()
                
                # Aguarda timeout (simulado para threads que nÃ£o bloqueiam)
                # Em um cenÃ¡rio real, join() seria ideal, mas timeout funciona para forÃ§ar progresso
                # time.sleep(timeout) -> Removido para shutdown mais Ã¡gil, ou reduzido
                
                logger.info(f"âœ… {name} desligado")
            except Exception as e:
                logger.warning(f"âš ï¸ {name} falhou: {e}")
