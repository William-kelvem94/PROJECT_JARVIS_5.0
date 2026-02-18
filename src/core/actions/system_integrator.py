#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - System Integrator (God Mode)
==================================================
Deep Windows system control via native APIs.

Capabilities:
- Per-application volume control (pycaw)
- Process management (kill, list, monitor)
- Window manipulation (focus, minimize, close)
- System information (hardware, processes)
- Privileged operations

Philosophy:
- API/CLI first (fast, invisible, robust)
- Fallback to automation only when necessary
- Security: Audit log for privileged operations
"""

import sys
import subprocess
import logging
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# CONDITIONAL IMPORTS (Platform-specific)
# ============================================================================
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    logger.warning("âš ï¸ psutil not available - system monitoring disabled")

WINDOWS = sys.platform == "win32"

if WINDOWS:
    try:
        import win32gui
        import win32con
        import win32process
        import win32api
        import win32com.client

        PYWIN32_AVAILABLE = True
    except ImportError:
        PYWIN32_AVAILABLE = False
        logger.warning("âš ï¸ pywin32 not available - Windows API features disabled")

    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
        from comtypes import CLSCTX_ALL
        import comtypes

        PYCAW_AVAILABLE = True
    except ImportError:
        PYCAW_AVAILABLE = False
        logger.warning("âš ï¸ pycaw not available - audio control disabled")

    try:
        import wmi

        WMI_AVAILABLE = True
    except ImportError:
        WMI_AVAILABLE = False
        logger.warning("âš ï¸ WMI not available - advanced hardware features disabled")
else:
    PYWIN32_AVAILABLE = False
    PYCAW_AVAILABLE = False
    WMI_AVAILABLE = False
    logger.warning("âš ï¸ Non-Windows platform - God Mode features limited")


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class ProcessInfo:
    """Process information"""

    pid: int
    name: str
    exe: Optional[str]
    cpu_percent: float
    memory_mb: float
    status: str


@dataclass
class WindowInfo:
    """Window information"""

    hwnd: int
    title: str
    class_name: str
    pid: int
    is_visible: bool
    is_minimized: bool


class SystemOperation(Enum):
    """Types of system operations (for audit log)"""

    KILL_PROCESS = "kill_process"
    SET_VOLUME = "set_volume"
    CLOSE_WINDOW = "close_window"
    MINIMIZE_WINDOW = "minimize_window"
    FOCUS_WINDOW = "focus_window"
    SHELL_COMMAND = "shell_command"


# ============================================================================
# SYSTEM INTEGRATOR
# ============================================================================
class SystemIntegrator:
    """
    God Mode system controller for Windows.

    Features:
    - Per-app volume control
    - Process management
    - Window manipulation
    - System information
    - Audit logging

    Security:
    - Logs all privileged operations
    - Validates operations before execution
    - Provides safeguards against system damage
    """

    def __init__(self, audit_log_path: Optional[Path] = None):
        """
        Initialize System Integrator.

        Args:
            audit_log_path: Path to audit log file
        """
        self.audit_log_path = audit_log_path or Path("data/logs/god_mode_audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Capabilities
        self.capabilities = {
            "windows": WINDOWS,
            "pywin32": PYWIN32_AVAILABLE,
            "pycaw": PYCAW_AVAILABLE,
            "wmi": WMI_AVAILABLE,
            "psutil": True,  # Always available
        }

        # WMI connection (lazy)
        self._wmi_conn = None

        # Audio utilities cache
        self._audio_sessions_cache = {}
        self._audio_cache_time = 0
        self._audio_cache_ttl = 2  # seconds

        # Protected process names (cannot be killed)
        self.protected_processes = {
            "system",
            "wininit.exe",
            "csrss.exe",
            "services.exe",
            "lsass.exe",
            "winlogon.exe",
            "explorer.exe",
            "smss.exe",
        }

        logger.info("âœ… System Integrator initialized")
        logger.info(f"   Platform: {'Windows' if WINDOWS else 'Other'}")
        logger.info(f"   pywin32: {'âœ…' if PYWIN32_AVAILABLE else 'âŒ'}")
        logger.info(f"   pycaw: {'âœ…' if PYCAW_AVAILABLE else 'âŒ'}")
        logger.info(f"   WMI: {'âœ…' if WMI_AVAILABLE else 'âŒ'}")

    def _audit_log(
        self, operation: SystemOperation, details: str, success: bool = True
    ):
        """Log privileged operation to audit file"""
        try:
            timestamp = datetime.now().isoformat()
            status = "SUCCESS" if success else "FAILED"
            log_entry = f"[{timestamp}] {operation.value} | {status} | {details}\n"

            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    # ========================================================================
    # VOLUME CONTROL
    # ========================================================================
    def set_app_volume(self, app_name: str, volume: float) -> bool:
        """
        Set volume for specific application (0.0 to 1.0).

        Args:
            app_name: Application name or process name
            volume: Volume level (0.0 = mute, 1.0 = 100%)

        Returns:
            True if successful
        """
        if not PYCAW_AVAILABLE:
            logger.error("pycaw not available for volume control")
            return False

        if not 0.0 <= volume <= 1.0:
            logger.error(f"Invalid volume: {volume} (must be 0.0-1.0)")
            return False

        try:
            # Get audio sessions
            sessions = AudioUtilities.GetAllSessions()

            for session in sessions:
                if session.Process:
                    proc_name = session.Process.name().lower()

                    # Match app name
                    if app_name.lower() in proc_name:
                        # Get volume interface
                        volume_interface = session._ctl.QueryInterface(
                            ISimpleAudioVolume
                        )

                        # Set volume
                        volume_interface.SetMasterVolume(volume, None)

                        self._audit_log(
                            SystemOperation.SET_VOLUME,
                            f"{proc_name} -> {volume*100:.0f}%",
                        )

                        logger.info(
                            f"âœ… Set volume for {proc_name}: {volume*100:.0f}%"
                        )
                        return True

            logger.warning(f"No audio session found for: {app_name}")
            return False

        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            self._audit_log(
                SystemOperation.SET_VOLUME,
                f"{app_name} -> {volume*100:.0f}% | Error: {e}",
                success=False,
            )
            return False

    def get_app_volume(self, app_name: str) -> Optional[float]:
        """
        Get current volume for application.

        Args:
            app_name: Application name

        Returns:
            Volume level (0.0-1.0) or None if not found
        """
        if not PYCAW_AVAILABLE:
            return None

        try:
            sessions = AudioUtilities.GetAllSessions()

            for session in sessions:
                if session.Process:
                    proc_name = session.Process.name().lower()

                    if app_name.lower() in proc_name:
                        volume_interface = session._ctl.QueryInterface(
                            ISimpleAudioVolume
                        )
                        volume = volume_interface.GetMasterVolume()
                        return volume

            return None

        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return None

    def mute_app(self, app_name: str) -> bool:
        """Mute specific application"""
        return self.set_app_volume(app_name, 0.0)

    def unmute_app(self, app_name: str) -> bool:
        """Unmute specific application (set to 100%)"""
        return self.set_app_volume(app_name, 1.0)

    # ========================================================================
    # PROCESS MANAGEMENT
    # ========================================================================
    def kill_process(self, process_name: str, force: bool = False) -> bool:
        """
        Terminate process by name.

        Args:
            process_name: Process name (e.g., 'notepad.exe')
            force: Force kill even if protected (dangerous!)

        Returns:
            True if successful
        """
        # Safety check
        if process_name.lower() in self.protected_processes and not force:
            logger.error(f"Cannot kill protected process: {process_name}")
            logger.error("Use force=True to override (DANGEROUS!)")
            return False

        try:
            killed = False

            for proc in psutil.process_iter(["name", "pid"]):
                try:
                    if proc.info["name"].lower() == process_name.lower():
                        pid = proc.info["pid"]

                        # Kill process
                        proc.kill()

                        self._audit_log(
                            SystemOperation.KILL_PROCESS, f"{process_name} (PID: {pid})"
                        )

                        logger.info(f"âœ… Killed process: {process_name} (PID: {pid})")
                        killed = True

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"Cannot kill PID {proc.info['pid']}: {e}")

            if not killed:
                logger.warning(f"Process not found: {process_name}")

            return killed

        except Exception as e:
            logger.error(f"Failed to kill process: {e}")
            self._audit_log(
                SystemOperation.KILL_PROCESS,
                f"{process_name} | Error: {e}",
                success=False,
            )
            return False

    def get_process_info(self, process_name: Optional[str] = None) -> List[ProcessInfo]:
        """
        Get information about running processes.

        Args:
            process_name: Filter by process name (None = all processes)

        Returns:
            List of ProcessInfo objects
        """
        processes = []

        try:
            for proc in psutil.process_iter(
                ["name", "pid", "exe", "cpu_percent", "memory_info", "status"]
            ):
                try:
                    info = proc.info

                    # Filter by name if specified
                    if (
                        process_name
                        and process_name.lower() not in info["name"].lower()
                    ):
                        continue

                    # Get memory in MB
                    memory_mb = (
                        info["memory_info"].rss / (1024 * 1024)
                        if info.get("memory_info")
                        else 0
                    )

                    processes.append(
                        ProcessInfo(
                            pid=info["pid"],
                            name=info["name"],
                            exe=info.get("exe"),
                            cpu_percent=info.get("cpu_percent", 0),
                            memory_mb=memory_mb,
                            status=info.get("status", "unknown"),
                        )
                    )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            logger.error(f"Failed to get process info: {e}")

        return processes

    def is_process_running(self, process_name: str) -> bool:
        """Check if process is currently running"""
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"].lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    # ========================================================================
    # WINDOW MANAGEMENT
    # ========================================================================
    def get_active_window_title(self) -> Optional[str]:
        """Get title of currently active window"""
        if not PYWIN32_AVAILABLE:
            return None

        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title if title else None
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None

    def get_window_by_title(self, title_substring: str) -> Optional[WindowInfo]:
        """
        Find window by title substring.

        Args:
            title_substring: Part of window title to search for

        Returns:
            WindowInfo or None if not found
        """
        if not PYWIN32_AVAILABLE:
            return None

        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title_substring.lower() in window_title.lower():
                    results.append(hwnd)

        try:
            results = []
            win32gui.EnumWindows(enum_callback, results)

            if not results:
                return None

            # Get info for first match
            hwnd = results[0]
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)

            # Get PID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # Check window state
            placement = win32gui.GetWindowPlacement(hwnd)
            is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED

            return WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                pid=pid,
                is_visible=True,
                is_minimized=is_minimized,
            )

        except Exception as e:
            logger.error(f"Failed to find window: {e}")
            return None

    def focus_window(self, title_substring: str) -> bool:
        """
        Bring window to foreground by title.

        Args:
            title_substring: Part of window title

        Returns:
            True if successful
        """
        if not PYWIN32_AVAILABLE:
            return False

        try:
            window = self.get_window_by_title(title_substring)

            if not window:
                logger.warning(f"Window not found: {title_substring}")
                return False

            # Restore if minimized
            if window.is_minimized:
                win32gui.ShowWindow(window.hwnd, win32con.SW_RESTORE)

            # Bring to foreground
            win32gui.SetForegroundWindow(window.hwnd)

            self._audit_log(SystemOperation.FOCUS_WINDOW, f"{window.title}")

            logger.info(f"âœ… Focused window: {window.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to focus window: {e}")
            return False

    def minimize_window(self, title_substring: str) -> bool:
        """Minimize window by title"""
        if not PYWIN32_AVAILABLE:
            return False

        try:
            window = self.get_window_by_title(title_substring)

            if not window:
                return False

            win32gui.ShowWindow(window.hwnd, win32con.SW_MINIMIZE)

            self._audit_log(SystemOperation.MINIMIZE_WINDOW, f"{window.title}")

            logger.info(f"âœ… Minimized window: {window.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to minimize window: {e}")
            return False

    def close_window(self, title_substring: str) -> bool:
        """Close window by title"""
        if not PYWIN32_AVAILABLE:
            return False

        try:
            window = self.get_window_by_title(title_substring)

            if not window:
                return False

            # Send close message
            win32gui.PostMessage(window.hwnd, win32con.WM_CLOSE, 0, 0)

            self._audit_log(SystemOperation.CLOSE_WINDOW, f"{window.title}")

            logger.info(f"âœ… Closed window: {window.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            return False

    # ========================================================================
    # SYSTEM INFORMATION
    # ========================================================================
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = {}

        try:
            # CPU
            info["cpu"] = {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            }

            # Memory
            mem = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": mem.total / (1024**3),
                "available_gb": mem.available / (1024**3),
                "percent": mem.percent,
            }

            # Disk
            disk = psutil.disk_usage("/")
            info["disk"] = {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": disk.percent,
            }

            # Network (if available)
            try:
                net = psutil.net_io_counters()
                info["network"] = {
                    "bytes_sent": net.bytes_sent,
                    "bytes_recv": net.bytes_recv,
                }
            except BaseException:
                pass

            # Battery (if laptop)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    info["battery"] = {
                        "percent": battery.percent,
                        "plugged": battery.power_plugged,
                    }
            except BaseException:
                pass

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")

        return info

    def execute_shell_command(
        self, command: str, timeout: int = 30
    ) -> Tuple[bool, str]:
        """
        Execute shell command and return output.

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds

        Returns:
            (success, output)
        """
        try:
            if any(ch in command for ch in ["|", "&", ";", ">", "<", "$", "`"]):
                logger.warning(
                    "execute_shell_command: command contains shell operators — review for injection risk"
                )
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )

            success = result.returncode == 0
            output = result.stdout if success else result.stderr

            self._audit_log(
                SystemOperation.SHELL_COMMAND,
                f"{command[:50]}... | Exit: {result.returncode}",
                success=success,
            )

            return success, output

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return False, str(e)

    def cleanup(self):
        """Cleanup resources"""
        logger.info("âœ… System Integrator cleaned up")


# Singleton instance
_system_integrator: Optional[SystemIntegrator] = None


def get_system_integrator(audit_log_path: Optional[Path] = None) -> SystemIntegrator:
    """
    Get or create System Integrator singleton.

    Args:
        audit_log_path: Audit log path (for first call)

    Returns:
        SystemIntegrator instance
    """
    global _system_integrator

    if _system_integrator is None:
        _system_integrator = SystemIntegrator(audit_log_path)

    return _system_integrator


# Global Instance for direct import
try:
    system_integrator = SystemIntegrator()
except Exception:
    system_integrator = None


# Testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("\n" + "=" * 60)
    print("JARVIS System Integrator (God Mode) Test")
    print("=" * 60)

    # Create system integrator
    si = SystemIntegrator()

    # Test system info
    print("\n1. System Information:")
    info = si.get_system_info()
    print(f"   CPU: {info['cpu']['percent']}%")
    print(f"   Memory: {info['memory']['percent']}%")
    print(f"   Disk: {info['disk']['percent']}%")

    # Test active window
    print("\n2. Active Window:")
    title = si.get_active_window_title()
    print(f"   {title}")

    # Test process info
    print("\n3. Process Info (first 5):")
    processes = si.get_process_info()[:5]
    for proc in processes:
        print(
            f"   {proc.name} (PID: {proc.pid}) - CPU: {proc.cpu_percent}% - RAM: {proc.memory_mb:.1f}MB"
        )

    # Test shell command
    print("\n4. Shell Command (systeminfo):")
    if WINDOWS:
        success, output = si.execute_shell_command('systeminfo | findstr /C:"OS Name"')
        print(f"   {output.strip()}")
    else:
        success, output = si.execute_shell_command("uname -a")
        print(f"   {output.strip()}")

    print("\n" + "=" * 60)
    print("Capabilities:")
    for cap, available in si.capabilities.items():
        print(f"   {cap}: {'âœ…' if available else 'âŒ'}")
    print("=" * 60 + "\n")

    si.cleanup()
