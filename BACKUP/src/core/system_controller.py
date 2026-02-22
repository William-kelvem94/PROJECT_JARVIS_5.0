"""Compatibility shim for legacy imports of system_controller.

Some modules/tests do `from src.core.system_controller import system_controller`.
The implementation actually lives in `src.core.actions.system_controller` —
forward the reference here.
"""

from src.core.actions.system_controller import system_controller, SystemController

__all__ = ["system_controller", "SystemController"]
