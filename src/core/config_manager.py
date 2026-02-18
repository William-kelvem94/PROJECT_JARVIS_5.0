"""
Compatibility shim for ConfigManager

Some test modules and legacy code import `ConfigManager` from
`src.core.config_manager`. The canonical implementation lives in
`src/utils/config_manager.py`. This module re-exports that class and
singleton instance to preserve backward compatibility.
"""

from src.utils.config_manager import ConfigManager, config_manager

__all__ = ["ConfigManager", "config_manager"]
