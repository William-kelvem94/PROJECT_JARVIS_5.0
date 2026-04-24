"""
Backward-compatible import path for SystemController.

Legacy modules/tests import `src.core.system_controller`.
Canonical implementation lives in `src.core.actions.system_controller`.
"""

from src.core.actions.system_controller import SystemController, system_controller

__all__ = ["SystemController", "system_controller"]
