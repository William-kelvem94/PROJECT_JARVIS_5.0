
import os
import sys
import logging
import signal
import threading
import time
from pathlib import Path

# ============================================================================
# CRITICAL SYSTEM PATCHES (BEFORE ANY IMPORTS)
# ============================================================================
try:
    import comtypes.client
    import comtypes.client._code_cache
    import shutil
    gen_dir = Path(comtypes.client._code_cache._get_gen_dir())
    if gen_dir.exists():
        shutil.rmtree(gen_dir, ignore_errors=True)
    os.makedirs(gen_dir, exist_ok=True)
    comtypes.client._code_cache._enable_cache = False
except Exception:
    pass

os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"

# ============================================================================
# PATH SETUP
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QObject, QThread, pyqtSignal

# ============================================================================
# ASYNC INITIALIZER THREAD
# ============================================================================
class SystemInitializer(QThread):
    """Carrega módulos pesados em background para não travar a UI"""
    progress = pyqtSignal(str)
    finished_ok = pyqtSignal()
    
    def run(self):
        try:
            self.progress.emit("🧠 Carregando AI Agent...")
            from core.ai_agent import ai_agent
            
            self.progress.emit("🎤 Inicializando Voz...")
            from core.voice_controller import voice_controller
            
            self.progress.emit("🧠 Carregando Memória (ChromaDB)...")
            from core.memory_manager import memory_manager
            memory_manager._ensure_initialized() # Forçar lazy load
            
            self.progress.emit("👁️ Ativando Visão (YOLO)...")
            from core.vision_enhancer import vision_enhancer
            
            self.progress.emit("⚙️ Configurando Sistema...")
            from core.system_controller import system_controller
            
            self.finished_ok.emit()
        except Exception as e:
            self.progress.emit(f"❌ Erro: {str(e)}")
            logging.error(f"Erro na inicialização: {e}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================
class JarvisSingularityV2(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("JARVIS Singularity V2")
        
        # Carregar HUD Mock (Premium) se o real falhar
        try:
            from interface.hud import JarvisHUD
            self.hud = JarvisHUD()
            # DEBUG: Verificar métodos disponíveis no objeto HUD
            methods = [m for m in dir(self.hud) if not m.startswith('_')]
            print(f"DEBUG: HUD inicializado. Métodos: {methods}")
            if not hasattr(self.hud, 'show_response'):
                print("⚠️ AVISO: show_response não encontrado no HUD! Tentando recarregar...")
        except Exception as e:
            print(f"❌ Erro ao carregar HUD Real: {e}")
            from main_singularity import MockHUD
            self.hud = MockHUD()
            
        self.hud.show()
        self.hud.update_state("thinking")
        self.hud.show_response("Iniciando J.A.R.V.I.S. Singularity...")
        
        # Iniciar carregamento assíncrono
        self.initializer = SystemInitializer()
        self.initializer.progress.connect(self._update_hud_status)
        self.initializer.finished_ok.connect(self._on_systems_ready)
        self.initializer.start()
        
        # Signal handling
        signal.signal(signal.SIGINT, lambda *args: self.app.quit())

    def _update_hud_status(self, msg):
        print(f"DEBUG: {msg}")
        if hasattr(self.hud, 'show_response'):
            self.hud.show_response(msg)

    def _on_systems_ready(self):
        self.hud.update_state("idle")
        self.hud.show_response("Sistemas Online. Aguardando comando...")
        
        # Inicializar AIWorker
        from interface.ai_worker import AIWorker
        self.ai_worker = AIWorker()
        self.ai_worker.status_changed.connect(self.hud.update_state)
        self.ai_worker.response_ready.connect(self.hud.show_response)
        
        # Iniciar escuta (Wake Word)
        from core.voice_controller import voice_controller
        voice_controller.listen_for_wake_word(
            wake_word="jarvis",
            on_wake=self._on_wake_word
        )
        print("✅ J.A.R.V.I.S. está pronto.")

    def _on_wake_word(self):
        self.hud.update_state("listening")
        QTimer.singleShot(500, self._process_voice_command)

    def _process_voice_command(self):
        from core.voice_controller import voice_controller
        def handle_cmd(text):
             if text:
                 self.ai_worker.process_command(text)
             else:
                 self.hud.update_state("idle")
        
        voice_controller.listen_once(on_command=handle_cmd)

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    jarvis = JarvisSingularityV2()
    sys.exit(jarvis.run())
