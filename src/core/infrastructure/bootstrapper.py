"""
JARVIS 5.0 - System Bootstrapper
================================
Encapsulates the system initialization logic, dependency injection,
and boot sequence management.
"""

import logging
from typing import Dict, Any

from src.core.config.system_manifest import system_manifest
from src.core.config.blackbox_logger import blackbox_logger, setup_blackbox_integration
from src.core.infrastructure.boot_manager import BootManager, BootPriority

logger = logging.getLogger("JARVIS-BOOTSTRAPPER")


class SystemBootstrapper:
    """
    Handles the initialization of all core components using the BootManager.
    Provides a unified interface for system startup.
    """

    def __init__(self, app_instance=None):
        self.app = app_instance
        self.boot_manager = BootManager()
        self.instances = {}
        self.event_bus = None

    async def bootstrap(self) -> Dict[str, Any]:
        """
        Runs the full boot sequence.

        Returns:
            Dict containing initialized instances (window_manager, ai_agent, etc.)

        Raises:
            RuntimeError: If critical components fail to load.
        """
        print("DEBUG: Entering bootstrap()")
        logger.info("🚀 Starting JARVIS System Bootstrap...")

        # 0. Initialize DNA (System Manifest & Blackbox Logger)
        print("DEBUG: Calling _init_foundation()")
        self._init_foundation()
        print("DEBUG: _init_foundation() done")

        # 1. Initialize Event Bus (Critical Infrastructure)
        print("DEBUG: Calling _init_event_bus()")
        await self._init_event_bus()
        print("DEBUG: _init_event_bus() done")

        # 2. Register Core Components
        print("DEBUG: Calling _register_components()")
        self._register_components()
        print("DEBUG: _register_components() done")

        # 3. Execute Boot Sequence
        print("DEBUG: Calling boot_manager.start_boot()")
        success = self.boot_manager.start_boot()
        print(f"DEBUG: start_boot() returned {success}")

        if not success:
            logger.critical("❌ Boot Sequence FAILED")
            raise RuntimeError("System failed to boot correctly.")

        self.instances = self.boot_manager.instances
        logger.info("✅ System Bootstrap COMPLETED successfully")

        return self.instances

    async def _init_event_bus(self):
        """Initializes the async event bus."""
        try:
            from src.core.infrastructure.async_event_bus import AsyncEventBus

            self.event_bus = AsyncEventBus()
            logger.info("✅ AsyncEventBus initialized")

            # Register immediately as it's a dependency for others
            self.boot_manager.register_module(
                "event_bus", lambda: self.event_bus, BootPriority.CRITICAL, []
            )
        except ImportError:
            logger.warning(
                "⚠️ AsyncEventBus not available. System using sync fallback."
            )

    def _register_components(self):
        """Registers all system components with the BootManager."""

        # Window Manager (GUI)
        if self.app:
            self.boot_manager.register_module(
                "window_manager", self._init_window_manager, BootPriority.HIGH, []
            )

        # System Integrator (Actions)
        self.boot_manager.register_module(
            "system_integrator",
            self._init_system_integrator,
            BootPriority.MEDIUM,
            ["window_manager"] if self.app else [],
        )

        # Audio System (optional - não bloqueia o boot)
        self.boot_manager.register_module(
            "audio_system",
            self._init_audio_system,
            BootPriority.LOW,
            ["system_integrator"],
            required=False,
            timeout_seconds=60,
        )

        # Vision System (optional - não bloqueia o boot)
        self.boot_manager.register_module(
            "vision_system",
            self._init_vision_system,
            BootPriority.LOW,
            ["system_integrator"],
            required=False,
            timeout_seconds=60,
        )

        # AI Agent (The Brain) - inicia independente de áudio/visão
        self.boot_manager.register_module(
            "ai_agent",
            self._init_ai_agent,
            BootPriority.MEDIUM,
            ["system_integrator"],  # Só depende do integrador, não de áudio/visão
            required=True,
            timeout_seconds=120,  # Aumentado para 120s para heavy loading
        )

    # --- Factory Methods (Lazy Loading) ---

    def _init_window_manager(self):
        if not self.app:
            return None
        try:
            from src.interface.window_manager import get_window_manager

            return get_window_manager(self.app)
        except ImportError as e:
            logger.error(f"Failed to load WindowManager: {e}")
            return None

    def _init_system_integrator(self):
        try:
            # Dynamic import to avoid circular deps
            from src.core.actions.system_integrator import get_system_integrator

            return get_system_integrator()
        except ImportError as e:
            logger.error(f"Failed to load SystemIntegrator: {e}")
            return None

    def _init_audio_system(self):
        try:
            from src.core.audio.enhanced_audio import get_audio_system

            return get_audio_system(
                system_manifest.paths["base"] / "data", event_bus=self.event_bus
            )
        except ImportError as e:
            logger.error(f"Failed to load AudioSystem: {e}")
            return None

    def _init_vision_system(self):
        try:
            from src.core.vision.vision_system import get_vision_system

            return get_vision_system(
                system_manifest.paths["base"] / "data", event_bus=self.event_bus
            )
        except ImportError as e:
            logger.error(f"Failed to load VisionSystem: {e}")
            return None

    def _init_ai_agent(self):
        try:
            from src.core.intelligence.ai_agent import ai_agent

            return ai_agent
        except ImportError as e:
            logger.error(f"Failed to load AI Agent: {e}")
            return None

    def _init_foundation(self):
        """Initializes the system's DNA (Manifest and Logging)"""
        try:
            # Manifest is already initialized as a global singleton, but we log
            # its status
            logger.info("📜 System Manifest (DNA) LOADED")

            # Setup Blackbox integration
            setup_blackbox_integration()
            blackbox_logger.info(
                "📦 Blackbox Logger ACTIVATED", component="bootstrapper"
            )

        except Exception as e:
            logger.error(f"Failed to initialize foundation: {e}")
