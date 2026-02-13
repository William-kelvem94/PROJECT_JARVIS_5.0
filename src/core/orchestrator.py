"""Lightweight orchestrator stub to satisfy imports during tests and smoke
tests. Provides a minimal `StarkOrchestrator` class and placeholder
components that tests may patch.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SecurityManager:
    def __init__(self):
        logger.debug("SecurityManager initialized (stub)")


class IOTManager:
    def __init__(self):
        logger.debug("IOTManager initialized (stub)")


class FallbackSystem:
    def __init__(self):
        logger.debug("FallbackSystem initialized (stub)")


class StarkOrchestrator:
    """Minimal orchestrator used in tests and smoke runs.

    This stub keeps behavior deliberately small: it initializes placeholder
    subsystems and exposes a `start()` method.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.security = SecurityManager()
        self.iot = IOTManager()
        self.fallback = FallbackSystem()
        logger.info("StarkOrchestrator (stub) initialized")

    def start(self):
        logger.info("StarkOrchestrator (stub) started")

    def shutdown(self):
        logger.info("StarkOrchestrator (stub) shutdown")
