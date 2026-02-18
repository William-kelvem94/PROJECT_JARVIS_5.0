from src.core.management.shutdown_manager import ShutdownManager
from src.core.infrastructure.priority_scheduler import PriorityScheduler
from src.core.infrastructure.bootstrapper import SystemBootstrapper
import importlib
from src.core.config.blackbox_logger import setup_blackbox_integration, blackbox_logger
from src.core.config.system_manifest import system_manifest
import os
import sys
import time
import logging
import asyncio
import threading
import signal

# ─────────────────────────────────────────────────────────────────---------
# Configuration constants
DEFAULT_BOOT_CHECK_INTERVAL = 200  # ms
BOOT_FINALIZE_DELAY = 1000  # ms
PYTHON_ENCODING = "utf-8"
# ─────────────────────────────────────────────────────────────────---------

# 🛡️ EARLY ENVIRONMENT CONFIGURATION
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = PYTHON_ENCODING

# Configure Logging (Unified)

# mark as used to satisfy linters/static analysis (values are still
# available for runtime use)
_ = system_manifest
_ = blackbox_logger

# Initialize Foundation
try:
    setup_blackbox_integration()
    logger = logging.getLogger("BOOT")
    logger.info("📡 Blackbox Logging Integration Active")
except Exception as e:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("BOOT")
    logger.error(f"Foundation setup failed: {e}")


# 🛡️ GLOBAL MONKEY PATCHES (Safety checks)


def _apply_openvino_patch(openvino_module):
    """Patch specific to OpenVINO: expose Node from openvino.runtime if present."""
    if "openvino.runtime" in sys.modules:
        node_cls = getattr(sys.modules["openvino.runtime"], "Node", None)
        if node_cls is not None and not hasattr(openvino_module, "Node"):
            setattr(openvino_module, "Node", node_cls)
            logger.debug("Applied OpenVINO Node patch")


def apply_patches():
    """Applies optional runtime patches safely (non-fatal)."""
    patches = [
        ("openvino", _apply_openvino_patch),
        ("transformers", lambda mod: None),  # placeholder for future patches
    ]

    for module_name, patch_func in patches:
        try:
            module = importlib.import_module(module_name)
            try:
                patch_func(module)
            except Exception as e:
                logger.debug(f"Patch for {module_name} failed: {e}")
        except ImportError:
            logger.debug(f"{module_name} not available - skipping patch")
        except Exception as e:
            logger.debug(f"Unexpected error importing {module_name}: {e}")


apply_patches()

# Import Core Components

# Qt Imports (Conditional)

QtCore = None
QtWidgets = None
QT_AVAILABLE = False
try:
    QtCore = importlib.import_module("PyQt6.QtCore")
    QtWidgets = importlib.import_module("PyQt6.QtWidgets")
    QObject = getattr(QtCore, "QObject")
    pyqtSignal = getattr(QtCore, "pyqtSignal")
    pyqtSlot = getattr(QtCore, "pyqtSlot")
    QTimer = getattr(QtCore, "QTimer")
    QApplication = getattr(QtWidgets, "QApplication")
    QT_AVAILABLE = True
except Exception:
    QT_AVAILABLE = False

    class QObject:
        pass


# ============================================================================
# JARVIS CORE APPLICATION
# ============================================================================
class JarvisSingularity(QObject):
    """
    Main Application Controller.
    Orchestrates interaction between the GUI, AI Agent, and Perception Systems.
    """

    if QT_AVAILABLE:
        transcription_received = pyqtSignal(object)
        hud_update_requested = pyqtSignal(str, str)

    def __init__(self, app, instances):
        super().__init__()
        self.app = app
        self.instances = instances

        # Unpack instances
        self.window_manager = instances.get("window_manager")
        self.ai_agent = instances.get("ai_agent")
        self.audio_system = instances.get("audio_system")
        self.vision_system = instances.get("vision_system")
        self.event_bus = instances.get("async_event_bus") or instances.get("event_bus")
        self.scheduler = instances.get("priority_scheduler") or PriorityScheduler()

        # Estado inicializado de forma clara
        self._initialize_state()

        # Subsystems
        self.shutdown_manager = ShutdownManager(self)

        # Connect Signals
        if QT_AVAILABLE:
            self.transcription_received.connect(self._on_transcription)
            self.hud_update_requested.connect(self._on_hud_update)
            self._setup_signals()

        logger.info("✨ Singularity Core Initialized")

    def _initialize_state(self):
        """Inicializa o estado básico do núcleo JARVIS."""
        self.is_running = False
        self.last_interaction_time = 0
        self._services_started = False

    def _setup_signals(self):
        # Use variadic lambda to avoid unused-parameter linter hints
        signal.signal(signal.SIGINT, lambda *args: self.shutdown())
        signal.signal(signal.SIGTERM, lambda *args: self.shutdown())

    def start(self):
        """Starts the main event loops and background services."""
        if self._services_started:
            logger.warning("Services already started - skipping redundant start")
            return
        self._services_started = True

        self.is_running = True
        logger.info("🚀 Starting JARVIS Services...")

        # Start Scheduler
        threading.Thread(target=self._run_scheduler, daemon=True).start()

        # Start Audio Listening
        if self.audio_system:
            if self.audio_system.start_listening():
                # Em modo headless (sem Qt), usar callback direto em vez de sinal Qt
                if QT_AVAILABLE and self.app:
                    self.audio_system.on_transcription = self.transcription_received.emit
                else:
                    # Headless: processar transcrição diretamente via thread
                    def _headless_transcription_callback(result):
                        if result and getattr(result, "text", ""):
                            threading.Thread(
                                target=self._process_command,
                                args=(result.text,),
                                daemon=True,
                            ).start()
                    self.audio_system.on_transcription = _headless_transcription_callback
                logger.info("🎙️ Audio System Listening")

        # Start Vision
        if self.vision_system:
            # Trigger background loading
            threading.Thread(
                target=self.vision_system.start_background_loading, daemon=True
            ).start()

        # Connect GUI
        if self.window_manager:
            from src.interface.window_manager import InterfaceMode

            self.window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)
            self.window_manager.jarvis_core = self

        # ✅ ACIONAR PROTOCOLO DE FINALIZAÇÃO DE BOOT (Correção Definitiva)
        # Usa QTimer para garantir que rode na thread principal do Qt após breve delay
        if QT_AVAILABLE and self.app:
            QTimer.singleShot(BOOT_FINALIZE_DELAY, self._finalize_boot_sequence)
        else:
            # Em modo headless, roda direto
            threading.Thread(target=self._finalize_boot_sequence_headless, daemon=True).start()

    def _finalize_boot_sequence(self):
        """Garante que a UI e o EventBus estejam sincronizados no estado ONLINE."""
        # Import locally to avoid module import cycles during bootstrap
        from src.interface.ui_signals import ui_signals
        from src.core.infrastructure.async_event_bus import EventType

        def _update_ui_state():
            ui_signals.update_boot_stage.emit("SYSTEM ONLINE", 100)
            ui_signals.update_status.emit("ONLINE")
            ui_signals.update_listening_state.emit(True)

        def _publish_system_event():
            # Use getattr to safely access EventType members that might be dynamically added or renamed
            event_type_online = getattr(EventType, "SYSTEM_ONLINE", None)
            if self.event_bus and event_type_online:
                self.event_bus.publish(event_type_online, {
                    "timestamp": time.time(),
                    "status": "fully_operational"
                })

        def _do_finalize():
            logger.info("🔧 Finalizing Boot Sequence (UI Thread)...")
            try:
                _update_ui_state()
                _publish_system_event()
                logger.info("✅ Boot Sequence Finalized: HUD Online & Events Active")
            except Exception as e:
                logger.error(f"❌ Error finalizing boot: {e}")

        # Garantir execução na main thread
        if QT_AVAILABLE and self.app:
            QTimer.singleShot(0, _do_finalize)
        else:
            _do_finalize()

    def _finalize_boot_sequence_headless(self):
        """Versão headless da finalização de boot"""
        time.sleep(BOOT_FINALIZE_DELAY / 1000)
        logger.info("🔧 Finalizing Boot Sequence (Headless)...")
        try:
             from src.core.infrastructure.async_event_bus import EventType
             if hasattr(self, 'event_bus') and self.event_bus and hasattr(EventType, 'SYSTEM_ONLINE'):
                self.event_bus.publish(getattr(EventType, 'SYSTEM_ONLINE'), {
                    "timestamp": time.time(),
                    "status": "fully_operational_headless"
                })
        except Exception as e:
            logger.error(f"❌ Error finalizing boot (headless): {e}")

    async def _run_scheduler_async(self):
        """Versão assíncrona do scheduler que mantém o loop enquanto o core estiver rodando."""
        try:
            await self.scheduler.start()
            while self.is_running:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")

    def _run_scheduler(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_scheduler_async())
        except Exception as e:
            logger.error(f"❌ Scheduler thread died: {e}")
        finally:
            loop.close()
            logger.info("Scheduler loop closed")

    def shutdown(self):
        logger.info("🛑 Shutting down...")
        self.is_running = False
        if self.app and QT_AVAILABLE:
            self.app.quit()
        sys.exit(0)

    # --- Signal Handlers ---

    if QT_AVAILABLE:

        @pyqtSlot(object)
        def _on_transcription(self, result):
            if not result or not result.text:
                return
            # Simple logic for now - process everything
            threading.Thread(
                target=self._process_command, args=(result.text,), daemon=True
            ).start()

        @pyqtSlot(str, str)
        def _on_hud_update(self, state, text):
            if self.window_manager:
                hud = self.window_manager.get_hud()
                if hud:
                    hud.update_state(state)
                    if text:
                        hud.show_response(text)

    def _process_command(self, text):
        if not self.ai_agent:
            return
        try:
            # Emitir sinal de status apenas se Qt estiver disponível
            if QT_AVAILABLE and self.app:
                self.hud_update_requested.emit("thinking", "")

            # Sync wrapper for async agent processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.ai_agent.process_command(text))
            loop.close()

            if QT_AVAILABLE and self.app:
                self.hud_update_requested.emit("speaking", str(response))

            # Speak response
            from src.core.audio.voice_controller import get_voice_controller

            vc = get_voice_controller()
            if vc:
                vc.speak(str(response))

            if QT_AVAILABLE and self.app:
                self.hud_update_requested.emit("idle", "")

        except Exception as e:
            logger.error(f"Error processing command: {e}")
            if QT_AVAILABLE and self.app:
                self.hud_update_requested.emit("error", "Erro ao processar")


# ============================================================================
# MAIN ENTRY POINT (lightweight starter)
# ============================================================================
def _enforce_single_instance():
    """Ensure no other JARVIS instance is running"""
    import psutil
    pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == pid: continue
            cmd = proc.info.get('cmdline') or []
            # Check strictly for python running this main.py
            if 'python' in proc.info['name'].lower() and any('main.py' in str(s) for s in cmd):
                 logger.warning(f"Concurrent JARVIS found (PID {proc.info['pid']}). Aborting.")
                 sys.exit(0)
        except Exception:
            pass

def main():
    _enforce_single_instance()
    """Lightweight launcher that delegates to SystemBootstrapper/BootManager.

    Responsibilities:
    - Minimal startup logic and environment checks
    - Delegate component initialization to SystemBootstrapper
    - Perform optional Ollama health-check after bootstrap
    - Keep `JarvisSingularity` class intact for tests and backward compatibility
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS 5.0 - Singularity (light boot)"
    )
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Prepare GUI only if requested and available
    app = None
    if not args.headless and QT_AVAILABLE:
        app = QApplication(sys.argv)
    elif not args.headless and not QT_AVAILABLE:
        logger.warning("PyQt6 not available — switching to headless mode")
        args.headless = True

    # Create bootstrapper (delegates heavy lifting to BootManager)
    bootstrapper = SystemBootstrapper(app)

    # Run bootstrap synchronously for headless, or in background for GUI so
    # the GUI event loop can start immediately.
    boot_result = {"status": "init", "instances": {}}

    def _run_boot_in_thread():
        import asyncio

        try:
            boot_result["instances"] = asyncio.run(bootstrapper.bootstrap())
            boot_result["status"] = "success"
        except Exception as e:
            logger.critical(f"Bootstrap failed: {e}")
            boot_result["status"] = "failed"
            boot_result["error"] = e

    if app:
        # Start bootstrap in background to keep GUI responsive
        t = threading.Thread(target=_run_boot_in_thread, daemon=True)
        t.start()

        # Periodically check bootstrap status and start JarvisSingularity when
        # ready
        timer = QTimer()

        def _check_and_start():
            if boot_result["status"] == "success":
                timer.stop()
                jarvis = JarvisSingularity(app, boot_result["instances"])
                jarvis.start()
                # Manter referência para evitar garbage collection
                app._jarvis = jarvis
            elif boot_result["status"] == "failed":
                timer.stop()
                logger.critical("Boot failed — exiting GUI")
                app.quit()

        timer.timeout.connect(_check_and_start)
        timer.start(DEFAULT_BOOT_CHECK_INTERVAL)  # Checar a cada DEFAULT_BOOT_CHECK_INTERVAL ms
        sys.exit(app.exec())

    # HEADLESS path — run bootstrap synchronously
    _run_boot_in_thread()

    if boot_result["status"] != "success":
        logger.critical("Boot failed — aborting")
        sys.exit(1)

    # Optional: quick Ollama health check (best-effort)
    try:
        from src.core.intelligence.ollama_manager import ollama_manager

        try:
            if not ollama_manager.is_server_running():
                logger.info("Ollama appears offline; attempting best-effort start")
                ollama_manager.ensure_server_running()
        except Exception as _:
            logger.debug("Ollama health-check failed (non-fatal)")
    except Exception:
        # OllamaManager may not be present in all builds — ignore
        pass

    jarvis = JarvisSingularity(None, boot_result["instances"])
    jarvis.start()

    # Keep main process alive while components run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received — shutting down")


if __name__ == "__main__":
    main()
