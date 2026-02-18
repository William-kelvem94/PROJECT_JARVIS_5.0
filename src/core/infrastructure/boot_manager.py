#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Boot Manager (Sistema de Inicialização Robusto)
============================================================
FASE 1.1: Resolve o problema crítico de ui_signals e organiza todo o boot process.

Responsibilities:
- Inicialização sequencial ordenada e tolerante a falhas
- Gerenciamento de dependências entre módulos
- Recovery automático de falhas de boot
- Integração com System Manifest para configurações
- Logging estruturado do processo de boot

Philosophy:
- Fail-fast com recovery inteligente
- Dependências explícitas e resolvidas em ordem
- Estado observável e diagnosticável
- Zero dependências circulares
"""

import logging
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import sys

logger = logging.getLogger(__name__)


class BootStage(Enum):
    """Estágios do processo de boot"""

    INITIALIZING = "initializing"
    PRE_GUI = "pre_gui"
    GUI_INIT = "gui_init"
    CORE_SYSTEMS = "core_systems"
    HEAVY_SYSTEMS = "heavy_systems"
    POST_INIT = "post_init"
    READY = "ready"
    FAILED = "failed"


class BootPriority(Enum):
    """Prioridades de inicialização"""

    CRITICAL = 0  # Deve inicializar primeiro (configurações, logging)
    HIGH = 1  # GUI, sinais, dependências críticas
    MEDIUM = 2  # Sistemas core (IA, visão, áudio)
    LOW = 3  # Sistemas auxiliares
    BACKGROUND = 4  # Sistemas que podem inicializar depois


@dataclass
class BootModule:
    """Definição de um módulo para inicialização"""

    name: str
    initializer: Callable[[], Any]
    priority: BootPriority
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    required: bool = True
    retry_count: int = 3
    instance: Optional[Any] = None
    initialized: bool = False
    error: Optional[Exception] = None
    init_time: Optional[float] = None


@dataclass
class BootProgress:
    """Estado do progresso de boot"""

    stage: BootStage = BootStage.INITIALIZING
    completed_modules: List[str] = field(default_factory=list)
    failed_modules: List[str] = field(default_factory=list)
    current_module: Optional[str] = None
    progress_percent: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None


class BootManager:
    """
    Gerenciador de Boot Robusto para JARVIS 5.0

    Gerencia todo o processo de inicialização de forma ordenada, tolerante a falhas,
    e com recovery automático. Resolve o problema de ui_signals e outros imports.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.modules: Dict[str, BootModule] = {}
        self.instances: Dict[str, Any] = {}
        self.progress = BootProgress()

        # Configuração básica
        self.project_root = self._discover_project_root()
        self.max_parallel_init = 2
        self.boot_timeout = 300  # 5 minutes total timeout

        # Event callbacks
        self.progress_callbacks: List[Callable[[BootProgress], None]] = []
        self.completion_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # Internal state
        self._boot_thread = None
        self._boot_complete = False
        self._shutdown_event = threading.Event()

        self._setup_core_modules()
        self._initialized = True

        logger.info("🔥 Boot Manager initialized")

    def _discover_project_root(self) -> Path:
        """Discover project root directory"""
        current = Path(__file__).resolve()

        # Look for main.py or other markers
        for parent in current.parents:
            if (parent / "main.py").exists() or (parent / "jarvis.bat").exists():
                return parent

        # Fallback
        return current.parent.parent.parent

    def _setup_core_modules(self):
        """Setup core modules for initialization"""

        # Critical modules (must initialize first)
        self.register_module(
            "system_manifest",
            self._init_system_manifest,
            BootPriority.CRITICAL,
            required=True,
            timeout_seconds=10,
        )

        self.register_module(
            "async_event_bus",
            self._init_async_event_bus,
            BootPriority.CRITICAL,
            dependencies=["system_manifest"],
            required=True,
            timeout_seconds=5,
        )

        self.register_module(
            "priority_scheduler",
            self._init_priority_scheduler,
            BootPriority.CRITICAL,
            dependencies=["async_event_bus"],
            required=True,
            timeout_seconds=10,
        )

        self.register_module(
            "blackbox_logger",
            self._init_blackbox_logger,
            BootPriority.CRITICAL,
            dependencies=["system_manifest", "async_event_bus"],
            required=True,
            timeout_seconds=10,
        )

        # GUI and signals (high priority)
        self.register_module(
            "qt_application",
            self._init_qt_application,
            BootPriority.HIGH,
            dependencies=["system_manifest"],
            required=True,
            timeout_seconds=15,
        )

        self.register_module(
            "ui_signals",
            self._init_ui_signals,
            BootPriority.HIGH,
            dependencies=["qt_application"],
            required=True,
            timeout_seconds=5,
        )

        self.register_module(
            "window_manager",
            self._init_window_manager,
            BootPriority.HIGH,
            dependencies=["qt_application", "ui_signals"],
            required=False,  # Nao bloqueia boot em modo headless
            timeout_seconds=15,
        )

        # Core systems (medium priority)
        self.register_module(
            "system_integrator",
            self._init_system_integrator,
            BootPriority.MEDIUM,
            dependencies=["ui_signals"],
            required=False,  # Nao bloqueia boot se falhar
            timeout_seconds=20,
        )

        self.register_module(
            "ai_agent",
            self._init_ai_agent,
            BootPriority.MEDIUM,
            dependencies=["system_integrator"],
            required=True,
            timeout_seconds=90,  # ai_agent demora ~25s para carregar todos os modulos
        )

        # Heavy systems (can be initialized in background)
        self.register_module(
            "audio_system",
            self._init_audio_system,
            BootPriority.LOW,
            dependencies=["system_integrator", "ui_signals"],
            required=False,
            timeout_seconds=45,
        )

        self.register_module(
            "vision_system",
            self._init_vision_system,
            BootPriority.LOW,
            dependencies=["system_integrator", "ui_signals"],
            required=False,
            timeout_seconds=45,
        )

        # Background systems
        self.register_module(
            "network_mesh",
            self._init_network_mesh,
            BootPriority.BACKGROUND,
            dependencies=["system_manifest"],
            required=False,
            timeout_seconds=30,
        )

        # self.register_module(
        #     "watchdog_supervisor",
        #     self._init_watchdog_supervisor,
        #     BootPriority.BACKGROUND,
        #     dependencies=["system_manifest", "priority_scheduler"],
        #     required=False,
        #     timeout_seconds=10,
        # )

    def register_module(
        self,
        name: str,
        initializer: Callable[[], Any],
        priority: BootPriority,
        dependencies: Optional[List[str]] = None,
        required: bool = True,
        timeout_seconds: int = 30,
        retry_count: int = 3,
    ):
        """Register a module for initialization"""
        self.modules[name] = BootModule(
            name=name,
            initializer=initializer,
            priority=priority,
            dependencies=dependencies or [],
            timeout_seconds=timeout_seconds,
            required=required,
            retry_count=retry_count,
        )

        logger.debug(f"📝 Registered boot module: {name} (priority={priority.name})")

    def add_progress_callback(self, callback: Callable[[BootProgress], None]):
        """Add callback for progress updates"""
        self.progress_callbacks.append(callback)

    def add_completion_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for boot completion"""
        self.completion_callbacks.append(callback)

    def start_boot(self, blocking: bool = True) -> bool:
        """Start the boot process"""
        if self._boot_complete:
            logger.warning("Boot sequence already completed - skipping redundant start")
            return True

        if self._boot_thread and self._boot_thread.is_alive():
            logger.warning("Boot process already running")
            return False

        logger.info("🚀 Starting JARVIS 5.0 boot sequence...")
        self.progress.start_time = datetime.now()
        self.progress.stage = BootStage.INITIALIZING

        if blocking:
            return self._execute_boot()
        else:
            self._boot_thread = threading.Thread(
                target=self._execute_boot, daemon=False, name="BootManager"
            )
            self._boot_thread.start()
            return True

    def _execute_boot(self) -> bool:
        """Execute boot sequence"""
        try:
            start_time = time.time()

            # Get modules sorted by priority and dependencies
            ordered_modules = self._resolve_dependencies()

            logger.info(
                f"🔄 Boot sequence: {len(ordered_modules)} modules to initialize"
            )

            # Initialize modules in order
            for i, module in enumerate(ordered_modules):
                if self._shutdown_event.is_set():
                    logger.info("🛑 Boot interrupted by shutdown")
                    return False

                # Update progress
                self.progress.current_module = module.name
                self.progress.progress_percent = int((i / len(ordered_modules)) * 100)
                self._notify_progress()

                # Initialize module
                success = self._initialize_module(module)

                if success:
                    self.progress.completed_modules.append(module.name)

                    # Store instance
                    self.instances[module.name] = module.instance

                    # Auto-connect EventBus to modules that implement
                    # connect_event_bus
                    try:
                        event_bus = self.instances.get("async_event_bus")
                        if event_bus and hasattr(module.instance, "connect_event_bus"):
                            try:
                                module.instance.connect_event_bus(event_bus)
                                logger.debug(f"🔌 Connected event bus to {module.name}")
                            except Exception as e:
                                logger.warning(
                                    f"Failed to connect event bus to {module.name}: {e}"
                                )
                    except Exception:
                        pass

                    logger.info(
                        f"✅ {module.name} initialized ({module.init_time:.2f}s)"
                    )
                else:
                    self.progress.failed_modules.append(module.name)
                    if module.required:
                        logger.critical(
                            f"❌ Critical module {module.name} failed - aborting boot"
                        )
                        self.progress.stage = BootStage.FAILED
                        self._notify_progress()
                        return False
                    else:
                        logger.warning(
                            f"⚠️ Optional module {module.name} failed - continuing"
                        )

            # Boot completed successfully
            boot_time = time.time() - start_time
            self.progress.stage = BootStage.READY
            self.progress.progress_percent = 100
            self.progress.current_module = None

            logger.info(
                f"🎉 JARVIS 5.0 boot completed successfully in {boot_time:.2f}s"
            )
            self._boot_complete = True

            # Notify callbacks
            self._notify_progress()
            self._notify_completion()

            return True

        except Exception as e:
            logger.critical(f"💥 Boot process failed critically: {e}")
            self.progress.stage = BootStage.FAILED
            self._notify_progress()
            return False

    def _resolve_dependencies(self) -> List[BootModule]:
        """Resolve module dependencies and return ordered list"""
        # Sort by priority first
        modules = sorted(self.modules.values(), key=lambda m: m.priority.value)

        # Simple dependency resolution (can be improved with topological sort)
        ordered = []
        remaining = {m.name: m for m in modules}

        while remaining:
            # Find modules with no unmet dependencies
            ready = []
            for name, module in remaining.items():
                deps_met = all(
                    dep in [m.name for m in ordered] for dep in module.dependencies
                )
                if deps_met:
                    ready.append(module)

            if not ready:
                # Circular dependency or missing dependency
                logger.error(
                    f"❌ Dependency resolution failed. Remaining: {list(remaining.keys())}"
                )
                # Add remaining modules anyway (best effort)
                ordered.extend(remaining.values())
                break

            # Sort ready modules by priority and add to ordered list
            ready.sort(key=lambda m: m.priority.value)
            ordered.extend(ready)

            # Remove from remaining
            for module in ready:
                remaining.pop(module.name)

        return ordered

    def _initialize_module(self, module: BootModule) -> bool:
        """Initialize a single module with retry logic"""
        for attempt in range(module.retry_count):
            try:
                logger.debug(f"🔄 Initializing {module.name} (attempt {attempt + 1})")

                start_time = time.time()

                # Execute initializer with timeout
                instance = module.initializer()

                # Store results
                module.instance = instance
                module.initialized = True
                module.init_time = time.time() - start_time

                return True

            except Exception as e:
                module.error = e
                logger.warning(
                    f"⚠️ {module.name} initialization failed (attempt {attempt + 1}): {e}"
                )

                if attempt < module.retry_count - 1:
                    time.sleep(1)  # Brief delay before retry

        return False

    def _notify_progress(self):
        """Notify progress callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")

    def _notify_completion(self):
        """Notify completion callbacks"""
        for callback in self.completion_callbacks:
            try:
                callback(self.instances)
            except Exception as e:
                logger.error(f"Completion callback failed: {e}")

    def get_instance(self, name: str) -> Optional[Any]:
        """Get initialized instance by name"""
        return self.instances.get(name)

    def get_all_instances(self) -> Dict[str, Any]:
        """Get all initialized instances"""
        return self.instances.copy()

    def is_ready(self) -> bool:
        """Check if boot process is complete"""
        return self.progress.stage == BootStage.READY

    def shutdown(self):
        """Shutdown boot manager"""
        logger.info("🔽 Boot Manager shutting down...")
        self._shutdown_event.set()

        if self._boot_thread and self._boot_thread.is_alive():
            self._boot_thread.join(timeout=5)

        logger.info("✅ Boot Manager shutdown complete")

    # ========================================================================
    # MODULE INITIALIZERS
    # ========================================================================

    def _init_system_manifest(self) -> Any:
        """Initialize system manifest"""
        try:
            from src.core.config.system_manifest import system_manifest

            return system_manifest
        except ImportError as e:
            logger.error(f"Failed to import system manifest: {e}")
            raise

    def _init_blackbox_logger(self) -> Any:
        """Initialize blackbox logger"""
        try:
            from src.core.config.blackbox_logger import (
                blackbox_logger,
                setup_blackbox_integration,
            )

            setup_blackbox_integration()
            return blackbox_logger
        except ImportError as e:
            logger.error(f"Failed to import blackbox logger: {e}")
            raise

    def _init_qt_application(self) -> Any:
        """Initialize Qt application"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer

            # Check if QApplication already exists
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
                app.setStyle("Fusion")

                # Set unicode font
                try:
                    from src.interface.window_manager import set_unicode_font

                    set_unicode_font(app)
                except ImportError:
                    pass

            return app
        except ImportError as e:
            logger.error(f"Failed to initialize Qt application: {e}")
            raise

    def _init_ui_signals(self) -> Any:
        """Initialize UI signals - CRITICAL FIX"""
        try:
            from src.interface.ui_signals import ui_signals

            logger.info("✅ ui_signals initialized successfully")
            return ui_signals
        except ImportError as e:
            logger.error(f"❌ Failed to initialize ui_signals: {e}")
            raise

    def _init_window_manager(self) -> Any:
        """Initialize window manager"""
        try:
            from src.interface.window_manager import get_window_manager, InterfaceMode

            app = self.get_instance("qt_application")
            if app is None:
                raise RuntimeError("Qt application not initialized")

            window_manager = get_window_manager(app)

            # Show HUD immediately
            window_manager.switch_mode(InterfaceMode.HUD_OVERLAY)

            return window_manager
        except ImportError as e:
            logger.error(f"Failed to initialize window manager: {e}")
            raise

    def _init_system_integrator(self) -> Any:
        """Initialize system integrator"""
        try:
            from src.core.actions.system_integrator import get_system_integrator

            return get_system_integrator()
        except ImportError as e:
            logger.error(f"Failed to initialize system integrator: {e}")
            raise

    def _init_ai_agent(self) -> Any:
        """Initialize AI agent (defensive import to avoid intermittent NameError for decorators)

        Some modules occasionally raise "name 'safe_execute' is not defined" during
        import due to import-order races. Retry once and preload `safe_execute` if
        that specific NameError occurs.
        """
        for attempt in range(2):
            try:
                from src.core.intelligence.ai_agent import ai_agent

                return ai_agent
            except Exception as e:
                # If the failure looks like the historical `safe_execute` NameError,
                # try preloading the safe_execute utilities and retry once.
                if "safe_execute" in str(e):
                    try:
                        from src.utils.safe_execute import safe_execute, safe_context  # noqa: F401
                        logger.warning(
                            "Preloaded src.utils.safe_execute to mitigate import race"
                        )
                    except Exception as _ie:
                        logger.warning(f"Preload of safe_execute failed: {_ie}")

                logger.error(f"Failed to initialize AI agent (attempt {attempt+1}): {e}")
                time.sleep(0.5)

        # If we get here, re-raise the last exception to surface the root cause
        raise RuntimeError("AI agent initialization failed after retries")

    def _init_audio_system(self) -> Any:
        """Initialize audio system"""
        try:
            from src.core.audio.enhanced_audio import get_audio_system

            audio = get_audio_system(self.project_root / "data")

            # Start background loading
            if hasattr(audio, "start_background_loading"):
                audio.start_background_loading()

            return audio
        except ImportError as e:
            logger.warning(f"Audio system not available: {e}")
            return None

    def _init_vision_system(self) -> Any:
        """Initialize vision system"""
        try:
            from src.core.vision.vision_system import get_vision_system

            vision = get_vision_system(self.project_root / "data")

            # Start background loading
            if hasattr(vision, "start_background_loading"):
                vision.start_background_loading()

            return vision
        except ImportError as e:
            logger.warning(f"Vision system not available: {e}")
            return None

    def _init_network_mesh(self) -> Any:
        """Initialize network mesh"""
        try:
            # Check if network mesh is enabled
            system_manifest = self.get_instance("system_manifest")
            if system_manifest and system_manifest.network.enabled:
                from src.core.network_mesh.local_network_intelligence import (
                    LocalNetworkIntelligence,
                )

                return LocalNetworkIntelligence(str(self.project_root))
            else:
                logger.info("Network mesh disabled in configuration")
                return None
        except ImportError as e:
            logger.warning(f"Network mesh not available: {e}")
            return None

    def _init_async_event_bus(self) -> Any:
        """Initialize unified async event bus"""
        try:
            from src.core.infrastructure.async_event_bus import get_event_bus

            bus = get_event_bus()
            # Ensure the EventBus is started early so subscribers/publishers and
            # the Watchdog heartbeat are active immediately. Start in the
            # running asyncio loop if available; otherwise spawn a background
            # thread to run the bus.start() coroutine.
            import asyncio
            import threading

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(bus.start())
                else:

                    def _bg_start():
                        try:
                            import asyncio as _asyncio

                            _asyncio.run(bus.start())
                        except Exception as _e:
                            logger.warning(f"Background event bus start failed: {_e}")

                    threading.Thread(target=_bg_start, daemon=True).start()
            except Exception as _e:
                logger.warning(f"Could not auto-start event bus: {_e}")

            return bus
        except ImportError as e:
            logger.error(f"Failed to import async event bus: {e}")
            raise

    def _init_priority_scheduler(self) -> Any:
        """Initialize priority scheduler (The Maestro)"""
        try:
            from src.core.infrastructure.priority_scheduler import (
                get_priority_scheduler,
            )

            scheduler = get_priority_scheduler()
            # Start scheduler immediately
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(scheduler.start())

            return scheduler
        except ImportError as e:
            logger.error(f"Failed to import priority scheduler: {e}")
            raise

    def _init_watchdog_supervisor(self) -> Any:
        """Initialize watchdog supervisor"""
        try:
            from src.core.infrastructure.watchdog import watchdog_system

            # Register core components
            watchdog_system.register_component(
                "priority_scheduler", heartbeat_interval=2.0
            )
            # Give the EventBus a larger heartbeat window to tolerate heavy-load
            # spikes during startup and long-running DreamCycle activity.
            watchdog_system.register_component("event_bus", heartbeat_interval=10.0)

            # Start monitoring thread
            watchdog_system.start()

            return watchdog_system
        except ImportError as e:
            logger.error(f"Failed to import watchdog system: {e}")
            raise
        except Exception as e:
            logger.warning(f"Watchdog supervisor initialization failed: {e}")
            return None


# Global instance
boot_manager = BootManager()

if __name__ == "__main__":
    # Test boot manager
    print("🧪 Testing Boot Manager")
    print("=" * 50)

    def progress_callback(progress: BootProgress):
        print(
            f"Progress: {progress.stage.value} - {progress.current_module} ({progress.progress_percent}%)"
        )

    def completion_callback(instances: Dict[str, Any]):
        print(f"Boot completed! Instances: {list(instances.keys())}")

    boot_manager.add_progress_callback(progress_callback)
    boot_manager.add_completion_callback(completion_callback)

    success = boot_manager.start_boot(blocking=True)
    print(f"Boot result: {'SUCCESS' if success else 'FAILED'}")
