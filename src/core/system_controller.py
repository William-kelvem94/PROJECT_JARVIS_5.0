"""
Backward-compatible import path for SystemController.

Legacy modules/tests import `src.core.system_controller`.
This module provides a stub SystemController for backward compatibility.
"""

class SystemController:
    """Stub SystemController for backward compatibility."""
    def __init__(self):
        pass

    def get_status(self) -> dict:
        return {"status": "ok", "system": "JARVIS 5.0"}

system_controller = SystemController()

__all__ = ["SystemController", "system_controller"]
