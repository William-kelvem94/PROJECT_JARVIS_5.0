import os
import sys
import warnings
import time
import platform
import logging
import asyncio
import threading
import shutil
import psutil
import signal
from pathlib import Path

# 🛡️ EARLY ENVIRONMENT CONFIGURATION (Critical for Windows/UTF-8)
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Set console to UTF-8 on Windows
if platform.system() == "Windows":
    try:
        import subprocess
        subprocess.run(["chcp", "65001"], check=True, capture_output=True)
    except:
        pass  # Ignore if fails

# Force UTF-8 encoding for file operations
import locale
try:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        pass  # Use system default if UTF-8 not available

# 🛡️ BLINDAGEM DE UNICODE DEFINITIVA
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 🛡️ EARLY WARNING SUPPRESSION
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*openvino.runtime.*')
warnings.filterwarnings('ignore', message='.*loss_type=None.*')

from src.core.infrastructure.priority_scheduler import PriorityScheduler, TaskPriority, TaskType
from src.core.config.system_manifest import system_manifest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/jarvis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Setup unified JARVIS logging system
try:
    from src.utils.jarvis_logger import setup_jarvis_logging, apply_global_duplicate_filter, get_component_logger
    
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    jarvis_logging_system = setup_jarvis_logging(data_dir)
    logger = jarvis_logging_system.get_logger('core')
    
    root_logger = logging.getLogger()
    apply_global_duplicate_filter(root_logger)
    
    jarvis_core_logger = logging.getLogger("JARVIS-CORE")
    apply_global_duplicate_filter(jarvis_core_logger)
    
    logger.info("🎯 JARVIS Unified Logging System initialized")
except Exception as e:
    logger = logging.getLogger("JARVIS-CORE")
    logger.error(f"❌ Failed to initialize unified logging: {e}")

# 🛡️ GLOBAL MONKEY PATCHES
try:
    import openvino  # noqa: F401  # type: ignore
    node_obj = getattr(openvino, 'Node', None)
    if not node_obj and 'openvino.runtime' in sys.modules:
        node_obj = getattr(sys.modules['openvino.runtime'], 'Node', None)
    if node_obj and not hasattr(openvino, 'Node'): openvino.Node = node_obj
        
    op_obj = getattr(openvino, 'op', None)
    if not op_obj and 'openvino.runtime' in sys.modules:
        op_obj = getattr(sys.modules['openvino.runtime'], 'op', None)
    if op_obj:
        sys.modules['openvino.op'] = op_obj
        if not hasattr(openvino, 'op'): openvino.op = op_obj
except ImportError:
    pass

try:
    from transformers import __version__ as transformers_version
    if transformers_version.startswith(('4.4', '4.3', '4.2')):
        try:
            from transformers.generation import BeamSearchScorer
        except ImportError:
            class _BeamSearchScorerNew: pass
            import transformers
            transformers.BeamSearchScorer = _BeamSearchScorerNew
    else:
        try:
            from transformers import generation_utils
            if not hasattr(generation_utils, 'BeamSearchScorer'):
                class _BeamSearchScorerOld: pass
                generation_utils.BeamSearchScorer = _BeamSearchScorerOld
        except ImportError:
            pass
except (ImportError, AttributeError, Exception):
    pass

# IMPORTS
# Try to import ShutdownManager
try:
    from src.core.management.shutdown_manager import ShutdownManager
    SHUTDOWN_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ShutdownManager not available: {e}")
    ShutdownManager = None
    SHUTDOWN_MANAGER_AVAILABLE = False

# Hardware Manager
try:
    from src.core.management.hardware_manager import get_hardware_manager
    hardware_manager = get_hardware_manager()
    HARDWARE_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"HardwareManager not available: {e}")
    hardware_manager = None
    HARDWARE_MANAGER_AVAILABLE = False

# StarkOrchestrator
try:
    from src.core.management.orchestrator import StarkOrchestrator
    STARK_ORCHESTRATOR_AVAILABLE = True
except (ImportError, AttributeError) as e:
    logger.warning(f"⚠️ StarkOrchestrator not available via management: {e}")
    StarkOrchestrator = None
    STARK_ORCHESTRATOR_AVAILABLE = False

# NeuroSync
try:
    from src.core.management.neuro_sync import neuro_sync
    NEURO_SYNC_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning(f"⚠️ NeuroSync not available: {e}")

# INFRASTRUCTURE IMPORTS (FIXED)
try:
    from src.core.infrastructure.boot_manager import BootManager, BootPriority
    BOOT_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ BootManager not available")
    BOOT_MANAGER_AVAILABLE = False
    BootManager = None
    BootPriority = None

try:
    from src.core.infrastructure.async_event_bus import AsyncEventBus
    EVENT_BUS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ AsyncEventBus not available")
    EVENT_BUS_AVAILABLE = False
    AsyncEventBus = None

try:
    from src.core.infrastructure.session_manager import SessionManager
except ImportError:
    logger.warning("⚠️ SessionManager not available")
    SessionManager = None

try:
    from src.core.infrastructure.watchdog import watchdog_system
except ImportError:
    logger.warning("⚠️ Watchdog System not available")
    watchdog_system = None

# Network Mesh Config
PROJECT_ROOT = Path(__file__).parent.absolute()
network_config = {}
network_config_path = PROJECT_ROOT / "config" / "network_mesh_config.yaml"
if network_config_path.exists():
    try:
        import yaml
        with open(network_config_path, 'r', encoding='utf-8') as f:
            network_config = yaml.safe_load(f) or {}
    except Exception:
        pass

# Torch Lazy Check
TORCH_AVAILABLE = False
torch = None

def _check_torch():
    global TORCH_AVAILABLE, torch
    if not TORCH_AVAILABLE:
        try:
            import torch as torch_module
            torch = torch_module
            TORCH_AVAILABLE = True
            return True
        except Exception:
            TORCH_AVAILABLE = False
            return False
    return True

# ============================================================================
# DIAGNOSTICS & HEALTH
# ============================================================================

def auto_diagnose():
    issues = []
    try:
        if _check_torch() and torch is not None:
            _ = torch.zeros(1)
    except Exception as e:
        issues.append({'level': 'CRITICAL', 'component': 'Neural Engine', 'error': str(e), 'fix': 'Check PyTorch'})
    
    if not any(Path('data/faces').glob("*.j*")):
        issues.append({'level': 'INFO', 'component': 'FaceID', 'error': 'No faces registered', 'fix': 'Register face'})
    return issues

def print_system_health(instances, neural_systems=None):
    # Simplified health print for conciseness
    print("\n" + "═"*70)
    print(" JARVIS SINGULARITY - HEALTH REPORT ".center(70, "═"))
    print("═"*70)
    
    for name, obj in instances.items():
        badge = "🟢 [ONLINE]" if obj else "🔴 [OFFLINE]"
        print(f" ├─ {name.ljust(20)} {badge}")

    print("═"*70 + "\n")

# ============================================================================
# CORE APPLICATION
# ============================================================================
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

class JarvisSingularity(QObject):
    transcription_received = pyqtSignal(object)
    hud_update_requested = pyqtSignal(str, str)
    
    def __init__(self, app, instances):
        super().__init__()
        self.app = app
        self.window_manager = instances.get("window_manager")
        self.vision_system = instances.get("vision_system")
        self.audio_system = instances.get("audio_system")
        self.system_integrator = instances.get("system_integrator")
        self.ai_agent = instances.get("ai_agent")
        
        self.last_interaction_time = 0
        self.continuous_mode_window = 15
        self.is_running = False
        self._is_processing = False

        self.shutdown_manager = ShutdownManager(self) if ShutdownManager else None
        
        # Priority Scheduler
        self.scheduler = PriorityScheduler()
        self._scheduler_loop = None
        self._scheduler_thread = None
        self._start_backend_scheduler()

        # Session Manager
        self.session_manager = SessionManager() if SessionManager else None
        
        # Watchdog
        if watchdog_system:
            try:
                watchdog_system.start()
                watchdog_system.register_component("MainUI", heartbeat_interval=3.0)
                watchdog_system.register_component("BackendScheduler", heartbeat_interval=10.0)
                logger.info("✅ Watchdog System ACTIVE")
            except Exception as e:
                logger.error(f"❌ Failed to start Watchdog: {e}")
        
        # Stark Orchestrator (Hardware Lock happens here)
        self.stark_orchestrator = StarkOrchestrator(self) if StarkOrchestrator else None
        if self.stark_orchestrator:
            try:
                self.stark_orchestrator.initialize_stark_system()
            except RuntimeError as e:
                logger.critical(f"🛑 CRITICAL BOOT FAILURE: {e}")
                sys.exit(1)
        
        # Network Mesh
        self.network_mesh = None
        if network_config.get('network_mesh', {}).get('enabled'):
            try:
                from src.core.network_mesh.local_network_intelligence import LocalNetworkIntelligence
                self.network_mesh = LocalNetworkIntelligence(str(PROJECT_ROOT))
                logger.info("🌐 Network Mesh initialized")
            except Exception as e:
                logger.warning(f"⚠️ Network Mesh failed: {e}")
        
        # Self-Learning
        self.self_learning_engine = None
        try:
            from src.core.evolution.self_learning_engine import SelfLearningEngine
            self.self_learning_engine = SelfLearningEngine(PROJECT_ROOT)
            self.self_learning_engine.start_continuous_learning()
            logger.info("🧠 Self-Learning Engine initialized")
        except Exception:
            pass
        
        self.transcription_received.connect(self._on_transcription_safe)
        self.hud_update_requested.connect(self._on_hud_update_safe)
        
        self._setup_signals()
        
        try:
            from src.utils.kill_switch import kill_switch
            kill_switch.start()
        except Exception:
            pass

        logger.info("Singularity Core Engaged.")

    def _setup_signals(self):
        signal.signal(signal.SIGINT, lambda _, __: self.shutdown())
        signal.signal(signal.SIGTERM, lambda _, __: self.shutdown())

    def start(self):
        if self.window_manager:
            from src.interface.window_manager import InterfaceMode
            self.window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)
        
        neuro_sync.run_sync(blocking=False)
        QTimer.singleShot(2000, self._staggered_daemon_start)

    def _staggered_daemon_start(self):
        QTimer.singleShot(5000, self._start_camera_monitoring)
        QTimer.singleShot(10000, self._start_proactive_monitor)
        QTimer.singleShot(15000, self._start_network_mesh)
        QTimer.singleShot(20000, self._start_dynamic_systems)
        QTimer.singleShot(60000, self._start_heavy_models_loading)

    def _start_dynamic_systems(self):
        try:
            from src.core.management.plugin_manager import plugin_manager
            plugin_manager.start()
            from src.utils.file_indexer import file_indexer
            file_indexer.start_background_indexing([str(Path.home() / "Documents")])
        except Exception:
            pass

    def _start_heavy_models_loading(self):
        logger.info("🧠 Starting heavy model warmup...")
        if self.audio_system and hasattr(self.audio_system, 'start_background_loading'):
            try: self.audio_system.start_background_loading()
            except: pass

        def start_vision():
            if self.vision_system and hasattr(self.vision_system, 'start_background_loading'):
                try: self.vision_system.start_background_loading()
                except: pass
        QTimer.singleShot(45000, start_vision)

    def _start_network_mesh(self):
        if self.network_mesh:
            import threading
            def run_mesh():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.network_mesh.start_network_mesh())
                except Exception: pass
            threading.Thread(target=run_mesh, daemon=True).start()

    def _start_backend_scheduler(self):
        def _run_scheduler_loop():
            try:
                self._scheduler_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._scheduler_loop)
                self._scheduler_loop.run_until_complete(self.start_scheduler_async())
                self._scheduler_loop.run_forever()
            except Exception as e:
                logger.error(f"Scheduler crashed: {e}")
        self._scheduler_thread = threading.Thread(target=_run_scheduler_loop, daemon=True)
        self._scheduler_thread.start()

    async def start_scheduler_async(self):
        await self.scheduler.start()
        try:
            from src.evolution import start_evolution_services
            await start_evolution_services()
        except: pass

    def _start_camera_monitoring(self):
        try:
            from src.core.vision.camera_controller import camera_controller
            camera_controller.start_monitoring()
        except Exception: pass

    def _start_proactive_monitor(self):
        try:
            from src.core.intelligence.proactive_monitor import proactive_monitor
            proactive_monitor.start()
        except Exception: pass
        QTimer.singleShot(5000, self._start_audio_listening)

    def _start_audio_listening(self):
        if self.audio_system:
            success = self.audio_system.start_listening()
            if success:
                self.audio_system.on_transcription = self.transcription_received.emit
                QTimer.singleShot(3000, self._greet_user_proactively)

    def _greet_user_proactively(self):
        if not self.ai_agent: return
        try:
            from src.core.audio.voice_controller import get_voice_controller
            vc = get_voice_controller()
            if vc: vc.speak("Sistemas online, William. Estou pronto.")
        except Exception: pass

    @pyqtSlot(object)
    def _on_transcription_safe(self, result):
        if not result or not result.text: return
        from src.core.audio.voice_filter import AtomicVoiceFilter
        has_name = AtomicVoiceFilter.has_wake_word(result.text)
        is_follow_up = (time.time() - self.last_interaction_time) < self.continuous_mode_window
        
        if self._is_processing and has_name:
            try:
                from src.core.audio.voice_controller import get_voice_controller
                vc = get_voice_controller()
                if vc: vc.stop_speaking()
                self._is_processing = False
            except: pass

        if self._is_processing: return
        if not has_name and not is_follow_up: return

        self._is_processing = True
        if self.window_manager:
            hud = self.window_manager.get_hud()
            if hud:
                if hasattr(hud, 'update_state'): hud.update_state("thinking")
                hud.show()

        threading.Thread(target=self._process_and_respond, args=(result.text,), daemon=True).start()

    @pyqtSlot(str, str)
    def _on_hud_update_safe(self, state, text=None):
        if self.window_manager:
            hud = self.window_manager.get_hud()
            if hud:
                if state: hud.update_state(state)
                if text: hud.show_response(text)
                hud.show()

    def _process_and_respond(self, text):
        try:
            # Sync wrapper for async agent
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.ai_agent.process_command(text))
            loop.close()
            
            self.hud_update_requested.emit("speaking", str(response))

            from src.core.audio.voice_controller import get_voice_controller
            vc = get_voice_controller()
            if vc:
                while getattr(vc, '_is_speaking', False): time.sleep(0.5)

            self.hud_update_requested.emit("idle", "")
            self.last_interaction_time = time.time()
        except Exception as e:
            logger.error(f"Error processing: {e}")
            self.hud_update_requested.emit("error", str(e))
        finally:
            self._is_processing = False

    def shutdown(self):
        logger.info("Shutting down...")
        if self.self_learning_engine:
            try: self.self_learning_engine.stop_continuous_learning()
            except: pass
        if self.shutdown_manager:
            self.shutdown_manager.graceful_shutdown()
        elif self.app:
            self.app.quit()

# ============================================================================
# HEADLESS MODE
# ============================================================================
def run_headless_mode(args):
    try:
        logger.info("🚀 Headless Mode Initialization")
        from src.core.actions.system_integrator import get_system_integrator
        from src.core.audio.enhanced_audio import get_audio_system
        from src.core.vision.vision_system import get_vision_system

        data_path = PROJECT_ROOT / "data"
        sys_int = get_system_integrator()
        audio = get_audio_system(data_path)
        vision = get_vision_system(data_path)

        try:
            from src.web.web_server import start_web_server
            start_web_server()
        except: pass

        if audio: audio.start_listening()
        if vision:
            from src.core.vision.camera_controller import camera_controller
            camera_controller.start_monitoring()

        logger.info("✅ Headless systems active")
        while True: time.sleep(1)
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        logger.error(f"Headless failed: {e}")
        return 1

# ============================================================================
# MAIN
# ============================================================================
def main():
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except: pass

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--democratic', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    if args.headless:
        return run_headless_mode(args)

    # Initialize Torch (Optional MKL Pre-warm)
    if TORCH_AVAILABLE and torch is not None and hardware_manager:
        try:
             device = getattr(hardware_manager, 'get_torch_device', lambda: 'cpu')()
             _ = torch.zeros(1).to(device)
        except: pass

    try:
        from PyQt6.QtWidgets import QApplication as QApp
        app = QApp(sys.argv)
        
        # BOOT MANAGER INITIALIZATION
        boot_data = {"instances": None, "status": "initializing"}
        
        async def initialize_with_boot_manager():
            try:
                if not BOOT_MANAGER_AVAILABLE:
                    raise ImportError("Boot Manager unavailable")
                
                boot_manager = BootManager()
                
                event_bus = None
                if EVENT_BUS_AVAILABLE:
                    event_bus = AsyncEventBus()
                    if event_bus:
                        boot_manager.register_module("event_bus", lambda: event_bus, [], BootPriority.HIGH)
                
                from src.interface.window_manager import get_window_manager
                window_manager = get_window_manager(app)
                
                boot_manager.register_module("window_manager", lambda: window_manager, [], BootPriority.HIGH)
                
                boot_manager.register_module(
                    "system_integrator",
                    lambda: __import__('src.core.actions.system_integrator', fromlist=['get_system_integrator']).get_system_integrator(),
                    dependencies=["window_manager"],
                    priority=BootPriority.MEDIUM
                )
                
                boot_manager.register_module(
                    "audio_system",
                    lambda: __import__('src.core.audio.enhanced_audio', fromlist=['get_audio_system']).get_audio_system(PROJECT_ROOT / "data", event_bus=event_bus),
                    dependencies=["system_integrator"],
                    priority=BootPriority.MEDIUM
                )
                
                boot_manager.register_module(
                    "vision_system",
                    lambda: __import__('src.core.vision.vision_system', fromlist=['get_vision_system']).get_vision_system(PROJECT_ROOT / "data", event_bus=event_bus),
                    dependencies=["system_integrator"],
                    priority=BootPriority.MEDIUM
                )
                
                boot_manager.register_module(
                    "ai_agent",
                    lambda: __import__('src.core.intelligence.ai_agent', fromlist=['ai_agent']).ai_agent,
                    dependencies=["audio_system", "vision_system"],
                    priority=BootPriority.MEDIUM
                )
                
                if not boot_manager.start_boot():
                    raise Exception("Boot failed")
                
                boot_data["instances"] = boot_manager.instances
                boot_data["status"] = "completed"
                
            except Exception as e:
                logger.error(f"Boot Manager failed: {e}")
                # Fallback Logic
                try:
                    from src.interface.window_manager import get_window_manager
                    from src.core.actions.system_integrator import get_system_integrator
                    from src.core.audio.enhanced_audio import get_audio_system
                    from src.core.vision.vision_system import get_vision_system
                    from src.core.intelligence.ai_agent import ai_agent

                    wm = get_window_manager(app)
                    si = get_system_integrator()
                    au = get_audio_system(PROJECT_ROOT / "data")
                    vs = get_vision_system(PROJECT_ROOT / "data")

                    boot_data["instances"] = {
                        "window_manager": wm,
                        "system_integrator": si,
                        "audio_system": au,
                        "vision_system": vs,
                        "ai_agent": ai_agent
                    }
                    boot_data["status"] = "completed"
                except Exception as fallback_err:
                    logger.critical(f"Fallback failed: {fallback_err}")
                    boot_data["status"] = "failed"

        # Start Async Boot
        def run_async_boot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(initialize_with_boot_manager())
            loop.close()
        
        threading.Thread(target=run_async_boot, daemon=True).start()

        # Wait for boot
        def check_boot_completion():
            if boot_data["status"] == "completed":
                instances = boot_data["instances"]
                jarvis = JarvisSingularity(app, instances)
                
                if instances.get("window_manager"):
                    instances["window_manager"].jarvis_core = jarvis
                
                jarvis.start()
                boot_checker.stop()
            elif boot_data["status"] == "failed":
                logger.error("Boot failed. Exiting.")
                app.quit()

        boot_checker = QTimer()
        boot_checker.timeout.connect(check_boot_completion)
        boot_checker.start(200)

        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
