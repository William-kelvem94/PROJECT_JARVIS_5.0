"""Backward-compatibility shim: expose `memory_manager` where tests expect it.

Tests may import `src.core.intelligence.memory_manager` — the real manager
lives under `src.core.intelligence.memory` (package). Re-export the
expected symbols here.
"""
from src.core.intelligence.memory import memory_manager, UnifiedMemoryManager

__all__ = ["memory_manager", "UnifiedMemoryManager"]