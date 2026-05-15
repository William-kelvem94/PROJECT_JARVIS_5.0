"""
JARVIS 5.0 - Memory Module
Fachada para o sistema de memória unificada.

Uso:
    from app.memory import memory
    from app.memory import UnifiedMemory
"""
# Re-exports from original locations (backward compatible)
from app.unified_memory import memory, UnifiedMemory          # noqa: F401

__all__ = ["memory", "UnifiedMemory"]
