"""Compatibility shim: expose `system_controller` at `src.core.system_controller`.
This module re-exports the instance from `src.core.actions.system_controller` to
keep older import paths working for tests and external scripts.
"""
from src.core.actions.system_controller import system_controller

__all__ = ["system_controller"]
