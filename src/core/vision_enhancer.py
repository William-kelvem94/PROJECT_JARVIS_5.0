"""Compatibility shim: expose `vision_enhancer` at `src.core.vision_enhancer`.
Re-exports the instance from `src.core.vision.vision_enhancer`.
"""
from src.core.vision.vision_enhancer import vision_enhancer

__all__ = ["vision_enhancer"]
