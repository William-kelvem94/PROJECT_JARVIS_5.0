"""Compatibility shim: expose `code_generator` at `src.core.code_generator`.
Re-exports the instance from `src.core.engine.code_generator`.
"""
from src.core.engine.code_generator import code_generator

__all__ = ["code_generator"]
