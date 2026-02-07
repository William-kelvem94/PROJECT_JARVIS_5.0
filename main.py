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

def print_system_health(instances):
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

    # Calculations for Score
    working = sum(1 for v in instances.values() if v) + sum(1 for _, s in ml_feats if s)
    total_slots = len(instances) + len(ml_feats)
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
class JarvisSingularity:
    def __init__(self, app, instances):
        self.app = app
        self.window_manager = instances.get("Window Manager")
        self.vision_system = instances.get("Vision System")
        self.audio_system = instances.get("Audio System")
        self.system_integrator = instances.get("System Integrator")
        
        self._setup_signals()
        logger.info("Singularity Core Engaged.")

    def _setup_signals(self):
        signal.signal(signal.SIGINT, lambda s, f: self.shutdown())
        signal.signal(signal.SIGTERM, lambda s, f: self.shutdown())

    def start(self):
        if self.window_manager:
            from interface.window_manager import InterfaceMode
            self.window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)

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
    from core.vision_system import get_vision_system
    from core.enhanced_audio import get_audio_system
    from core.system_integrator import get_system_integrator
    
    tasks = [
        load_module_async("Window Manager", get_window_manager, app),
        load_module_async("Vision System", get_vision_system, PROJECT_ROOT / "data"),
        load_module_async("Audio System", get_audio_system, PROJECT_ROOT / "data"),
        load_module_async("System Integrator", get_system_integrator)
    ]
    
    results = await asyncio.gather(*tasks)
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
        
        boot_time = time.time() - start_time
        logger.info(f"⚡ Boot completed in {boot_time:.2f}s")
        
        print("\n")
        print_system_health(instances)
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
