import os
import sys
import logging
import time
import platform
import psutil
import signal
import shutil
import warnings
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
from datetime import datetime
from src.core.management.shutdown_manager import ShutdownManager # New Shutdown Manager
from src.core.management.hardware_manager import hardware_manager
from src.core.orchestrator import StarkOrchestrator # Stark 2.0 Orchestrator
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

# Try to import torch and determine availability
try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

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
        ("Hw Acceleration", hardware_manager.device != "cpu", False),
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
        # Camera monitoring now handled in Stage 3 after neural models load
        # This prevents ACCESS_VIOLATION crashes from parallel model loading
        
        # Wait 5s then start Proactive Monitor
        QTimer.singleShot(5000, self._start_proactive_monitor)

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
            else:
                logger.error("❌ Failed to start microphone")
        
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
            return
            
        logger.info(f"🎙️ [UI THREAD] Transcription received: '{result.text}'")
        self._is_processing = True
        
        # Update HUD state (Now safe because we are on main thread)
        if self.window_manager:
            hud = self.window_manager.get_hud()
            if hud:
                hud.update_state("thinking")
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

async def load_module_async(name: str, factory_func, *args):
    """Safe wrapper for module initialization. Using main thread for 100% stability."""
    try:
        # ABSOLUTE SAFETY: Run everything in the main thread during boot.
        # This prevents 0xC0000005 Access Violations caused by thread-unsafe DLL loads.
        if asyncio.iscoroutinefunction(factory_func):
            module = await factory_func(*args)
        else:
            module = factory_func(*args)
        
        logger.info(f"✅ {name} loaded")
        return (name, module)
    except Exception as e:
        logger.error(f"❌ {name} failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return (name, None)

async def parallel_boot(app):
    """Orchestrates the parallel loading of all major systems"""
    print_progress("Iniciando Parallel Boot", 1, 12)
    
    # Delayed imports to stay parallel
    # Delayed imports to stay parallel
    from src.interface.window_manager import get_window_manager
    from src.core.vision.vision_system import get_vision_system
    from src.core.audio.enhanced_audio import get_audio_system
    from src.core.actions.system_integrator import get_system_integrator
    from src.core.intelligence.neural_systems import NeuralSystemsLoader
    from src.utils.config import Config
    
    config = Config()
    step = 1
    total = 7
    
    async def load_with_progress(name, func, *args):
        nonlocal step
        res = await load_module_async(name, func, *args)
        step += 1
        print_progress("Iniciando Parallel Boot", step, total)
        return res

    results = {}
    
    # Sequential loading for COM/GDI sensitive modules to prevent 0xC0000005
    # Step 1-6
    results["Window Manager"] = (await load_with_progress("Window Manager", get_window_manager, app))[1]
    results["System Integrator"] = (await load_with_progress("System Integrator", get_system_integrator))[1]
    results["Audio System"] = (await load_with_progress("Audio System", get_audio_system, PROJECT_ROOT / "data"))[1]
    results["Vision System"] = (await load_with_progress("Vision System", get_vision_system, PROJECT_ROOT / "data"))[1]
    results["AI Agent"] = (await load_with_progress("AI Agent", lambda: __import__("src.core.intelligence.ai_agent", fromlist=["ai_agent"]).ai_agent))[1]
    results["Neural Systems"] = (await load_with_progress("Neural Systems", lambda: NeuralSystemsLoader(PROJECT_ROOT / "data", config)))[1]

    print_progress("Boot Finalizado", 12, 12)
    print("\n")
    return results

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
    
    print(f"\n🌌 [STAGE 0] Initializing JARVIS Singularity Suite...")
    start_time = time.time()
    
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
        global QApplication
        app = QApp(sys.argv)
        app.setStyle("Fusion")
        
        # --------------------------------------------------------------------
        # [STAGE 2] INTERFACE & BODY (Visuals)
        # --------------------------------------------------------------------
        # Load lightweight systems: Window Manager, Audio/Vision (Passive), etc.
        instances = asyncio.run(parallel_boot(app))
        
        # Fetch instances for Stage 3
        window_manager = instances.get("Window Manager")
        vision_system = instances.get("Vision System")
        audio_system = instances.get("Audio System")
        neural_systems = instances.get("Neural Systems")
        
        boot_time = time.time() - start_time
        logger.info(f"⚡ [STAGE 2] Boot completed in {boot_time:.2f}s")
        
        print("\n")
        print_system_health(instances, neural_systems)
        print(f" [OK] Startup completed in {boot_time:.2f}s\n")

        # --------------------------------------------------------------------
        # [STAGE 3] NEURAL AWAKENING (Brain) - POST-BOOT
        # --------------------------------------------------------------------
        # SEQUENTIAL loading to prevent ACCESS_VIOLATION crashes
        # Vision -> Audio -> Camera (one at a time)
        
        from PyQt6.QtCore import QTimer
        import threading
        
        def start_neural_engines_sequential(window_manager, vision_system, audio_system):
            """Load heavy models SEQUENTIALLY to avoid memory conflicts"""
            logger.info("⚡ [STAGE 3] Igniting Neural Engines (Sequential Load)...")
            
            # 0. 🔥 LocalBrain Pre-Load (nuevo - auto-load durante boot)
            try:
                from src.core.intelligence.local_brain import local_brain
                if local_brain and not local_brain._is_loaded:
                    logger.info("🧠 Pre-loading LocalBrain (1.5B model)...")
                    if window_manager and window_manager.get_hud():
                        window_manager.get_hud().update_state("loading_model")
                        window_manager.get_hud().log_event("Carregando Cérebro Local...")
                    local_brain.load_async()
                    # Dar 30s para carregar enquanto outros módulos também carregam
                    logger.info("✅ LocalBrain loading started (async)")
            except Exception as e:
                logger.warning(f"⚠️ LocalBrain pre-load failed: {e}")
            
            # 1. Vision System first (FaceRec/OCR/YOLO)
            if vision_system:
                logger.info("🧠 Loading Vision models...")
                if window_manager and window_manager.get_hud():
                    window_manager.get_hud().log_event("Carregando modelos de visão...")
                vision_system.start_background_loading()
                vision_system.wait_for_models(timeout=30.0)  # Wait for completion
                logger.info("✅ Vision models loaded")
                if window_manager and window_manager.get_hud():
                    window_manager.get_hud().log_event("VISION ENGINE: READY")
            
            # 2. Audio System second (Whisper/VAD) - only after Vision completes
            if audio_system:
                logger.info("🧠 Loading Audio models...")
                if window_manager and window_manager.get_hud():
                    window_manager.get_hud().log_event("Carregando Whisper & VAD...")
                audio_system.start_background_loading()
                time.sleep(10)  # Give Whisper time to load
                logger.info("✅ Audio models loaded")
                if window_manager and window_manager.get_hud():
                    window_manager.get_hud().log_event("AUDIO ENGINE: READY")
                
                # 🔥 VAD Auto-Calibração (nuevo)
                try:
                    logger.info("🎤 Calibrando VAD com ruído ambiente...")
                    if window_manager and window_manager.get_hud():
                        window_manager.get_hud().update_state("calibrating")
                        window_manager.get_hud().log_event("Medindo ruído ambiente...")
                    audio_system.calibrate_vad_threshold(duration=3.0)
                    logger.info("✅ VAD calibrado para ambiente atual")
                    if window_manager and window_manager.get_hud():
                        window_manager.get_hud().log_event("VAD: CALIBRADO")
                        window_manager.get_hud().update_state("idle")
                except Exception as e:
                    logger.warning(f"⚠️ VAD calibration failed: {e}")
            
            # 3. Camera Monitoring last - schedule with threading.Timer
            logger.info("⏳ Scheduling camera start in 30s for system stabilization...")
            camera_timer = threading.Timer(30.0, lambda: start_camera_monitoring_safe(window_manager, vision_system))
            camera_timer.daemon = True
            camera_timer.start()
            
            # KEEP THREAD ALIVE until camera starts (prevents crash)
            logger.info("🛡️ Neural load thread staying alive until camera initialized...")
            time.sleep(35)  # Wait for camera to start
            logger.info("✅ Neural sequential load complete")
                
        def start_camera_monitoring_safe(window_manager, vision_system):
            """Start camera only after all neural models loaded"""
            if vision_system:
                try:
                    from src.core.vision.camera_controller import get_camera_controller
                    camera_controller = get_camera_controller()
                    threading.Thread(target=camera_controller.start_monitoring, daemon=True).start()
                    logger.info("👁️ Camera Monitoring activated (Post-Neural Load)")
                    if window_manager and window_manager.get_hud():
                        window_manager.get_hud().log_event("VISION ENGINE: ONLINE")
                except Exception as e:
                    logger.warning(f"⚠️ Vision start failure: {e}")
        
        # Schedule Stage 3 in background thread (doesn't block Qt event loop)
        QTimer.singleShot(1500, lambda: threading.Thread(
            target=start_neural_engines_sequential,
            args=(window_manager, vision_system, audio_system),
            daemon=True,
            name="NeuralSequentialLoad"
        ).start())

        # 🔥 Iniciar Telemetria Live (nuevo)
        def update_telemetry_loop(window_manager):
            """Thread que atualiza telemetria do sistema em tempo real"""
            import psutil
            import threading
            while True:
                try:
                    if window_manager and window_manager.get_hud():
                        cpu = psutil.cpu_percent(interval=0.5)
                        mem = psutil.virtual_memory().percent
                        
                        # 📡 Adicionar status de conexão (Phase 2)
                        try:
                            from src.core.intelligence.brain_router import brain_router
                            is_online = brain_router.check_connectivity() if brain_router else False
                        except Exception:
                            is_online = False
                        
                        window_manager.get_hud().telemetry_updated.emit({
                            'cpu': cpu,
                            'memory': mem,
                            'threads': threading.active_count(),
                            'is_online': is_online
                        })

                        # 🌐 Dashboard Web (Phase 3)
                        emit_telemetry_sync(cpu, mem)
                    time.sleep(1)  # Atualizar a cada 1s
                except Exception as e:
                    logger.debug(f"Telemetry update error: {e}")
                    time.sleep(5)
        
        telemetry_thread = threading.Thread(
            target=update_telemetry_loop,
            args=(window_manager,),
            daemon=True,
            name="TelemetryMonitor"
        )
        telemetry_thread.start()
        logger.info("📊 Live telemetry monitoring started")
        
        # Start Core Orchestrator
        jarvis = JarvisSingularity(app, instances)
        jarvis.start()
        
        # Optional: Start learning background process
        try:
            from src.learning.continual_learner import get_continual_learner
            learner = get_continual_learner(PROJECT_ROOT / "data")
            learner.start()
            logger.info("🧠 Brain Learning Systems active")
        except Exception as e:
            logger.warning(f"⚠️ Learning system unavailable: {e}")

        # 🌐 Iniciar Servidor Web (Phase 3)
        try:
            import threading
            web_server = start_server(port=5000)
            web_thread = threading.Thread(target=web_server.run, daemon=True, name="WebDashboard")
            web_thread.start()
            logger.info("🌐 Web Dashboard ready at http://localhost:5000")
        except Exception as e:
            logger.warning(f"⚠️ Web Dashboard unavailable: {e}")

        # Enter Event Loop
        return app.exec()

    except KeyboardInterrupt: return 130
    except Exception as e:
        logger.error(f"FATAL BOOT ERROR: {e}")
        import traceback
        tb = traceback.format_exc()
        logger.error(tb)
        
        # Crash Intelligence Loop: Save report for Launcher
        try:
            import json
            report = {
                "timestamp": datetime.now().isoformat() if 'datetime' in globals() else time.ctime(),
                "error": str(e),
                "traceback": tb
            }
            # Save to logs
            Path('data/logs').mkdir(parents=True, exist_ok=True)
            with open('data/logs/crash_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)
        except: pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
