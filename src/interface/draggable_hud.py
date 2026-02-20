"""Compatibility shim: provide `DraggableHUD` class for legacy imports.
This maps to `ModernHUD` implemented in `src.interface.modern_hud`.
"""

try:
    from src.interface.modern_hud import ModernHUD as DraggableHUD
except Exception:
    # Fallback minimal stub to avoid import errors in headless/test
    # environments
    class DraggableHUD:
        def __init__(self, *args, **kwargs):
            pass


__all__ = ["DraggableHUD"]
