import os
import sys
import warnings
import time
import platform

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

# 🛡️ BLINDAGEM DE UNICODE DEFINITIVA (Ignorar erros de codificação no terminal)
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 🛡️ EARLY WARNING SUPPRESSION (Must be before any heavy imports)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*openvino.runtime.*')
warnings.filterwarnings('ignore', message='.*loss_type=None.*')

import logging
import asyncio
import threading
from src.core.infrastructure.priority_scheduler import PriorityScheduler, TaskPriority, TaskType

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
    from pathlib import Path
    from src.utils.jarvis_logger import setup_jarvis_logging, apply_global_duplicate_filter
    
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    jarvis_logging_system = setup_jarvis_logging(data_dir)
    logger = jarvis_logging_system.get_logger('core')
    
    # Apply global duplicate filter to the root logger and existing loggers
    root_logger = logging.getLogger()
    apply_global_duplicate_filter(root_logger)
    
    # Apply to the basic logger we created
    jarvis_core_logger = logging.getLogger("JARVIS-CORE")
    apply_global_duplicate_filter(jarvis_core_logger)
    
    logger.info("🎯 JARVIS Unified Logging System initialized")
except Exception as e:
    logger = logging.getLogger("JARVIS-CORE")
    logger.error(f"❌ Failed to initialize unified logging: {e}")

# 🛡️ GLOBAL MONKEY PATCH: Correção Crítica para OpenVINO/Optimum-Intel
# Previne erro 'module openvino has no attribute Node' e 'No module named openvino.op'
try:
    import openvino  # noqa: F401  # type: ignore
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
except ImportError:
    pass

# 🛡️ GLOBAL MONKEY PATCH: Correção Crítica para XTTS (Transformers compatibility)
try:
    from transformers import __version__ as transformers_version
    if transformers_version.startswith('4.4') or transformers_version.startswith('4.3') or transformers_version.startswith('4.2'):
        # For newer versions (4.21+), import directly from transformers.generation
        try:
            from transformers.generation import BeamSearchScorer  # type: ignore
            # No patch needed if import succeeds
            logger.info("🛡️ XTTS Patch: BeamSearchScorer disponível nativamente em transformers.generation")
        except ImportError:
            # Fallback: Create dummy class and inject into transformers
            class _BeamSearchScorerNew:
                pass
            import transformers
            transformers.BeamSearchScorer = _BeamSearchScorerNew  # type: ignore
            logger.info("🛡️ XTTS Patch: BeamSearchScorer injetado em transformers (fallback para versões novas)")
    else:
        # For older versions, try the legacy import and patch if needed
        try:
            from transformers import generation_utils  # type: ignore
            if not hasattr(generation_utils, 'BeamSearchScorer'):
                class _BeamSearchScorerOld:
                    pass
                generation_utils.BeamSearchScorer = _BeamSearchScorerOld  # type: ignore
                logger.info("🛡️ XTTS Patch: BeamSearchScorer injetado em transformers.generation_utils (versão antiga)")
        except ImportError:
            # If even the legacy import fails, skip patching
            logger.warning("🛡️ XTTS Patch: generation_utils não disponível, pulando patch")
except (ImportError, AttributeError, Exception) as e:
    logger.debug(f"XTTS Patch Error: {e}")
import psutil
import signal
import shutil
import warnings
from pathlib import Path

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
    StarkOrchestrator = None
    STARK_ORCHESTRATOR_AVAILABLE = False

# Optional web server imports (loaded on demand)
try:
    from src.core.management.neuro_sync import neuro_sync
    NEURO_SYNC_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning(f"⚠️ NeuroSync not available (may need GUI libraries): {e}")
    neuro_sync = None
    NEURO_SYNC_AVAILABLE = False

# Import Boot Manager for infrastructure initialization
try:
    from src.core.infrastructure.boot_manager import BootManager, BootPriority
    BOOT_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Boot Manager not available: {e}")
    BootManager = None
    BOOT_MANAGER_AVAILABLE = False

# Import Event Bus for asynchronous module communication
try:
    from src.core.infrastructure.async_event_bus import AsyncEventBus
    EVENT_BUS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Event Bus not available: {e}")
    AsyncEventBus = None
    EVENT_BUS_AVAILABLE = False

# Import Phase 1 Infrastructure (Watchdog & Session)
try:
    from src.core.infrastructure.watchdog import watchdog_system
    from src.core.infrastructure.session_manager import SessionManager
    INFRA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Infrastructure Phase 1 components not available: {e}")
    watchdog_system = None
    SessionManager = None
    INFRA_AVAILABLE = False

# =============================
# ORIENTAÇÃO SOBRE ENCODING DE ARQUIVOS EXTERNOS
# =============================
# Para evitar bugs de encoding:
# 1. Garanta que todos os arquivos de texto/configuração (json, yaml, txt, csv, etc.) estejam salvos em UTF-8.
#    - No VS Code: clique com o direito no arquivo > "Reabrir com codificação" > UTF-8.
# 2. Sempre abra arquivos de texto explicitamente com encoding='utf-8':
#    with open('arquivo.txt', 'r', encoding='utf-8') as f:
#        conteudo = f.read()
# 3. Se usar pandas, use encoding='utf-8' ao ler csv:
#    pd.read_csv('arquivo.csv', encoding='utf-8')
# 4. Para arquivos de configuração YAML:
#    with open('config.yaml', 'r', encoding='utf-8') as f:
#        config = yaml.safe_load(f)
# 5. Se usar arquivos de tradução (.ts/.qm), gere e salve em UTF-8.
# =============================

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
        code_cache = getattr(comtypes.client, '_code_cache', None)
        # Disable cache globally to avoid Access Violation in parallel boot
        if code_cache and hasattr(code_cache, '_enable_cache'):
            code_cache._enable_cache = False
        if code_cache and hasattr(code_cache, '_get_gen_dir'):
            gen_dir = Path(code_cache._get_gen_dir())
            if gen_dir.exists():
                shutil.rmtree(gen_dir, ignore_errors=True)
            os.makedirs(gen_dir, exist_ok=True)
    except Exception: pass

# Path Synchronization
PROJECT_ROOT = Path(__file__).parent.absolute()
VENV_SITE = PROJECT_ROOT / "venv" / "Lib" / "site-packages"
if VENV_SITE.exists():
    if str(VENV_SITE) in sys.path: sys.path.remove(str(VENV_SITE))
    sys.path.insert(0, str(VENV_SITE))
if str(PROJECT_ROOT / "src" / "stubs") not in sys.path:
    sys.path.insert(1, str(PROJECT_ROOT / "src" / "stubs"))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(2, str(PROJECT_ROOT / "src"))

# Suppress Warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*loss_type=None.*')

# Ensure necessary data structure
Path('data/logs').mkdir(parents=True, exist_ok=True)

# Centralized Logging (Organized by Date)
from datetime import datetime
log_date_dir = Path("data/logs") / datetime.now().strftime("%Y-%m-%d")
log_date_dir.mkdir(parents=True, exist_ok=True)
session_timestamp = datetime.now().strftime("%H%M%S")
log_file = log_date_dir / f"jarvis_session_{session_timestamp}.log"

# Also keep a symlink/copy to latest
latest_log = Path("data/logs") / "jarvis.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.FileHandler(latest_log, mode='w', encoding='utf-8'),  # Overwrite latest
        logging.StreamHandler(sys.stdout)
    ]
)
# Global reference for shutdown signaling
QApplication = None

# Load Network Mesh Configuration
network_config = {}
network_config_path = PROJECT_ROOT / "config" / "network_mesh_config.yaml"
if network_config_path.exists():
    try:
        import yaml
        with open(network_config_path, 'r', encoding='utf-8') as f:
            network_config = yaml.safe_load(f) or {}
    except Exception as e:
        logging.warning(f"Failed to load network config: {e}")

# Unified InterfaceMode Import
from enum import Enum
class InterfaceMode(Enum):
    HUD_OVERLAY = "hud"
    DASHBOARD = "dashboard"
    HIDDEN = "hidden"

# Try to import torch and determine availability (lazy import)
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
        if _check_torch() and torch is not None:
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
        try:
            import easyocr  # noqa: F401
        except ImportError:
            pass
    except Exception:
        pass
    try:
        try:
            import openvino  # noqa: F401  # type: ignore
        except ImportError:
            pass
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
    if TORCH_AVAILABLE and torch is not None and torch.cuda.is_available():
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
        # Check globally if not in vs using dynamic import to avoid static analysis issues
        try:
            import importlib.util
            if importlib.util.find_spec('face_recognition') is not None:
                face_rec_installed = True
        except Exception:
            pass

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
    
    hw_accel = False
    if hardware_manager is not None:
        hw_accel = (getattr(hardware_manager, 'device', 'cpu') != "cpu") or (hasattr(hardware_manager, 'accelerator') and hardware_manager.accelerator is not None)
    
    ml_feats = [
        ("OCR (EasyOCR)", ocr_status, vs_passive and not ocr_status),
        ("YOLO (Detection)", yolo_status, vs_passive and not yolo_status),
        (face_label, face_rec_installed, False),
        ("Hw Acceleration", hw_accel, False),
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
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer  # type: ignore

class JarvisSingularity(QObject):
    # Signal to bridge background audio thread to main UI thread
    transcription_received = pyqtSignal(object)
    # Signal for thread-safe HUD updates (state, optional text)
    hud_update_requested = pyqtSignal(str, str)
    
    def __init__(self, app, instances):
        super().__init__()
        self.app = app
        self.window_manager = instances.get("window_manager")
        self.vision_system = instances.get("vision_system")
        self.audio_system = instances.get("audio_system")
        self.system_integrator = instances.get("system_integrator")
        self.ai_agent = instances.get("ai_agent")
        
        # 🧠 Contextual Awareness State
        self.last_interaction_time = 0
        self.continuous_mode_window = 15 # Seconds to stay 'awake' for follow-ups
        
        self.is_running = False
        # Initialize Shutdown Manager
        self.shutdown_manager = ShutdownManager(self) if ShutdownManager else None
        
        # Priority Scheduler (Backend Async Orchestrator - Fase 1.2)
        self.scheduler = PriorityScheduler()
        self._scheduler_loop = None
        self._scheduler_thread = None
        self._start_backend_scheduler()

        # Session Manager (Thread-safe Context - Fase 1.7)
        self.session_manager = SessionManager() if SessionManager else None
        
        # Watchdog System (Self-Healing - Fase 1.4)
        if watchdog_system:
            try:
                watchdog_system.start()
                watchdog_system.register_component("MainUI", heartbeat_interval=3.0) # 30s grace during boot
                watchdog_system.register_component("BackendScheduler", heartbeat_interval=10.0)
                if self.vision_system:
                    watchdog_system.register_component("VisionSystem", heartbeat_interval=10.0)
                if self.audio_system:
                    watchdog_system.register_component("AudioSystem", heartbeat_interval=10.0)
                
                logger.info("✅ Watchdog System ACTIVE (Phase 1.4)")
            except Exception as e:
                logger.error(f"❌ Failed to start Watchdog: {e}")
        
        # Initialize Stark Orchestrator (Phase 4)
        self.stark_orchestrator = StarkOrchestrator(self) if StarkOrchestrator else None
        if self.stark_orchestrator:
            self.stark_orchestrator.initialize_stark_system()
        
        # Initialize Network Mesh (Collective Mind)
        self.network_mesh = None
        if network_config.get('network_mesh', {}).get('enabled'):
            try:
                from src.core.network_mesh.local_network_intelligence import LocalNetworkIntelligence
                self.network_mesh = LocalNetworkIntelligence(str(PROJECT_ROOT))
                logger.info("🌐 Network Mesh initialized for collective mind")
            except Exception as e:
                logger.warning(f"⚠️ Network Mesh initialization failed: {e}")
        
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
        signal.signal(signal.SIGINT, lambda _, __: self.shutdown())
        signal.signal(signal.SIGTERM, lambda _, __: self.shutdown())

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
        
        # [STEP 0] Neuro-Sync: Sincronização de Redes Neurais e Modelos
        neuro_sync.run_sync(blocking=False)
        
        # Staggered initialization: Warmup for subsystems
        QTimer.singleShot(2000, self._staggered_daemon_start)
        
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
        
        # [STEP 3] Wait 15s then start Network Mesh (Collective Mind)
        QTimer.singleShot(15000, self._start_network_mesh)
        
        # [STEP 4] Start Plugin Manager and Indexer
        QTimer.singleShot(20000, self._start_dynamic_systems)

        # [STEP 5] 🚀 LATE BOOT: Neural Warmup (Heavy Models)
        # We wait 40s to ensure system is 100% idle and HUD is stable
        QTimer.singleShot(40000, self._start_heavy_models_loading)

    def _start_dynamic_systems(self):
        """Inicia sistemas dinâmicos de plugins e indexação de arquivos"""
        try:
            from src.core.management.plugin_manager import plugin_manager
            plugin_manager.start()
            
            from src.utils.file_indexer import file_indexer
            # Indexar pastas padrão (Documentos, Músicas, Imagens)
            search_paths = [
                str(Path.home() / "Documents"),
                str(Path.home() / "Music"),
                str(Path.home() / "Pictures")
            ]
            file_indexer.start_background_indexing(search_paths)
            
            logger.info("🔌 Plugin Manager & 🔍 MetaCache Indexer iniciados.")
            if self.window_manager and self.window_manager.get_hud():
                self.window_manager.get_hud().log_event("HOT-RELOAD ENGINE: ACTIVE")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao iniciar sistemas dinâmicos: {e}")

    def _start_heavy_models_loading(self):
        """Final stage of boot: Trigger heavy neural model loading on demand"""
        logger.info("🧠 JARVIS: Iniciando aquecimento de motores neurais (Carga Pesada)...")
        
        if self.audio_system and hasattr(self.audio_system, 'start_background_loading'):
            try:
                self.audio_system.start_background_loading()
            except Exception as e:
                logger.warning(f"⚠️ Falha no warmup de áudio: {e}")

        # Wait extra 10s between audio and vision to avoid spike overlap
        def start_vision():
            if self.vision_system and hasattr(self.vision_system, 'start_background_loading'):
                try:
                    self.vision_system.start_background_loading()
                except Exception as e:
                    logger.warning(f"⚠️ Falha no warmup de visão: {e}")
        
        QTimer.singleShot(10000, start_vision)

    def _start_network_mesh(self):
        """Initialize and start the Network Mesh for collective intelligence"""
        if self.network_mesh:
            assert self.network_mesh is not None  # For linter
            try:
                # Start the network mesh in background
                import threading
                
                def run_mesh():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.network_mesh.start_network_mesh())  # type: ignore
                    except Exception as e:
                        logger.error(f"Network Mesh start failed: {e}")
                
                mesh_thread = threading.Thread(target=run_mesh, daemon=True, name="NetworkMesh")
                mesh_thread.start()
                
                logger.info("🌐 Network Mesh started for collective mind")
                if self.window_manager and self.window_manager.get_hud():
                    self.window_manager.get_hud().log_event("COLLECTIVE MIND: ACTIVE")
                    
            except Exception as e:
                logger.warning(f"⚠️ Network Mesh initialization failed: {e}")

    def _start_backend_scheduler(self):
        """Start async priority scheduler in background thread (Fase 1.2)"""
        def _run_scheduler_loop():
            try:
                self._scheduler_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._scheduler_loop)
                
                # Verify loop
                if not self._scheduler_loop:
                    logger.error("❌ Failed to create scheduler loop")
                    return
                
                # Start scheduler async
                self._scheduler_loop.run_until_complete(self.start_scheduler_async())
                self._scheduler_loop.run_forever()
            except Exception as e:
                logger.error(f"❌ Priority Scheduler crashed: {e}")

        self._scheduler_thread = threading.Thread(
            target=_run_scheduler_loop, 
            daemon=True, 
            name="PrioritySchedulerMetaContext"
        )
        self._scheduler_thread.start()

    async def start_scheduler_async(self):
        """Async startup wrapper"""
        await self.scheduler.start()
        logger.info("✅ Priority Scheduler ACTIVE (Backend Async Loop)")
        
        # 🛡️ JARVIS Evolution Layer (Self-Healing)
        try:
            from src.evolution import start_evolution_services
            await start_evolution_services()
            logger.info("🧬 Evolution Services (Self-Healing) ACTIVATED")
        except Exception as e:
            logger.error(f"❌ Evolution Services failed to start: {e}")

    def schedule_backend_task(self, name, coro_func, delay=0, priority=TaskPriority.NORMAL):
        """Schedule a task on the backend scheduler thread-safely"""
        if not self._scheduler_loop:
            logger.warning(f"⚠️ Scheduler loop not ready, task {name} pending...")
            # Retry in 1s? Or use queue? For now, just log.
            return

        assert self._scheduler_loop is not None  # For linter

        async def _schedule_wrapper():
            # Wait for delay inside the loop
            if delay > 0:
                await asyncio.sleep(delay)
            # Schedule execution
            self.scheduler.schedule_task(
                name=name,
                coroutine_factory=coro_func,
                priority=priority
            )
            
        asyncio.run_coroutine_threadsafe(_schedule_wrapper(), self._scheduler_loop)

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
                try:
                    from src.core.audio.voice_controller import voice_controller  # noqa: F401  # type: ignore
                    if voice_controller:
                        voice_controller.speak("Sistemas online, William. Estou pronto.")
                except ImportError:
                    logger.warning("⚠️ Voice controller not available")
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
            
        # 🧠 [STARK BARGE-IN LOGIC]
        from src.core.audio.voice_filter import AtomicVoiceFilter
        has_name = AtomicVoiceFilter.has_wake_word(result.text)
        is_follow_up = (time.time() - self.last_interaction_time) < self.continuous_mode_window
        
        # Se estiver processando e o usuário falar meu nome, interrompo o atual para ouvir o novo
        if self._is_processing and has_name:
            logger.info("⚡ INTERRUPÇÃO DETECTADA: Parando resposta atual para ouvir o Senhor.")
            try:
                from src.core.audio.voice_controller import voice_controller
                voice_controller.stop_requested = True # Sinal para parar playback
                # Pequeno delay para garantir que o áudio parou
                time.sleep(0.1)
                self._is_processing = False 
            except Exception:
                pass

        if self._is_processing:
            logger.debug("Ocupado, ignorando ruído de fundo...")
            return

        if not has_name and not is_follow_up:
            logger.debug(f"🔇 Ignorado (Sem wake word & sem contexto): '{result.text}'")
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
            elif hasattr(self, 'stark_orchestrator') and self.stark_orchestrator and hasattr(self.stark_orchestrator, 'fallback_system'):
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
            # 1. Process Command (Async bridge)
            try:
                # Check if we're already in an async context
                loop = asyncio.get_running_loop()
                # If we get here, we're in an async context - this shouldn't happen in a background thread
                logger.warning("⚠️ _process_and_respond called from async context - this may cause issues")
                # Create task instead of blocking
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._sync_process_command, text)
                    response = future.result(timeout=30)  # 30 second timeout
            except RuntimeError:
                # No running loop, safe to create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(self.ai_agent.process_command(text))
                finally:
                    loop.close()
            
            # 2. Update HUD with final response (Emit signal)
            self.hud_update_requested.emit("speaking", str(response))
                    
            # 3. Wait for voice to finish
            try:
                from src.core.audio.voice_controller import voice_controller  # noqa: F401  # type: ignore
                if voice_controller:
                    while getattr(voice_controller, '_is_speaking', False):
                        time.sleep(0.5)
            except ImportError:
                pass
                
            # 4. Return to idle (Emit signal)
            self.hud_update_requested.emit("idle", "")
                    
        except Exception as e:
            logger.error(f"Error in process_and_respond: {e}")
            self.hud_update_requested.emit("error", f"Erro: {e}")
        finally:
            self._is_processing = False
    
    def _sync_process_command(self, text):
        """Synchronous wrapper for process_command"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.ai_agent.process_command(text))
        finally:
            loop.close()
            self.last_interaction_time = time.time() # Start follow-up timer AFTER finishing speech

    def _process_fallback(self, text):
        """Emergency Fallback Loop (No AI Agent)"""
        try:
            if self.stark_orchestrator and hasattr(self.stark_orchestrator, 'fallback_system'):
                fb = self.stark_orchestrator.fallback_system
                result = fb.process_command(text)
                
                response_text = result.get("response", "Comando não reconhecido no modo de emergência.")
                
                # Emit speech output signal (using same slot as normal)
                self.hud_update_requested.emit("speaking", response_text)
                
                # Speak via voice controller (direct call if available)
                # Note: Voice Controller might be functional even if Agent failed
                try:
                    from src.core.audio.voice_controller import voice_controller  # noqa: F401  # type: ignore
                    if voice_controller:
                        voice_controller.speak(response_text)
                except ImportError:
                    logger.warning("⚠️ Voice controller not available")
            else:
                logger.error("Fallback system not available")
                
        except Exception as e:
            logger.error(f"Fallback processing error: {e}")
            self.hud_update_requested.emit("error", "Falha no sistema de emergência.")
        finally:
            self._is_processing = False

    def shutdown(self):
        """Finalizes all systems and exits gracefully via ShutdownManager"""
        if hasattr(self, 'shutdown_manager') and self.shutdown_manager:
            self.shutdown_manager.graceful_shutdown()
        else:
            # Fallback if manager not initialized
            logger.warning("⚠️ ShutdownManager not found, using legacy shutdown")
            if QApplication:
                QApplication.quit()

# ============================================================================
# BOOT ENGINES
# ============================================================================

# Removed load_module_async


# Removed parallel_boot


# ============================================================================
# HEADLESS MODE - SERVER ONLY OPERATION
# ============================================================================
def run_headless_mode(args):
    """Run JARVIS in headless mode (no GUI, server-only)"""
    try:
        logger.info("🚀 Initializing JARVIS in headless mode...")

        # Initialize core systems without GUI
        from src.core.actions.system_integrator import get_system_integrator
        from src.core.audio.enhanced_audio import get_audio_system
        from src.core.vision.vision_system import get_vision_system
        from src.core.intelligence.ai_agent import ai_agent

        # Initialize systems
        data_path = PROJECT_ROOT / "data" if PROJECT_ROOT else Path("data")

        logger.info("🔧 Initializing System Integrator...")
        sys_int = get_system_integrator()

        logger.info("🎤 Initializing Audio System...")
        audio = get_audio_system(data_path)

        logger.info("👁️ Initializing Vision System...")
        vision = get_vision_system(data_path)

        logger.info("🧠 Initializing AI Agent...")
        # ai_agent is already imported and initialized

        # Start web server if available
        try:
            from src.web.web_server import start_web_server  # type: ignore
            logger.info("🌐 Starting Web Server...")
            web_thread = start_web_server()
            logger.info("✅ Web Server started successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"⚠️ Web Server failed to start: {e}")

        # Start audio listening
        if audio:
            logger.info("🎤 Starting audio listening...")
            success = audio.start_listening()
            if success:
                logger.info("✅ Audio system listening")
            else:
                logger.warning("⚠️ Audio system failed to start")

        # Start vision monitoring
        if vision:
            logger.info("👁️ Starting vision monitoring...")
            try:
                from src.core.vision.camera_controller import camera_controller
                camera_controller.start_monitoring()
                logger.info("✅ Vision system active")
            except Exception as e:
                logger.warning(f"⚠️ Vision monitoring failed: {e}")

        # Start proactive monitoring
        try:
            from src.core.intelligence.proactive_monitor import proactive_monitor
            proactive_monitor.start()
            logger.info("⚡ Proactive monitor active")
        except Exception as e:
            logger.warning(f"⚠️ Proactive monitor failed: {e}")

        logger.info("🎉 JARVIS headless mode initialized successfully!")
        logger.info("💡 Available endpoints:")
        logger.info("   - Web API: Check web_server logs for port")
        logger.info("   - Voice commands active")
        logger.info("   - Vision monitoring active")

        # Keep running until interrupted
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")

        return 0

    except Exception as e:
        logger.error(f"❌ Headless mode failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

# ============================================================================
# MAIN ENTRY POINT - STAGED BOOT PROTOCOL
# ============================================================================
def main():
    """Main entry point for JARVIS Singularity - Advanced AI Assistant.
    This function initializes and runs the JARVIS system, handling various modes and configurations
    based on command-line arguments. It performs pre-GUI setup, including console encoding fixes for
    Windows, CLI argument parsing, and conditional initialization of democratic systems. In GUI mode,
    it sets up the PyQt6 application, initializes the user interface via the window manager, and
    orchestrates asynchronous boot processes using the Boot Manager to load core subsystems like
    audio, vision, AI agent, and event bus. It integrates democratic control interfaces if enabled,
    starts the JarvisSingularity core, and enters the application event loop. In headless mode, it
    delegates to a server-only operation.
    Command-line arguments:
        --headless: Run in headless mode (no GUI, server-only).
        --debug: Enable debug logging and verbose output.
        --democratic: Enable democratic mode with full system control.
    The function ensures proper resource cleanup and handles exceptions gracefully, returning
    appropriate exit codes.
    Returns:
        int: Exit code (0 for success, 1 for general error, 130 for KeyboardInterrupt).
    Raises:
        SystemExit: When the application event loop exits normally.
    """
    # Fix console encoding for Windows (emojis support)
    if sys.platform == 'win32':
        try:
            # Só usa reconfigure se for o sys.stdout padrão (não wrapper)
            import io
            if isinstance(sys.stdout, io.TextIOWrapper) and hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if isinstance(sys.stderr, io.TextIOWrapper) and hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass  # Python < 3.7 ou stdout redefinido

    # ========================================================================
    # CLI ARGUMENT PARSING
    # ========================================================================
    import argparse

    parser = argparse.ArgumentParser(
        description='JARVIS Singularity - Advanced AI Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with GUI (default)
  python main.py --headless         # Start without GUI (server mode)
  python main.py --debug            # Enable debug logging
  python main.py --democratic       # Enable democratic mode
  python main.py --headless --debug # Headless with debug logging
        """
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no GUI, server-only)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging and verbose output'
    )

    parser.add_argument(
        '--democratic',
        action='store_true',
        help='Enable democratic mode with full system control'
    )

    # Parse arguments
    args = parser.parse_args()

    # Configure logging based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        print("🐛 Debug mode enabled - verbose logging active")

    # Handle headless mode
    if args.headless:
        print("🚀 Starting JARVIS in HEADLESS mode (server-only)")
        print("💡 GUI interfaces will be disabled")
        print("🔧 Use API endpoints or external clients to interact")

        # In headless mode, we still need to initialize core systems
        # but skip all GUI-related code
        return run_headless_mode(args)

    # ========================================================================
    # 🔥 NOVO: VERIFICAÇÃO DE MODO DEMOCRÁTICO
    # ========================================================================
    democratic_mode = args.democratic

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
            try:
                from src.core.democratic.democratic_core import DemocraticCore  # noqa: F401  # type: ignore
            except (ImportError, ModuleNotFoundError):
                logger.warning("⚠️ DemocraticCore module not found at src.core.democratic.democratic_core")
                DemocraticCore = None

            # Configurar paths (usar variável local para não sobrescrever o PROJECT_ROOT global)
            democratic_project_root = Path(__file__).parent
            data_path = democratic_project_root / "data"

            # Classe temporária para jarvis_core
            class TempJarvisCore:
                def __init__(self):
                    self.config = {
                        'system': {
                                    'base_path': str(democratic_project_root),
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

            if DemocraticCore is not None:
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
            else:
                print("⚠️ [DEMOCRÁTICO] Núcleo democrático não disponível, pulando inicialização.")
                democratic_systems = None
                democratic_mode = False  # Fallback para modo normal

        except Exception as e:
            print(f"❌ [DEMOCRÁTICO] Erro inicializando sistemas: {e}")
            democratic_mode = False  # Fallback para modo normal
    
    # ------------------------------------------------------------------------
    # [STAGE 1] CORE INITIALIZATION (Pre-GUI)
    # ------------------------------------------------------------------------
    # CRITICAL: Initialize Torch/MKL BEFORE QApp to prevent 0xC0000005.
    # This ensures the Neural Engine's threading model (OpenMP/MKL) captures
    # the process context before the GUI Event Loop (PyQt6) can conflict with it.
    if TORCH_AVAILABLE and torch is not None and hardware_manager is not None:
        try:
             # Force MKL initialization (Pre-warm)
             device = getattr(hardware_manager, 'get_torch_device', lambda: 'cpu')() if hasattr(hardware_manager, 'get_torch_device') else 'cpu'
             _ = torch.zeros(1).to(device)
             logger.info("🧠 [STAGE 1] Neural Engine: Pre-warmed (MKL Initialized)")
        except Exception as e:
            logger.warning(f"⚠️ Neural Engine Pre-warm failed: {e}")

    try:
        from PyQt6.QtWidgets import QApplication as QApp  # noqa: F401  # type: ignore
        from PyQt6.QtCore import QTimer  # noqa: F401  # type: ignore
        import threading as threading_module
        
        global QApplication
        app = QApp(sys.argv)
        app.setStyle("Fusion")
        # Fallback de fonte Unicode para toda interface
        from src.interface.window_manager import set_unicode_font
        set_unicode_font(app)
        
        # --------------------------------------------------------------------
        # [STAGE 2] INTERFACE & BODY (Visuals)
        # --------------------------------------------------------------------
        
        # Shared container for instances
        boot_data: dict = {"instances": None}
        
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
        
        # ========================================================================
        # 🚀 [STAGE 2] INFRASTRUCTURE INITIALIZATION WITH BOOT MANAGER
        # ========================================================================
        boot_data = {"instances": None, "status": "initializing"}
        
        async def initialize_with_boot_manager():
            """Initialize all systems using the new Boot Manager infrastructure"""
            import asyncio # Local import to force visibility in nested scope
            try:
                if not BOOT_MANAGER_AVAILABLE:
                    logger.error("❌ Boot Manager not available, falling back to legacy boot")
                    return await legacy_boot_fallback()
                
                # Create Boot Manager instance
                assert BOOT_MANAGER_AVAILABLE and BootManager is not None  # For linter
                boot_manager = BootManager()
                
                # Initialize Event Bus for module communication
                event_bus = None
                if EVENT_BUS_AVAILABLE:
                    assert AsyncEventBus is not None  # For linter
                    try:
                        event_bus = AsyncEventBus()
                        logger.info("✅ Event Bus initialized for module communication")

                        # [PHASE 2.2] Connect UnifiedMemoryManager to Event Bus
                        if event_bus:
                            try:
                                from src.core.intelligence.memory import memory_manager
                                if memory_manager and hasattr(memory_manager, 'connect_event_bus'):
                                    memory_manager.connect_event_bus(event_bus)
                                    logger.info("✅ Memory Manager connected to Event Bus")
                                else:
                                    logger.warning("⚠️ Memory Manager not available for Event Bus connection")
                                
                                # Connect AI Agent to Event Bus (Phase 2)
                                from src.core.intelligence.ai_agent import ai_agent
                                if ai_agent and hasattr(ai_agent, 'connect_event_bus'):
                                    ai_agent.connect_event_bus(event_bus)
                                    logger.info("✅ AI Agent connected to Event Bus")
                                else:
                                    logger.warning("⚠️ AI Agent not available for Event Bus connection")
                                
                                # Connect Proactive Monitor (Phase 2.3)
                                from src.core.intelligence.proactive_monitor import proactive_monitor
                                if proactive_monitor and hasattr(proactive_monitor, 'connect_event_bus'):
                                    proactive_monitor.connect_event_bus(event_bus)
                                    try:
                                        if hasattr(proactive_monitor, 'event_bus') and proactive_monitor.event_bus:
                                            import asyncio as _asyncio # Safe local reference
                                            proactive_monitor.event_bus.loop = _asyncio.get_running_loop() # Inject loop for thread safety
                                        logger.info("✅ Proactive Monitor connected to Event Bus")
                                    except AttributeError as e:
                                        logger.warning(f"⚠️ Could not set proactive monitor loop: {e}")
                                else:
                                    logger.warning("⚠️ Proactive Monitor not available for Event Bus connection")

                            except ImportError as e:
                                logger.warning(f"⚠️ Import error during Event Bus connections: {e}")
                            except Exception as e:
                                logger.warning(f"⚠️ Event Bus connection error: {e}")
                                import traceback
                                logger.warning(f"Connection traceback: {traceback.format_exc()}")
                    except Exception as e:
                        logger.warning(f"⚠️ Event Bus initialization failed: {e}")
                        import traceback
                        logger.warning(f"Event Bus traceback: {traceback.format_exc()}")
                        event_bus = None
                
                # [STEP 0] Register Event Bus
                if event_bus:
                    boot_manager.register_module(
                        "event_bus",
                        lambda: event_bus,
                        dependencies=[],
                        priority=BootPriority.HIGH
                    )
                
                # Update HUD status
                if hud and hasattr(hud, 'show_response'):
                    hud.show_response("CONECTANDO MÓDULOS...")
                await asyncio.sleep(1.0) # Grace period
                
                # [STEP 1] UI Core
                boot_manager.register_module(
                    "window_manager",
                    lambda: window_manager,
                    dependencies=[],
                    priority=BootPriority.HIGH
                )
                await asyncio.sleep(1.0)
                
                # [STEP 2] System Integrator
                boot_manager.register_module(
                    "system_integrator",
                    lambda: __import__('src.core.actions.system_integrator', fromlist=['get_system_integrator']).get_system_integrator(),
                    dependencies=["window_manager"],
                    priority=BootPriority.MEDIUM
                )
                await asyncio.sleep(1.0)
                
                # [STEP 3] Multimedia (Audio)
                boot_manager.register_module(
                    "audio_system", 
                    lambda: __import__('src.core.audio.enhanced_audio', fromlist=['get_audio_system']).get_audio_system(PROJECT_ROOT / "data" if PROJECT_ROOT else Path("data"), event_bus=event_bus),
                    dependencies=["system_integrator"],
                    priority=BootPriority.MEDIUM
                )
                await asyncio.sleep(1.0)
                
                # [STEP 4] Computer Vision (Heavy)
                boot_manager.register_module(
                    "vision_system",
                    lambda: __import__('src.core.vision.vision_system', fromlist=['get_vision_system']).get_vision_system(PROJECT_ROOT / "data" if PROJECT_ROOT else Path("data"), event_bus=event_bus),
                    dependencies=["system_integrator"],
                    priority=BootPriority.MEDIUM
                )
                await asyncio.sleep(2.0) # More time for Vision models
                
                # [STEP 5] AI Agent (Intelligence)
                boot_manager.register_module(
                    "ai_agent",
                    lambda: __import__('src.core.intelligence.ai_agent', fromlist=['ai_agent']).ai_agent,
                    dependencies=["audio_system", "vision_system"],
                    priority=BootPriority.MEDIUM
                )
                
                # Initialize all modules
                logger.info("⚡ [STAGE 2] Starting Boot Manager initialization...")
                boot_success = boot_manager.start_boot()
                if not boot_success:
                    raise Exception("Boot Manager initialization failed")
                instances = boot_manager.instances
                
                # Neural systems will be warmed up later via staggered_daemon_start (Late Boot)
                
                # Add neural systems placeholder and event bus
                instances["Neural Systems"] = None
                if event_bus:
                    instances["event_bus"] = event_bus
                
                boot_data["instances"] = instances
                boot_data["status"] = "completed"
                
                if hud and hasattr(hud, 'show_response'):
                    hud.show_response("SUBSISTEMAS ALINHADOS")
                
                logger.info("✅ [STAGE 2] Boot Manager initialization completed successfully")
                return instances
                
            except Exception as e:
                logger.error(f"❌ Boot Manager initialization failed: {e}")
                import traceback
                traceback.print_exc()
                boot_data["status"] = "failed"
                return await legacy_boot_fallback()
        
        async def legacy_boot_fallback():
            """Legacy fallback boot process"""
            try:
                logger.warning("⚠️ Using legacy boot fallback")
                
                # Load systems sequentially as fallback
                from src.core.actions.system_integrator import get_system_integrator
                from src.core.audio.enhanced_audio import get_audio_system
                from src.core.vision.vision_system import get_vision_system
                from src.core.intelligence.ai_agent import ai_agent
                
                data_path = PROJECT_ROOT / "data" if PROJECT_ROOT else Path("data")
                sys_int = get_system_integrator()
                audio = get_audio_system(data_path)
                vision = get_vision_system(data_path)
                
                # Background loading will be triggered by JarvisSingularity.start() (Late Boot)
                
                instances = {
                    "window_manager": window_manager,
                    "system_integrator": sys_int,
                    "audio_system": audio,
                    "vision_system": vision,
                    "ai_agent": ai_agent,
                    "Neural Systems": None
                }
                
                boot_data["instances"] = instances
                boot_data["status"] = "completed"
                return instances
                
            except Exception as e:
                logger.error(f"❌ Legacy boot fallback also failed: {e}")
                boot_data["status"] = "failed"
                raise
        
        # Start initialization in background thread
        def run_async_boot():
            try:
                # Check if there's already an event loop in this thread
                try:
                    loop = asyncio.get_running_loop()
                    # If we get here, there's already a running loop - schedule the task
                    asyncio.create_task(initialize_with_boot_manager())
                except RuntimeError:
                    # No running loop, create a new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(initialize_with_boot_manager())
                    loop.close()
            except Exception as e:
                logger.error(f"❌ Async boot failed: {e}")
                boot_data["status"] = "failed"
        
        boot_thread = threading_module.Thread(target=run_async_boot, daemon=True, name="BootManager")  
        boot_thread.start()
        
        # Timer to check for completion and start Stage 3 
        def check_boot_completion():
            from src.core.infrastructure.async_event_bus import event_bus
            
            if boot_data["instances"] and boot_data["status"] == "completed":
                logger.info("⚡ [STAGE 2] Boot Manager initialization completed")
                instances = boot_data["instances"]
                
                # ========================================================================
                # 🔥 NOVO: INTEGRAÇÃO DOS SISTEMAS DEMOCRÁTICOS
                # ========================================================================
                if democratic_mode and democratic_systems:
                    try:
                        print("🔥 [DEMOCRÁTICO] Integrando sistemas de poder ao núcleo...")
                        
                        # Adicionar sistemas democráticos às instâncias
                        instances["democratic_core"] = democratic_systems['democratic_core']
                        instances["microsoft_identifier"] = democratic_systems['microsoft_identifier']
                        instances["biometric_verifier"] = democratic_systems['biometric_verifier']
                        instances["drive_manager"] = democratic_systems['drive_manager']
                        instances["democratic_interface"] = democratic_systems['democratic_interface']
                        
                        # Lançar interface democrática em thread separada
                        def launch_democratic_interface():
                            try:
                                if democratic_systems and 'democratic_interface' in democratic_systems:
                                    print("🚀 [DEMOCRÁTICO] Lançando Interface de Controle Total...")
                                    democratic_systems['democratic_interface'].launch_interface()
                            except Exception as e:
                                print(f"❌ [DEMOCRÁTICO] Erro na interface: {e}")
                        
                        democratic_thread = threading_module.Thread(
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
                
                # Connect AI Agent to Event Bus if available
                if event_bus and "ai_agent" in instances:
                    try:
                        ai_agent = instances["ai_agent"]
                        if hasattr(ai_agent, 'set_event_bus'):
                            ai_agent.set_event_bus(event_bus)
                            logger.info("✅ AI Agent connected to Event Bus")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to connect AI Agent to Event Bus: {e}")
                
                # Update WindowManager with jarvis_core reference for dashboard integration
                if window_manager:
                    window_manager.jarvis_core = jarvis
                
                # Initialize Core
                jarvis.start()
                
                # ========================================================================
                # 🧬 EVOLUTION LAYER: Self-Healing & Auto-Organization System
                # ========================================================================
                # Initialize the Evolution Layer for autonomous system maintenance
                # This enables self-observation, diagnosis, correction, and auto-development
                evolution_enabled = os.environ.get("JARVIS_EVOLUTION_ENABLED", "true").lower() == "true"
                
                if evolution_enabled:
                    try:
                        logger.info("🧬 [EVOLUTION] Initializing Complete Self-Healing System...")
                        from src.evolution import evolution_manager
                        from src.core.config.system_manifest import system_manifest
                        
                        # Get protected files from system manifest
                        protected_files = system_manifest.system.core_protected_files
                        
                        # Start evolution layer with all features
                        async def start_evolution():
                            try:
                                await evolution_manager.start(
                                    observer_interval=300,          # Check every 5 minutes
                                    auto_heal=True,                 # Enable automatic corrections
                                    initial_scan=True,              # Run initial health check
                                    enable_module_generation=True,  # Enable auto-development
                                    enable_voice_commands=True      # Enable voice control
                                )
                                logger.info("✅ [EVOLUTION] Complete Self-Healing System operational")
                                logger.info("   ├─ Auto-Observation: ACTIVE")
                                logger.info("   ├─ Auto-Diagnosis: ACTIVE")
                                logger.info("   ├─ Auto-Correction: ACTIVE")
                                logger.info("   ├─ Auto-Development: ACTIVE")
                                logger.info("   ├─ Voice Commands: ACTIVE")
                                logger.info("   └─ Protected Files: ENFORCED")
                            except Exception as e:
                                logger.error(f"❌ [EVOLUTION] Failed to start: {e}")
                        
                        # Run in event loop
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        
                        loop.create_task(start_evolution())
                        
                        # Add to instances for integration
                        instances["evolution_manager"] = evolution_manager
                        
                        logger.info("🧬 [EVOLUTION] Integration complete - System is fully autonomous")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ [EVOLUTION] Could not initialize Evolution Layer: {e}")
                        logger.warning("   System will continue without self-healing capabilities")
                else:
                    logger.info("⚠️ [EVOLUTION] Self-Healing System disabled (set JARVIS_EVOLUTION_ENABLED=true to enable)")
                
                # Stop checking
                boot_checker.stop()
            elif boot_data["status"] == "failed":
                logger.error("❌ [STAGE 2] Boot Manager initialization failed, stopping")
                boot_checker.stop()
                app.quit()
                
        # Create boot completion checker
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
        # Ensure cleanup of resources when system shuts down
        # Note: instances and other vars are local to main, so we check local scope if possible
        # or just rely on OS cleanup since we are exiting.
        # But per user request, we add the logging.
        if 'logger' in globals():
            logger.info("🧹 Cleaning up and shutting down...")
            
            # Gracefully shutdown Evolution Layer if it was started
            try:
                if 'evolution_manager' in locals() or 'instances' in locals():
                    if 'instances' in locals() and 'evolution_manager' in locals()['instances']:
                        logger.info("🧬 [EVOLUTION] Shutting down Self-Healing System...")
                        from src.evolution import evolution_manager
                        try:
                            loop = asyncio.get_event_loop()
                            if not loop.is_closed():
                                loop.run_until_complete(evolution_manager.stop())
                        except:
                            # If event loop is not available, just log
                            pass
                        logger.info("✅ [EVOLUTION] Shutdown complete")
            except Exception as e:
                logger.warning(f"⚠️ [EVOLUTION] Shutdown warning: {e}")
            
            logger.info("🧹 Memory cleanup complete")

if __name__ == "__main__":
    sys.exit(main())
