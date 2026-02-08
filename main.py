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

# ============================================================================
# CRITICAL PATCHES (MUST RUN BEFORE ANY OTHER AI IMPORT)
# ============================================================================
# Fix for Torch DLL initialization (Error 1114)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_OFF"] = "TRUE"

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
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Ensure necessary data structure
Path('data/logs').mkdir(parents=True, exist_ok=True)

# Centralized Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/jarvis_singularity.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
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
    # Check PyTorch Stability (c10.dll)
    try:
        import torch
        _ = torch.zeros(1)
    except Exception as e:
        if "c10.dll" in str(e) or "1114" in str(e):
            issues.append({
                'level': 'CRITICAL',
                'component': 'AI Neural Engine (c10.dll)',
                'error': 'DLL dependency failure',
                'fix': 'Run START_JARVIS.bat --repair-pytorch'
            })
    # Check faces registry
    if not any(Path('data/faces').glob("*.j*")):
        issues.append({
            'level': 'WARNING',
            'component': 'Visual FaceID',
            'error': 'Zero authorized faces detected',
            'fix': 'Add user photos to data/faces/'
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
    ml_feats = [
        ("OCR (EasyOCR)", vs._ocr_ready if vs else False),
        ("YOLO (Detection)", vs._yolo_ready if vs else False),
        ("Face Recognition", len(getattr(vs, 'known_face_encodings', [])) > 0 if vs else False),
        ("PyTorch Neural", TORCH_AVAILABLE)
    ]
    for name, status in ml_feats:
        icon = "✅" if status else "❌"
        print(f" ├─ {icon} {name}")
    
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
    working = sum(1 for v in instances.values() if v) + sum(1 for _, s in ml_feats if s)
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
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

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
        """Start JARVIS with voice listening and HUD"""
        # Show HUD interface
        if self.window_manager:
            from interface.window_manager import InterfaceMode
            self.window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)
            logger.info("✅ HUD interface activated")
            hud = self.window_manager.get_hud()
            if hud:
                hud.log_event("SINGULARITY CORE ENGAGED")
                hud.log_event("INTERFACE MODE: HUD_OVERLAY")
        
        # 🟢 PROACTIVE MONITOR (Quantum Core)
        try:
            from src.core.intelligence.proactive_monitor import proactive_monitor
            proactive_monitor.start()
            logger.info("⚡ Proactive Monitor online (Sixth Sense Active)")
            if self.window_manager and self.window_manager.get_hud():
                self.window_manager.get_hud().log_event("PROACTIVE MONITOR ACTIVE")
        except Exception as e:
            logger.warning(f"⚠️ Failed to start Proactive Monitor: {e}")
            
        # 🎤 START MICROPHONE LISTENING
        if self.audio_system:
            logger.info("🎤 Starting continuous microphone listening...")
            success = self.audio_system.start_listening()
            if success:
                logger.info("✅ Microphone active - JARVIS is listening!")
                if self.window_manager and self.window_manager.get_hud():
                    self.window_manager.get_hud().log_event("AUDIO ENGINE: LISTENING")
                
                # Connect transcription callback (Emits signal to main thread)
                self.audio_system.on_transcription = self.transcription_received.emit
                
                # Update system tray to show listening status
                if self.window_manager and hasattr(self.window_manager, '_tray_icon') and self.window_manager._tray_icon:
                    self.window_manager._tray_icon.setToolTip("🎤 JARVIS - Listening")
            else:
                logger.error("❌ Failed to start microphone - check audio permissions")

        # 📊 TELEMETRY SYNC (Quantum Core)
        from PyQt6.QtCore import QTimer
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self._sync_hud_telemetry)
        self.telemetry_timer.start(2000) # Every 2s
        
    def _sync_hud_telemetry(self):
        """Sync core stats with HUD telemetry (Quantum Core)"""
        if not self.window_manager: return
        
        hud = self.window_manager.get_hud()
        if not hud: return
        
        try:
            # 1. Fetch Emotion
            from src.core.vision.camera_controller import camera_controller
            emotion = camera_controller.current_emotion
            
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
            else:
                logger.error("AI Agent not loaded")
                self._is_processing = False
                if self.window_manager:
                    hud = self.window_manager.get_hud()
                    if hud:
                        hud.update_state("error")
                        hud.show_response("Erro: Agente de IA offline.")
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

    def shutdown(self):
        logger.info("Initiating graceful shutdown sequence...")
        for name, instance in [("Vision", self.vision_system), ("Audio", self.audio_system), ("Integration", self.system_integrator)]:
            if instance: instance.cleanup()
        sys.exit(0)

# ============================================================================
# BOOT ENGINES
# ============================================================================

async def load_module_async(name: str, factory_func, *args):
    """Async wrapper for module initialization in thread pool"""
    loop = asyncio.get_event_loop()
    try:
        # Some modules might expect to be on the main thread (like GUI)
        # We use a thread pool for heavy non-GUI IO/ML tasks
        if name == "Window Manager":
             module = factory_func(*args)
        else:
            with ThreadPoolExecutor() as executor:
                module = await loop.run_in_executor(executor, factory_func, *args)
        logger.info(f"✅ {name} loaded")
        return (name, module)
    except Exception as e:
        logger.error(f"❌ {name} failed: {e}")
        return (name, None)

async def parallel_boot(app):
    """Orchestrates the parallel loading of all major systems"""
    print_progress("Iniciando Parallel Boot", 1, 10)
    
    # Delayed imports to stay parallel
    from interface.window_manager import get_window_manager
    from core.vision.vision_system import get_vision_system
    from core.audio.enhanced_audio import get_audio_system
    from core.actions.system_integrator import get_system_integrator
    
    step = 1
    total = 6
    
    async def load_with_progress(name, func, *args):
        nonlocal step
        res = await load_module_async(name, func, *args)
        step += 1
        print_progress("Iniciando Parallel Boot", step, total)
        return res

    tasks = [
        load_with_progress("Window Manager", get_window_manager, app),
        load_with_progress("Vision System", get_vision_system, PROJECT_ROOT / "data"),
        load_with_progress("Audio System", get_audio_system, PROJECT_ROOT / "data"),
        load_with_progress("System Integrator", get_system_integrator),
        load_with_progress("AI Agent", lambda: __import__("src.core.intelligence.ai_agent", fromlist=["ai_agent"]).ai_agent)
    ]
    
    results = await asyncio.gather(*tasks)
    print_progress("Parallel Boot Finalizado", 10, 10)
    print("\n")
    return dict(results)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    print("\n🌌 Initializing JARVIS Singularity Suite...")
    start_time = time.time()
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # 🆕 PARALLEL BOOT (3x faster)
        instances = asyncio.run(parallel_boot(app))
        
        # 🆕 WAIT FOR BACKGROUND MODELS (Fix timing bug)
        vision_system = instances.get("Vision System")
        if vision_system:
            vision_system.wait_for_models(timeout=15.0)
        
        # 🆕 LOAD NEURAL SYSTEMS (Advanced AI)
        neural_systems = None
        try:
            from src.core.intelligence.neural_systems import NeuralSystemsLoader
            from src.utils.config import Config
            config = Config()
            neural_systems = NeuralSystemsLoader(PROJECT_ROOT / "data", config)
        except Exception as e:
            logger.warning(f"⚠️ Neural Systems unavailable: {e}")
        
        boot_time = time.time() - start_time
        logger.info(f"⚡ Boot completed in {boot_time:.2f}s")
        
        print("\n")
        print_system_health(instances, neural_systems)
        print(f" [OK] Startup completed in {boot_time:.2f}s\n")

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

        return app.exec()

    except KeyboardInterrupt: return 130
    except Exception as e:
        logger.error(f"FATAL BOOT ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
