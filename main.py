import os
import sys
import warnings
import time
import platform

# 🛡️ EARLY ENVIRONMENT CONFIGURATION (Critical for Windows/UTF-8)
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Force UTF-8 encoding for file operations
import locale
try:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        pass  # Use system default if UTF-8 not available

# 🛡️ EARLY WARNING SUPPRESSION (Must be before any heavy imports)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*openvino.runtime.*')
warnings.filterwarnings('ignore', message='.*loss_type=None.*')

import logging

# 🛡️ GLOBAL MONKEY PATCH: Correção Crítica para OpenVINO/Optimum-Intel
# Previne erro 'module openvino has no attribute Node' e 'No module named openvino.op'
try:
    import sys
    import openvino
    # Favorece o novo padrão sem .runtime (OpenVINO 2023.1+)
    node_obj = getattr(openvino, 'Node', None)
    
    # Fallback silencioso via sys.modules se já estiver carregado por outra lib
    if not node_obj and 'openvino.runtime' in sys.modules:
        node_obj = getattr(sys.modules['openvino.runtime'], 'Node', None)
        
    if node_obj:
        if not hasattr(openvino, 'Node'): openvino.Node = node_obj
        
    # Patch op module
    op_obj = getattr(openvino, 'op', None)
    if not op_obj and 'openvino.runtime' in sys.modules:
        op_obj = getattr(sys.modules['openvino.runtime'], 'op', None)
        
    if op_obj:
        sys.modules['openvino.op'] = op_obj
        if not hasattr(openvino, 'op'): openvino.op = op_obj
except Exception:
    pass
import psutil
import signal
import shutil
import warnings
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
from datetime import datetime

# Try to import ShutdownManager (may fail due to heavy dependencies)
try:
    from src.core.management.shutdown_manager import ShutdownManager # New Shutdown Manager
    SHUTDOWN_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: ShutdownManager not available: {e}")
    ShutdownManager = None
    SHUTDOWN_MANAGER_AVAILABLE = False

# Lazy import of hardware manager to avoid torch loading at startup
try:
    from src.core.management.hardware_manager import get_hardware_manager
    hardware_manager = get_hardware_manager()
    HARDWARE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: HardwareManager not available: {e}")
    hardware_manager = None
    HARDWARE_MANAGER_AVAILABLE = False

# Lazy import of StarkOrchestrator to avoid heavy dependencies
try:
    from src.core.management.orchestrator import StarkOrchestrator
    STARK_ORCHESTRATOR_AVAILABLE = True
except (ImportError, AttributeError) as e:
    logger.warning(f"⚠️ StarkOrchestrator not available via management: {e}")
    try:
        from src.core import StarkOrchestrator
        STARK_ORCHESTRATOR_AVAILABLE = True
    except:
        StarkOrchestrator = None
        STARK_ORCHESTRATOR_AVAILABLE = False

from src.web.web_server import start_server
from src.utils.web_emitter import emit_telemetry_sync, emit_log_sync

# ============================================================================
# [STAGE 1] ENVIRONMENT CONFIGURATION & COMPATIBILITY
# ============================================================================
# Core overrides for Windows/Torch stability
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"
# Suppress ChromaDB Telemetry Bug (posthog 7.x incompatible with chromadb 0.4.x)
# Disable telemetry entirely via env var + silence logger
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["POSTHOG_DISABLED"] = "1"
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
# Centralized comtypes Fix (Windows 11 stability)
if platform.system() == "Windows":
    try:
        import comtypes.client
        import comtypes.client._code_cache
        # Disable cache globally to avoid Access Violation in parallel boot
        comtypes.client._code_cache._enable_cache = False
        gen_dir = Path(comtypes.client._code_cache._get_gen_dir())
        if gen_dir.exists():
            shutil.rmtree(gen_dir, ignore_errors=True)
        os.makedirs(gen_dir, exist_ok=True)
    except Exception: pass

# Path Synchronization
PROJECT_ROOT = Path(__file__).parent.absolute()
VENV_SITE = PROJECT_ROOT / "venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
    if str(VENV_SITE) in sys.path: sys.path.remove(str(VENV_SITE))
    sys.path.insert(0, str(VENV_SITE))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(1, str(PROJECT_ROOT / "src"))

# Suppress Warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*loss_type=None.*')

# Ensure necessary data structure
Path('data/logs').mkdir(parents=True, exist_ok=True)

# Centralized Logging
log_dir = Path(os.environ.get("JARVIS_SESSION_LOG_DIR", "data/logs"))
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "jarvis_singularity.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
# Global reference for shutdown signaling
QApplication = None

# Unified InterfaceMode Import
try:
    from src.interface.window_manager import InterfaceMode
except ImportError:
    # Fallback if source root is not in path yet
    from enum import Enum
    class InterfaceMode(Enum):
        HUD_OVERLAY = "hud"
        DASHBOARD = "dashboard"
        HIDDEN = "hidden"

logger = logging.getLogger("JARVIS-CORE")

# Try to import torch and determine availability (lazy import)
TORCH_AVAILABLE = False
def _check_torch():
    global TORCH_AVAILABLE
    if not TORCH_AVAILABLE:
        try:
            import torch
            TORCH_AVAILABLE = True
            return True
        except Exception:
            TORCH_AVAILABLE = False
            return False
    return True

# ============================================================================
# VISUAL & DIAGNOSTIC UTILITIES
# ============================================================================

def print_progress(label, current, total, width=40):
    """ASCII Progress Bar for premium startup feel"""
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    sys.stdout.write(f"\r {label.ljust(25)}: [{bar}] {percent*100:.0f}%")
    sys.stdout.flush()

def auto_diagnose():
    """Diagnostic suite to detect and suggest fixes for common issues"""
    issues = []
    # 1. Check PyTorch Stability (c10.dll/MKL)
    try:
        if _check_torch():
            import torch
            _ = torch.zeros(1)
    except Exception as e:
        issues.append({
            'level': 'CRITICAL',
            'component': 'Neural Engine (Torch)',
            'error': str(e),
            'fix': 'Run START_JARVIS.bat --repair-pytorch'
        })
    
    # 2. Check Vision Engines
    try:
        import easyocr
        import openvino
    except Exception as e:
        issues.append({
            'level': 'CRITICAL',
            'component': 'AI Vision/Hardware Acceleration',
            'error': f'Missing neural backends: {e}',
            'fix': 'Run START_JARVIS.bat to initiate Auto-Repair.'
        })

    # 3. Check faces registry (Operational warning)
    if not any(Path('data/faces').glob("*.j*")):
        issues.append({
            'level': 'INFO',
            'component': 'Visual FaceID',
            'error': 'Nenhuma biometria facial detectada',
            'fix': 'Diga: "Jarvis, cadastrar meu rosto" para iniciar o mapeamento.'
        })
    return issues

def print_system_health(instances, neural_systems=None):
    """Prints a detailed system health report using visual badges"""
    ram = psutil.virtual_memory()
    print("\n" + "═"*70)
    print(" JARVIS SINGULARITY - ULTIMATE HEALTH REPORT ".center(70, "═"))
    print("═"*70)
    print(f" HOST OS:      {platform.system()} {platform.release()} (v{platform.version()})")
    print(f" RAM USAGE:    {ram.available/1e9:.1f}GB Free / {ram.total/1e9:.1f}GB Total")
    if TORCH_AVAILABLE and torch.cuda.is_available():
        print(f" GPU ADAPTER:  {torch.cuda.get_device_name(0)}")
    
    print("\n [INFRASTRUCTURE STATUS]")
    for name, obj in instances.items():
        badge = "🟢 [OPERATIONAL]" if obj else "🔴 [OFFLINE]"
        print(f" ├─ {name.ljust(18)} {badge}")
    
    print("\n [ML CAPABILITIES]")
    vs = instances.get("Vision System")
    # ML Feature Logic with better distinction
    face_rec_installed = getattr(vs, 'FACE_REC_AVAILABLE', False) if vs else False
    if not face_rec_installed:
        # Check globally if not in vs
        try:
            import face_recognition
            face_rec_installed = True
        except: pass

    # Contar faces: tentar camera_controller primeiro (tem sync pós-boot), fallback para vs
    num_faces = len(getattr(vs, 'known_face_encodings', [])) if vs else 0
    if num_faces == 0:
        try:
            from src.core.vision.camera_controller import camera_controller as cam_ctrl
            if cam_ctrl:
                num_faces = len(getattr(cam_ctrl, 'known_face_encodings', []))
        except Exception:
            pass
    
    face_icon = "✅" if (face_rec_installed and num_faces > 0) else ("🔶" if face_rec_installed else "❌")
    face_label = f"Face Recognition ({num_faces} faces)" if face_rec_installed else "Face Recognition"

    # 🔒 Vision System em Passive Mode = modelos carregam no Stage 3 (pós health report)
    # Se vs existe mas _ocr_ready=False, significa que AINDA VAI carregar, não que falhou
    vs_passive = vs and not getattr(vs, '_ocr_ready', False) and not getattr(vs, '_yolo_ready', False)
    
    ocr_status = getattr(vs, '_ocr_ready', False) if vs else False
    yolo_status = getattr(vs, '_yolo_ready', False) if vs else False
    
    ml_feats = [
        ("OCR (EasyOCR)", ocr_status, vs_passive and not ocr_status),
        ("YOLO (Detection)", yolo_status, vs_passive and not yolo_status),
        (face_label, face_rec_installed, False),
        ("Hw Acceleration", hardware_manager.device != "cpu" or (hasattr(hardware_manager, 'accelerator') and hardware_manager.accelerator is not None), False),
        ("PyTorch Neural", TORCH_AVAILABLE, False)
    ]
    
    for name, status, pending in ml_feats:
        if "Face" in name:
            icon = face_icon
        elif pending:
            icon = "🛠️"  # Background loading starting shortly
        else:
            icon = "✅" if status else "❌"
        suffix = " [LOADING IN BG]" if pending else ""
        print(f" ├─ {icon} {name}{suffix}")
    
    # Neural Systems (Advanced)
    if neural_systems:
        print("\n [NEURAL SYSTEMS]")
        for name, status in neural_systems.get_status_report().items():
            if status.loaded:
                icon = "✅"
            elif status.requires_api_key and not status.api_key_valid:
                icon = "🔑"
            else:
                icon = "❌"
            print(f" ├─ {icon} {name}")

    # Calculations for Score
    working = sum(1 for v in instances.values() if v) + sum(1 for _, s, _ in ml_feats if s)
    total_slots = len(instances) + len(ml_feats)
    
    # Add neural systems to score
    if neural_systems:
        neural_active = len([s for s in neural_systems.get_status_report().values() if s.loaded])
        neural_total = len(neural_systems.get_status_report())
        working += neural_active
        total_slots += neural_total
    
    score = (working / total_slots * 10) if total_slots > 0 else 0
    print("\n" + f"═ SYSTEM HEALTH SCORE: {score:.1f}/10 ═".center(70, "═"))
    
    issues = auto_diagnose()
    if issues:
        print("\n [🔧 EMERGENCY PROTOCOLS]")
        for issue in issues:
            print(f" {issue['level']}: {issue['component']} -> {issue['fix']}")
    print("═"*70 + "\n")

# ============================================================================
# JARVIS SINGULARITY CORE
# ============================================================================
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

class JarvisSingularity(QObject):
    # Signal to bridge background audio thread to main UI thread
    transcription_received = pyqtSignal(object)
    # Signal for thread-safe HUD updates (state, optional text)
    hud_update_requested = pyqtSignal(str, str)
    
    def __init__(self, app, instances):
        super().__init__()
        self.app = app
        self.window_manager = instances.get("Window Manager")
        self.vision_system = instances.get("Vision System")
        self.audio_system = instances.get("Audio System")
        self.system_integrator = instances.get("System Integrator")
        self.ai_agent = instances.get("AI Agent")
        
        # 🧠 Contextual Awareness State
        self.last_interaction_time = 0
        self.continuous_mode_window = 15 # Seconds to stay 'awake' for follow-ups
        
        self.is_running = False
        # Initialize Shutdown Manager
        self.shutdown_manager = ShutdownManager(self)
        
        # Initialize Stark Orchestrator (Phase 4)
        self.stark_orchestrator = StarkOrchestrator(self)
        self.stark_orchestrator.initialize_stark_system()
        
        # Response lock to avoid overlapping
        self._is_processing = False
        
        # Connect internal signals to thread-safe slots
        self.transcription_received.connect(self._on_transcription_safe)
        self.hud_update_requested.connect(self._on_hud_update_safe)
        
        self._setup_signals()
        
        # 🛡️ FASE 4: Ativar Kill Switch (Singularity Edition)
        try:
            from src.utils.kill_switch import kill_switch
            kill_switch.start()
        except Exception as e:
            logger.warning(f"⚠️ Kill Switch não disponível: {e}")
        
        logger.info("Singularity Core Engaged.")

    def _setup_signals(self):
        signal.signal(signal.SIGINT, lambda s, f: self.shutdown())
        signal.signal(signal.SIGTERM, lambda s, f: self.shutdown())

    def start(self):
        """Start JARVIS with staggered daemon initialization for maximum stability"""
        # Show HUD interface
        if self.window_manager:
            from src.interface.window_manager import InterfaceMode
            self.window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)
            logger.info("✅ HUD interface activated")
            hud = self.window_manager.get_hud()
            if hud:
                try:
                    if hasattr(hud, 'log_event'):
                        hud.log_event("SINGULARITY CORE ENGAGED")
                except Exception as e:
                    logger.warning(f"HUD Log Error (Non-Fatal): {e}")
        
        # Staggered initialization: Warmup for subsystems
        QTimer.singleShot(5000, self._staggered_daemon_start)
        
        # 📊 TELEMETRY SYNC (Quantum Core)
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self._sync_hud_telemetry)
        self.telemetry_timer.start(2000) # Every 2s

    def _staggered_daemon_start(self):
        """Sequentially start background subsystems with delays to avoid DLL/COM collisions"""
        # [STEP 1] Wait 5s then start Camera (Eyes)
        # We start camera first to capture the user's initial emotion for the greeting
        QTimer.singleShot(5000, self._start_camera_monitoring)
        
        # [STEP 2] Wait another 5s then start Proactive Monitor (Screen)
        QTimer.singleShot(10000, self._start_proactive_monitor)

    def _start_camera_monitoring(self):
        """Initializes FaceID and Emotion detection via CameraController"""
        try:
            from src.core.vision.camera_controller import camera_controller
            camera_controller.start_monitoring()
            logger.info("👁️ Camera Monitoring (Eyes) active")
            if self.window_manager and self.window_manager.get_hud():
                self.window_manager.get_hud().log_event("OPTIC SENSORS: ONLINE")
        except Exception as e:
            logger.warning(f"⚠️ Camera Monitor failure: {e}")

    def _start_proactive_monitor(self):
        try:
            from src.core.intelligence.proactive_monitor import proactive_monitor
            proactive_monitor.start()
            logger.info("⚡ Proactive Monitor active")
            if self.window_manager and self.window_manager.get_hud():
                self.window_manager.get_hud().log_event("SIXTH SENSE ACTIVE")
        except Exception as e:
            logger.warning(f"⚠️ Proactive Monitor failure: {e}")

        # 3. Wait another 5s then start Microphone
        QTimer.singleShot(5000, self._start_audio_listening)

    def _start_audio_listening(self):
        if self.audio_system:
            logger.info("🎤 Starting audio engine...")
            success = self.audio_system.start_listening()
            if success:
                logger.info("✅ JARVIS is listening!")
                if self.window_manager and self.window_manager.get_hud():
                    self.window_manager.get_hud().log_event("AUDIO ENGINE: LISTENING")
                
                self.audio_system.on_transcription = self.transcription_received.emit
                
                if self.window_manager and hasattr(self.window_manager, '_tray_icon') and self.window_manager._tray_icon:
                    self.window_manager._tray_icon.setToolTip("🎤 JARVIS - Listening")
                
                # 🌟 NOVO: Agendar saudação proativa após o áudio estar pronto
                # Isso garante que ele te cumprimente sabendo que pode te ouvir
                QTimer.singleShot(3000, self._greet_user_proactively)
            else:
                logger.error("❌ Failed to start microphone")
        
    def _greet_user_proactively(self):
        """
        🌟 Executa saudação proativa após boot completo.
        Chama o AI Agent para gerar frase humana e contextual.
        """
        try:
            logger.info("⚡ Iniciando saudação proativa...")
            
            # 1. Verificar disponibilidade do AI Agent
            if not self.ai_agent or getattr(self.ai_agent, 'safe_mode', False):
                logger.warning("⚠️ AI Agent offline ou em safe mode - usando saudação básica")
                from src.core.audio.voice_controller import voice_controller
                voice_controller.speak("Sistemas online, William. Estou pronto.")
                return
            
            # 2. Coletar status de saúde do sistema
            system_health = {
                "AI Agent": bool(self.ai_agent),
                "Vision System": bool(self.vision_system),
                "Audio System": bool(self.audio_system),
                "Window Manager": bool(self.window_manager),
                "System Integrator": bool(self.system_integrator)
            }
            
            # 3. Chamar método de saudação do AI Agent (em thread para não bloquear)
            import threading
            def greeting_worker():
                try:
                    self.ai_agent.greet_user_on_startup(system_health=system_health)
                except Exception as e:
                    logger.error(f"❌ Erro na thread de saudação: {e}")
            
            greeting_thread = threading.Thread(target=greeting_worker, daemon=True, name="StartupGreeting")
            greeting_thread.start()
            
        except Exception as e:
            logger.error(f"❌ Falha ao executar saudação proativa: {e}")
    
    def _sync_hud_telemetry(self):
        """Sync core stats with HUD telemetry (Quantum Core)"""
        if not self.window_manager: return
        
        hud = self.window_manager.get_hud()
        if not hud: return
        
        try:
            # 1. Fetch Emotion
            try:
                from src.core.vision.camera_controller import camera_controller
                emotion = getattr(camera_controller, 'current_emotion', 'neutral') if camera_controller else "neutral"
            except (ImportError, AttributeError):
                emotion = "neutral"
            
            # 2. System Pulse (CPU Pulse)
            cpu_usage = psutil.cpu_percent()
            pulse = "STABLE"
            if cpu_usage > 70: pulse = "ADAPTIVE"
            if cpu_usage > 90: pulse = "CRITICAL"
            
            # 3. Neural Sync (Randomized realism)
            import random
            sync_val = 98.0 + random.uniform(0.1, 1.5)
            
            # Update HUD
            hud.update_telemetry({
                "sync": f"{sync_val:.1f}%",
                "emotion": emotion,
                "pulse": pulse,
                "cpu": cpu_usage
            })
        except Exception as e:
            logger.debug(f"Telemetry sync error: {e}")

    @pyqtSlot(object)
    def _on_transcription_safe(self, result):
        """Processes transcription result safely on the Main Thread"""
        if not result or not result.text or len(result.text.strip()) < 2:
            return
            
        if self._is_processing:
            logger.warning("Already processing a command, skipping...")
        # 🧠 [STARK NATURAL CONVERSATION LOGIC]
        # Check if we should process this:
        # 1. Has any wake word (Jarvis, James, etc) anywhere?
        # 2. Are we in a follow-up window (last 15s)?
        from src.core.audio.voice_filter import AtomicVoiceFilter
        has_name = AtomicVoiceFilter.has_wake_word(result.text)
        is_follow_up = (time.time() - self.last_interaction_time) < self.continuous_mode_window
        
        if not has_name and not is_follow_up:
            # Let's be smart: if it's very short silence or background, ignore
            # but log for diagnostics
            logger.debug(f"🔇 Ignored (No wake word & no context): '{result.text}'")
            return

        logger.info(f"🎙️ [UI THREAD] {'CONTINUAÇÃO' if is_follow_up and not has_name else 'COMANDO'} recebido: '{result.text}'")
        self._is_processing = True
        
        # Update HUD state (Now safe because we are on main thread)
        if self.window_manager:
            hud = self.window_manager.get_hud()
            if hud:
                if hasattr(hud, 'update_state'):
                    hud.update_state("thinking")
                if hasattr(hud, 'show_response'):
                    hud.show_response(f"Processando: {result.text}")
                hud.show() # Force visibility

        # Process via Agent in Background Thread
        try:
            if self.ai_agent:
                import threading
                threading.Thread(target=self._process_and_respond, args=(result.text,), daemon=True).start()
            
            # 🆕 STARK 2.0: EMERGENCY FALLBACK DIRECT LINK
            elif hasattr(self, 'stark_orchestrator') and hasattr(self.stark_orchestrator, 'fallback_system'):
                logger.warning("⚠️ AI Agent offline - Engaging Emergency Fallback System")
                
                # Show fallback status on HUD
                if self.window_manager:
                    hud = self.window_manager.get_hud()
                    if hud:
                        hud.update_state("error") # Orange/Red state
                        hud.show_response("⚠️ Modo de Emergência Ativo")
                
                # Run fallback in thread
                import threading
                threading.Thread(target=self._process_fallback, args=(result.text,), daemon=True).start()
                
            else:
                logger.error("AI Agent not loaded and Fallback unavailable")
                self._is_processing = False
                if self.window_manager:
                    hud = self.window_manager.get_hud()
                    if hud:
                        hud.update_state("error")
                        hud.show_response("Erro Crítico: Agente de IA offline.")
        except Exception as e:
            logger.error(f"Error starting agent thread: {e}")
            self._is_processing = False

    @pyqtSlot(str, str)
    def _on_hud_update_safe(self, state, text=None):
        """Processes HUD updates safely on the Main Thread"""
        if self.window_manager:
            hud = self.window_manager.get_hud()
            if hud:
                if state: hud.update_state(state)
                if text: hud.show_response(text)
                hud.show()

    def _process_and_respond(self, text):
        """Agent processing loop (Background Thread)"""
        try:
            # 1. Process Command
            response = self.ai_agent.process_command(text)
            
            # 2. Update HUD with final response (Emit signal)
            self.hud_update_requested.emit("speaking", response)
                    
            # 3. Wait for voice to finish
            from src.core.audio.voice_controller import voice_controller
            while voice_controller._is_speaking:
                time.sleep(0.5)
                
            # 4. Return to idle (Emit signal)
            self.hud_update_requested.emit("idle", "")
                    
        except Exception as e:
            logger.error(f"Error in process_and_respond: {e}")
            self.hud_update_requested.emit("error", f"Erro: {e}")
        finally:
            self._is_processing = False
            self.last_interaction_time = time.time() # Start follow-up timer AFTER finishing speech

    def _process_fallback(self, text):
        """Emergency Fallback Loop (No AI Agent)"""
        try:
            fb = self.stark_orchestrator.fallback_system
            result = fb.process_command(text)
            
            response_text = result.get("response", "Comando não reconhecido no modo de emergência.")
            
            # Emit speech output signal (using same slot as normal)
            self.hud_update_requested.emit("speaking", response_text)
            
            # Speak via voice controller (direct call if available)
            # Note: Voice Controller might be functional even if Agent failed
            from src.core.audio.voice_controller import voice_controller
            voice_controller.speak(response_text)
            
        except Exception as e:
            logger.error(f"Fallback processing error: {e}")
            self.hud_update_requested.emit("error", "Falha no sistema de emergência.")
        finally:
            self._is_processing = False

    def shutdown(self):
        """Finalizes all systems and exits gracefully via ShutdownManager"""
        if hasattr(self, 'shutdown_manager'):
            self.shutdown_manager.graceful_shutdown()
        else:
            # Fallback if manager not initialized
            logger.warning("⚠️ ShutdownManager not found, using legacy shutdown")
            QApplication.quit()

# ============================================================================
# BOOT ENGINES
# ============================================================================

# Removed load_module_async


# Removed parallel_boot


# ============================================================================
# MAIN ENTRY POINT - STAGED BOOT PROTOCOL
# ============================================================================
def main():
    # Fix console encoding for Windows (emojis support)
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass  # Python < 3.7 or non-standard console
    
    # ========================================================================
    # 🔥 NOVO: VERIFICAÇÃO DE MODO DEMOCRÁTICO
    # ========================================================================
    democratic_mode = "--democratic" in sys.argv
    
    if democratic_mode:
        print(f"\n🔥 [DEMOCRÁTICO] Inicializando JARVIS em Modo Democrático Total...")
        print("="*80)
        print("🔥 PODER TOTAL HABILITADO - SEM PRÉ-CONFIGURAÇÕES")
        print("👑 Interface de Controle Democrático Ativa")
        print("🆔 Identificação Microsoft + Biometric")
        print("☁️ Google Drive Estruturado")
        print("🌐 Rede Inteligente Democrática")
        print("="*80)
    else:
        print(f"\n🌌 [SINGULARITY] Inicializando JARVIS Singularity Suite...")
            
    # CRITICAL FIX: Ensure ui_signals is available in local scope
    from src.interface.ui_signals import ui_signals
    
    start_time = time.time()
    
    # ========================================================================
    # 🔥 NOVO: INICIALIZAÇÃO DEMOCRÁTICA PRÉ-GUI
    # ========================================================================
    democratic_systems = None
    if democratic_mode:
        try:
            print("🔥 [DEMOCRÁTICO] Inicializando sistemas de poder...")
            
            # Importar e inicializar sistemas democráticos
            from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier
            from src.core.identity.enhanced_biometric_verifier import EnhancedBiometricVerifier
            from src.core.cloud.structured_google_drive import StructuredGoogleDriveManager
            from src.core.interface.democratic_control_interface import DemocraticControlInterface
            from src.core.democratic.democratic_core import DemocraticCore
            
            # Configurar paths
            PROJECT_ROOT = Path(__file__).parent
            data_path = PROJECT_ROOT / "data"
            
            # Classe temporária para jarvis_core
            class TempJarvisCore:
                def __init__(self):
                    self.config = {
                        'system': {
                            'base_path': str(PROJECT_ROOT),
                            'data_path': str(data_path)
                        }
                    }
            
            temp_core = TempJarvisCore()
            
            # Inicializar sistemas democráticos
            print("   🆔 Carregando identificação Microsoft...")
            microsoft_identifier = MicrosoftDeviceIdentifier(str(data_path))
            microsoft_identifier.initialize()
            
            print("   🔐 Preparando verificação biométrica...")
            biometric_verifier = EnhancedBiometricVerifier(temp_core, microsoft_identifier)
            
            print("   ☁️ Configurando Google Drive...")
            drive_manager = StructuredGoogleDriveManager(temp_core, microsoft_identifier)
            drive_manager.initialize()
            
            print("   🗳️ Inicializando núcleo democrático...")
            democratic_core = DemocraticCore(temp_core)
            
            print("   🔥 Preparando interface de controle...")
            democratic_interface = DemocraticControlInterface(temp_core)
            
            # Armazenar sistemas para usar depois
            democratic_systems = {
                'core': temp_core,
                'microsoft_identifier': microsoft_identifier,
                'biometric_verifier': biometric_verifier,
                'drive_manager': drive_manager,
                'democratic_core': democratic_core,
                'democratic_interface': democratic_interface
            }
            
            print("✅ [DEMOCRÁTICO] Sistemas de poder inicializados com sucesso!")
            
        except Exception as e:
            print(f"❌ [DEMOCRÁTICO] Erro inicializando sistemas: {e}")
            democratic_mode = False  # Fallback para modo normal
    
    # ------------------------------------------------------------------------
    # [STAGE 1] CORE INITIALIZATION (Pre-GUI)
    # ------------------------------------------------------------------------
    # CRITICAL: Initialize Torch/MKL BEFORE QApp to prevent 0xC0000005.
    # This ensures the Neural Engine's threading model (OpenMP/MKL) captures
    # the process context before the GUI Event Loop (PyQt6) can conflict with it.
    if TORCH_AVAILABLE:
        try:
             # Force MKL initialization (Pre-warm)
             _ = torch.zeros(1).to(hardware_manager.get_torch_device())
             logger.info("🧠 [STAGE 1] Neural Engine: Pre-warmed (MKL Initialized)")
        except Exception as e:
            logger.warning(f"⚠️ Neural Engine Pre-warm failed: {e}")

    try:
        from PyQt6.QtWidgets import QApplication as QApp
        from PyQt6.QtCore import QTimer
        import threading
        
        global QApplication
        app = QApp(sys.argv)
        app.setStyle("Fusion")
        
        # --------------------------------------------------------------------
        # [STAGE 2] INTERFACE & BODY (Visuals)
        # --------------------------------------------------------------------
        
        # Shared container for instances
        boot_data = {"instances": None}
        
        # 1. Initialize UI synchronously
        from src.interface.window_manager import get_window_manager, InterfaceMode
        window_manager = get_window_manager(app)
        
        # Show HUD immediately
        window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)
        hud = window_manager.get_hud()
        if hud and hasattr(hud, 'update_state'): 
            hud.update_state("booting")
        if hud and hasattr(hud, 'show_response'):
             hud.show_response("INICIANDO PROTOCOLO SINGULARITY...")
        
        # 2. Define Background Boot Task
        def background_boot_task():
             try:
                # Load heavy systems
                from src.core.actions.system_integrator import get_system_integrator
                from src.core.audio.enhanced_audio import get_audio_system
                from src.core.vision.vision_system import get_vision_system
                from src.core.intelligence.ai_agent import ai_agent
                
                # Update status via signal (need ui_signals reference, implicitly available?)
                # ui_signals is local in main, need to pass it or re-import
                from src.interface.ui_signals import ui_signals
                ui_signals.update_status.emit("Carregando Core Systems...")
                
                sys_int = get_system_integrator()
                audio = get_audio_system(PROJECT_ROOT / "data")
                vision = get_vision_system(PROJECT_ROOT / "data")
                
                # 🚀 INICIAR CARREGAMENTO NEURAL EM BACKGROUND
                # Isso impede que o sistema fique "surdo" ou "cego"
                audio.start_background_loading()
                vision.start_background_loading()
                
                boot_data["instances"] = {
                    "Window Manager": window_manager,
                    "System Integrator": sys_int,
                    "Audio System": audio,
                    "Vision System": vision,
                    "AI Agent": ai_agent,
                    "Neural Systems": None 
                }
                
                ui_signals.update_status.emit("SUBSISTEMAS ALINHADOS")
                
             except Exception as e:
                 logger.error(f"❌ Background Boot Failed: {e}")
                 import traceback
                 traceback.print_exc()

        # 3. Start Background Thread (Scheduled after event loop starts)
        boot_thread = threading.Thread(target=background_boot_task, daemon=True, name="BackgroundBoot")
        QTimer.singleShot(100, boot_thread.start)
        
        # 4. Timer to check for completion and start Stage 3
        def check_boot_completion():
            if boot_data["instances"]:
                logger.info("⚡ [STAGE 2] Background Boot Completed")
                instances = boot_data["instances"]
                
                # ========================================================================
                # 🔥 NOVO: INTEGRAÇÃO DOS SISTEMAS DEMOCRÁTICOS
                # ========================================================================
                if democratic_mode and democratic_systems:
                    try:
                        print("🔥 [DEMOCRÁTICO] Integrando sistemas de poder ao núcleo...")
                        
                        # Adicionar sistemas democráticos às instâncias
                        instances["Democratic Core"] = democratic_systems['democratic_core']
                        instances["Microsoft Identifier"] = democratic_systems['microsoft_identifier']
                        instances["Biometric Verifier"] = democratic_systems['biometric_verifier']
                        instances["Drive Manager"] = democratic_systems['drive_manager']
                        instances["Democratic Interface"] = democratic_systems['democratic_interface']
                        
                        # Lançar interface democrática em thread separada
                        def launch_democratic_interface():
                            try:
                                print("🚀 [DEMOCRÁTICO] Lançando Interface de Controle Total...")
                                democratic_systems['democratic_interface'].launch_interface()
                            except Exception as e:
                                print(f"❌ [DEMOCRÁTICO] Erro na interface: {e}")
                        
                        democratic_thread = threading.Thread(
                            target=launch_democratic_interface, 
                            daemon=True, 
                            name="DemocraticInterface"
                        )
                        democratic_thread.start()
                        
                        print("✅ [DEMOCRÁTICO] Interface de Poder Total Ativa!")
                        
                    except Exception as e:
                        print(f"❌ [DEMOCRÁTICO] Erro integrando sistemas: {e}")
                
                # Start Stage 3 (Neural Awakening)
                logger.info("⚡ [STAGE 3] Igniting Neural Engines...")
                jarvis = JarvisSingularity(app, instances)
                
                # Initialize Core
                jarvis.start()
                
                # Stop checking
                boot_checker.stop()
                
        boot_checker = QTimer()
        boot_checker.timeout.connect(check_boot_completion)
        boot_checker.start(200) # Check every 200ms

        # Execute App
        sys.exit(app.exec())

        


    except KeyboardInterrupt:
        return 130
    except Exception as e:
        # Captura qualquer falha catastrófica no boot
        if 'logger' in globals():
            logger.error(f"❌ [FATAL] Erro crítico durante a inicialização: {e}")
        else:
            print(f"❌ [FATAL] Erro crítico (logger offline): {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Garante a limpeza de recursos se o sistema fechar
        # Note: instances and other vars are local to main, so we check local scope if possible
        # or just rely on OS cleanup since we are exiting.
        # But per user request, we add the logging.
        if 'logger' in globals():
             logger.info("🧹 Encerrando instâncias e limpando memória...")

if __name__ == "__main__":
    sys.exit(main())
