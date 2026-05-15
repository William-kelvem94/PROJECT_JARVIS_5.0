"""
JARVIS 5.0 - Brain Module
Fachada para os módulos de raciocínio e LLM.

Uso:
    from app.brain import brain, EngineerBrain
    from app.brain import SmartRouter, router
    from app.brain import AutonomousBrain, autonomous_brain
    from app.brain import NativeBrain, get_native_brain
"""
# Re-exports from original locations (backward compatible)
from app.engineer_brain import brain, EngineerBrain          # noqa: F401
from app.smart_router import SmartRouter, router             # noqa: F401
from app.autonomous_brain import AutonomousBrain, autonomous_brain  # noqa: F401
from app.native_brain import NativeBrain, get_native_brain   # noqa: F401

__all__ = [
    # engineer_brain
    "brain", "EngineerBrain",
    # smart_router
    "SmartRouter", "router",
    # autonomous_brain
    "AutonomousBrain", "autonomous_brain",
    # native_brain
    "NativeBrain", "get_native_brain",
]
