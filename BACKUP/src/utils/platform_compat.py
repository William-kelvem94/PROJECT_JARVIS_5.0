#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Cross-Platform Compatibility Utilities
===================================================
Provides graceful fallbacks for platform-specific imports.

Author: JARVIS 5.0 Core Team
"""

import platform
import logging

logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

# ============================================================================
# Windows-specific imports
# ============================================================================

# winreg
try:
    if IS_WINDOWS:
        import winreg

        WINREG_AVAILABLE = True
    else:
        winreg = None
        WINREG_AVAILABLE = False
except ImportError:
    winreg = None
    WINREG_AVAILABLE = False
    if IS_WINDOWS:
        logger.warning("winreg not available on Windows")

# pywin32
try:
    if IS_WINDOWS:
        import win32api
        import win32con
        import win32gui
        import win32process
        import win32security
        import win32com.client

        PYWIN32_AVAILABLE = True
    else:
        win32api = None
        win32con = None
        win32gui = None
        win32process = None
        win32security = None
        PYWIN32_AVAILABLE = False
except ImportError:
    win32api = None
    win32con = None
    win32gui = None
    win32process = None
    win32security = None
    PYWIN32_AVAILABLE = False
    if IS_WINDOWS:
        logger.warning("pywin32 not available on Windows")

# wmi
try:
    if IS_WINDOWS:
        import wmi

        WMI_AVAILABLE = True
    else:
        wmi = None
        WMI_AVAILABLE = False
except ImportError:
    wmi = None
    WMI_AVAILABLE = False
    if IS_WINDOWS:
        logger.warning("wmi not available on Windows")

# pycaw (audio control)
try:
    if IS_WINDOWS:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL

        PYCAW_AVAILABLE = True
    else:
        AudioUtilities = None
        IAudioEndpointVolume = None
        CLSCTX_ALL = None
        PYCAW_AVAILABLE = False
except ImportError:
    AudioUtilities = None
    IAudioEndpointVolume = None
    CLSCTX_ALL = None
    PYCAW_AVAILABLE = False
    if IS_WINDOWS:
        logger.warning("pycaw not available on Windows")

# ctypes for Windows
try:
    if IS_WINDOWS:
        import ctypes
        from ctypes import cast, POINTER

        CTYPES_AVAILABLE = True
    else:
        ctypes = None
        CTYPES_AVAILABLE = False
except ImportError:
    ctypes = None
    CTYPES_AVAILABLE = False

# ============================================================================
# Helper functions
# ============================================================================


def require_windows(func):
    """Decorator that makes a function Windows-only"""

    def wrapper(*args, **kwargs):
        if not IS_WINDOWS:
            logger.warning(f"{func.__name__} is only available on Windows")
            return None
        return func(*args, **kwargs)

    return wrapper


def windows_or_fallback(fallback_value=None):
    """Decorator that returns fallback value on non-Windows systems"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not IS_WINDOWS:
                return fallback_value
            return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# Platform info
# ============================================================================


def get_platform_info():
    """Get detailed platform information"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX,
        "is_mac": IS_MAC,
        "winreg_available": WINREG_AVAILABLE,
        "pywin32_available": PYWIN32_AVAILABLE,
        "wmi_available": WMI_AVAILABLE,
        "pycaw_available": PYCAW_AVAILABLE,
        "ctypes_available": CTYPES_AVAILABLE,
    }


# Log platform info on import
if __name__ != "__main__":
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    if IS_WINDOWS:
        logger.info(
            f"Windows modules: winreg={WINREG_AVAILABLE}, pywin32={PYWIN32_AVAILABLE}, wmi={WMI_AVAILABLE}"
        )
    else:
        logger.info(
            f"Running on {platform.system()} - Windows-specific features disabled"
        )
