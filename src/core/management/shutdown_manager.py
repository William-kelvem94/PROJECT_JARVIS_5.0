import logging
import time
import threading
from PyQt6.QtCore import QTimer, QCoreApplication
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class ShutdownManager:
    """Gerencia shutdown ordenado de todos os componentes"""
    
    SHUTDOWN_SEQUENCE = [
        ("🎤 Audio System", "stop_listening", 1.0),
        ("👁️ Vision System", "stop_monitoring", 1.0),
        ("🧠 Neural Systems", "shutdown", 2.0),
        ("💾 Memory Systems", "flush_and_close", 3.0),
        ("🖥️ GUI Systems", "shutdown", 1.0), # Alterado para chamar shutdown() do WindowManager
        ("📊 Monitoring", "stop_all_monitors", 0.5),
        ("⚙️ Core Engine", "shutdown_engine", 2.0),
    ]
    
    def __init__(self, jarvis_core):
        self.jarvis = jarvis_core
        self.shutdown_in_progress = False
        
    def graceful_shutdown(self, exit_code=0):
        """Executa shutdown ordenado"""
        if self.shutdown_in_progress:
            return
            
        self.shutdown_in_progress = True
        logger.info("🚀 Iniciando shutdown ordenado...")
        
        # Desativa hotkeys primeiro
        if hasattr(self.jarvis, 'window_manager') and self.jarvis.window_manager:
            try:
                self.jarvis.window_manager.unregister_hotkeys()
            except Exception: pass
        
        # Executa sequência de shutdown
        for component_name, method_name, timeout in self.SHUTDOWN_SEQUENCE:
            try:
                self._shutdown_component(component_name, method_name, timeout)
            except Exception as e:
                logger.error(f"❌ Erro em {component_name}: {e}")
                continue
        
        logger.info("✅ Shutdown completado com sucesso. Encerrando aplicação Qt...")
        
        # Fecha aplicação Qt com segurança
        if QApplication.instance():
            QApplication.instance().quit()
            
    def _shutdown_component(self, name: str, method: str, timeout: float):
        """Desliga um componente específico"""
        logger.info(f"🔄 Desligando {name}...")
        
        # Mapeamento de componentes para atributos do JarvisSingularity
        component_map = {
            "🎤 Audio System": "audio_system",
            "👁️ Vision System": "vision_system",
            "🧠 Neural Systems": "neural_systems",
            "💾 Memory Systems": "memory_manager",
            "🖥️ GUI Systems": "window_manager",
            "📊 Monitoring": "proactive_monitor",
            # Core Engine geralmente refere-se ao próprio loop ou integração, pode não ter um método direto
        }
        
        attr_name = component_map.get(name)
        if not attr_name:
            return

        component = getattr(self.jarvis, attr_name, None)
        
        if component:
            try:
                # Se o método existir, chama
                if hasattr(component, method):
                    func = getattr(component, method)
                    func()
                elif hasattr(component, 'stop'): # Fallback comum
                     component.stop()
                elif hasattr(component, 'cleanup'): # Outro fallback comum
                     component.cleanup()
                
                # Aguarda timeout (simulado para threads que não bloqueiam)
                # Em um cenário real, join() seria ideal, mas timeout funciona para forçar progresso
                # time.sleep(timeout) -> Removido para shutdown mais ágil, ou reduzido
                
                logger.info(f"✅ {name} desligado")
            except Exception as e:
                logger.warning(f"⚠️ {name} falhou: {e}")
