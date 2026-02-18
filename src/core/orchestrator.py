"""Compatibility shim for legacy imports.

Some older tests and modules import `src.core.orchestrator` — the real
implementation lives in `src.core.management.orchestrator`. Export the
primary classes and common names here to maintain backward compatibility.
"""

from src.core.management.orchestrator import StarkOrchestrator
from src.core.security.security_manager import SecurityManager
from src.core.iot.iot_manager import IOTManager
from src.core.management.fallback_system import FallbackSystem

import logging
import importlib

logger = logging.getLogger(__name__)

# Mirror common attributes into the original management module in a
# runtime-forwarding way so tests that patch `src.core.orchestrator` still
# influence `src.core.management.orchestrator` (the tests often patch the
# shim, not the implementation module). We create small factories / proxies
# on the management module that delegate back to this shim at call-time.
try:
    _mgmt_mod = importlib.import_module("src.core.management.orchestrator")

    # factories resolve the current symbol from this shim module at call-time
    def _make_factory(attr_name):
        def _factory(*args, **kwargs):
            import importlib as _il

            shim = _il.import_module(__name__)
            cls = getattr(shim, attr_name)
            return cls(*args, **kwargs)

        return _factory

    setattr(_mgmt_mod, "FallbackSystem", _make_factory("FallbackSystem"))
    setattr(_mgmt_mod, "SecurityManager", _make_factory("SecurityManager"))
    setattr(_mgmt_mod, "IOTManager", _make_factory("IOTManager"))

    # logger proxy forwards calls to the logger object in this shim so tests
    # that patch `src.core.orchestrator.logger` are respected by the
    # management.orchestrator implementation.
    class _LoggerProxy:
        def __getattr__(self, item):
            return getattr(logger, item)

    setattr(_mgmt_mod, "logger", _LoggerProxy())
except Exception:
    # best-effort only — do not fail import if the management module is
    # unavailable in some test environments
    pass

__all__ = [
    "StarkOrchestrator",
    "SecurityManager",
    "IOTManager",
    "FallbackSystem",
    "logger",
]
