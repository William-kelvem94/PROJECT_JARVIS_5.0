"""Compatibility shim: expose `performance_optimizer` at `src.core.performance_optimizer`.
Re-exports the instance from `src.core.management.performance_optimizer`.
"""
from src.core.management.performance_optimizer import performance_optimizer

__all__ = ["performance_optimizer"]
