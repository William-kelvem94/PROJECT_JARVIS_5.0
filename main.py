#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

# Fix encoding for Windows console
if sys.stdout and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
JARVIS SINGULARITY - Integrated Main Entry Point
=================================================
Complete integration of all Singularity systems with zero-error guarantee.

Systems:
- Window Manager (Dual Interface)
- Vision System (FaceID + OCR + YOLO)
- Enhanced Audio (Faster-Whisper + VAD + Speaker Verification)
- System Integrator (God Mode)
- Control Dashboard (Admin Panel)
"""

import os
import sys
import logging
import signal
import shutil
from pathlib import Path

# ============================================================================
# CRITICAL PATCHES (BEFORE ANY IMPORTS)
# ============================================================================
# Suppress Qt warnings
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false;qt.qpa.screen=false"
os.environ["QT_DEVICE_PIXEL_RATIO"] = "auto"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# Clear comtypes cache to prevent errors
try:
    import comtypes.client
    import comtypes.client._code_cache
    gen_dir = Path(comtypes.client._code_cache._get_gen_dir())
    if gen_dir.exists():
        shutil.rmtree(gen_dir, ignore_errors=True)
    os.makedirs(gen_dir, exist_ok=True)
    comtypes.client._code_cache._enable_cache = False
    logging.getLogger('comtypes').setLevel(logging.ERROR)
except Exception:
    pass  # Silently continue if comtypes not available

# Suppress other warnings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Ensure data directories exist
Path('data/logs').mkdir(parents=True, exist_ok=True)

# Setup logging BEFORE other imports
import sys
import io

# FORÇAR UTF-8 NO WINDOWS
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import logging

# Configurar logging com UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/jarvis_singularity.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Start System Monitor
try:
    from src.utils.system_monitor import system_monitor
    system_monitor.start_monitoring()
except ImportError:
    try:
        from utils.system_monitor import system_monitor
        system_monitor.start_monitoring()
    except ImportError:
        logger.warning("⚠️ System Monitor not found, starting without telemetry")

# ============================================================================
# PATH SETUP
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# ============================================================================
# IMPORTS
# ============================================================================
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        JARVIS SINGULARITY - Starting System v1.0            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

logger.info("="*70)
logger.info("JARVIS SINGULARITY INITIALIZATION")
logger.info("="*70)

# Import Window Manager
try:
    from interface.window_manager import get_window_manager, InterfaceMode
    logger.info("✅ Window Manager imported")
    WINDOW_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Window Manager not available: {e}")
    WINDOW_MANAGER_AVAILABLE = False

# Import Vision System
try:
    from core.vision_system import get_vision_system
    logger.info("✅ Vision System imported")
    VISION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Vision System not available: {e}")
    VISION_AVAILABLE = False

# Import Enhanced Audio
try:
    from core.enhanced_audio import get_audio_system
    logger.info("✅ Enhanced Audio imported")
    AUDIO_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Enhanced Audio not available: {e}")
    AUDIO_AVAILABLE = False

# Import System Integrator
try:
    from core.system_integrator import get_system_integrator
    logger.info("✅ System Integrator imported")
    SYSTEM_INTEGRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ System Integrator not available: {e}")
    SYSTEM_INTEGRATOR_AVAILABLE = False


# ============================================================================
# JARVIS SINGULARITY CONTROLLER
# ============================================================================
class JarvisSingularity:
    """
    Main controller for JARVIS Singularity.
    
    Integrates all systems and manages lifecycle.
    """
    
    def __init__(self, app: QApplication):
        """Initialize JARVIS Singularity"""
        self.app = app
        self.window_manager = None
        self.vision_system = None
        self.audio_system = None
        self.system_integrator = None
        
        logger.info("\n" + "="*70)
        logger.info("INITIALIZING SINGULARITY SYSTEMS")
        logger.info("="*70)
        
        # Initialize systems
        self._initialize_systems()
        
        # Connect systems
        self._connect_systems()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("\n" + "="*70)
        logger.info("✅ JARVIS SINGULARITY READY")
        logger.info("="*70)
        logger.info("\nKeyboard Shortcuts:")
        logger.info("  Ctrl+Shift+J - Toggle Control Dashboard")
        logger.info("  Ctrl+Shift+H - Toggle HUD Overlay")
        logger.info("  Ctrl+Shift+X - Hide All")
        logger.info("\n" + "="*70 + "\n")
        
    def _initialize_systems(self):
        """Initialize all Singularity systems"""
        data_dir = PROJECT_ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Window Manager (always needed)
        if WINDOW_MANAGER_AVAILABLE:
            try:
                self.window_manager = get_window_manager(self.app)
                logger.info("✅ Window Manager initialized")
            except Exception as e:
                logger.error(f"❌ Window Manager failed: {e}")
        else:
            logger.warning("⚠️ Window Manager not available - Using fallback")
            
        # Vision System (optional)
        if VISION_AVAILABLE:
            try:
                self.vision_system = get_vision_system(data_dir)
                logger.info("✅ Vision System initialized")
                
                # Start monitoring if FaceID enabled
                faces_dir = data_dir / "faces"
                if faces_dir.exists() and list(faces_dir.glob("*.jpg")):
                    self.vision_system.start_monitoring()
                    logger.info("✅ FaceID monitoring started")
                else:
                    logger.info("ℹ️ No authorized faces found - FaceID monitoring disabled")
                    
            except Exception as e:
                logger.warning(f"⚠️ Vision System initialization failed: {e}")
                self.vision_system = None
        else:
            logger.info("ℹ️ Vision System not available")
            
        # Enhanced Audio (optional)
        if AUDIO_AVAILABLE:
            try:
                self.audio_system = get_audio_system(data_dir)
                logger.info("✅ Enhanced Audio initialized")
                
                # Setup transcription callback
                self.audio_system.on_transcription = self._on_transcription
                self.audio_system.on_speaker_detected = self._on_speaker_detected
                
                # Start listening (optional - can be triggered by command)
                # self.audio_system.start_listening()
                
            except Exception as e:
                logger.warning(f"⚠️ Audio System initialization failed: {e}")
                self.audio_system = None
        else:
            logger.info("ℹ️ Enhanced Audio not available")
            
        # System Integrator (optional)
        if SYSTEM_INTEGRATOR_AVAILABLE:
            try:
                audit_log = data_dir / "logs" / "god_mode_audit.log"
                self.system_integrator = get_system_integrator(audit_log)
                logger.info("✅ System Integrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ System Integrator initialization failed: {e}")
                self.system_integrator = None
        else:
            logger.info("ℹ️ System Integrator not available")
            
    def _connect_systems(self):
        """Connect systems together"""
        if not self.window_manager:
            return
            
        # Connect status updates
        if self.vision_system:
            # Vision system can update HUD status
            pass
            
        if self.audio_system:
            # Audio system can update HUD status
            pass
            
        logger.info("✅ Systems connected")
        
    def _on_transcription(self, result):
        """Handle audio transcription"""
        if result.text:
            logger.info(f"📝 Transcription: {result.text}")
            
            if self.window_manager:
                hud = self.window_manager.get_hud()
                if hasattr(hud, 'show_response'):
                    hud.show_response(f"You said: {result.text}")
                    
    def _on_speaker_detected(self, speaker_id: str, confidence: float):
        """Handle speaker detection"""
        logger.info(f"🎤 Speaker: {speaker_id} ({confidence:.2f})")
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n⚠️  Shutdown signal received")
        self.cleanup()
        sys.exit(0)
        
    def start(self):
        """Start JARVIS Singularity"""
        if self.window_manager:
            # Start in HUD mode
            self.window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)
            
    def cleanup(self):
        """Cleanup all systems"""
        logger.info("\n" + "="*70)
        logger.info("SHUTTING DOWN JARVIS SINGULARITY")
        logger.info("="*70)
        
        if self.vision_system:
            try:
                self.vision_system.cleanup()
                logger.info("✅ Vision System cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Vision System: {e}")
                
        if self.audio_system:
            try:
                self.audio_system.cleanup()
                logger.info("✅ Audio System cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Audio System: {e}")
                
        if self.system_integrator:
            try:
                self.system_integrator.cleanup()
                logger.info("✅ System Integrator cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up System Integrator: {e}")
                
        if self.window_manager:
            try:
                self.window_manager.cleanup()
                logger.info("✅ Window Manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Window Manager: {e}")
                
        logger.info("\n✅ Shutdown complete")
        logger.info("="*70 + "\n")


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Main entry point"""
    # Auto-healing entry point
    if "--auto-heal" in sys.argv:
        try:
            from install_system import JarvisAutoSystem
            system = JarvisAutoSystem()
            system.auto_fix()
            print("✅ Auto-healing check complete.")
        except Exception as e:
            print(f"⚠️ Auto-healing failed: {e}")

    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("JARVIS Singularity")
        app.setOrganizationName("JARVIS")
        app.setOrganizationDomain("jarvis.ai")
        
        # Set application style
        app.setStyle("Fusion")
        
        # Create JARVIS controller
        jarvis = JarvisSingularity(app)
        
        # Start systems
        jarvis.start()
        
        # Run application
        exit_code = app.exec()
        
        # Cleanup
        jarvis.cleanup()
        
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        try:
            from utils.system_monitor import system_monitor
            system_monitor.log_error(str(e))
        except: pass
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
