# ============================================================================
# JARVIS SINGULARITY - System Controller (God Mode)
# ============================================================================
# Controle profundo do Windows via API programÃ¡tica
# Prioriza comandos diretos sobre automaÃ§Ã£o visual
# ============================================================================

<<<<<<< HEAD
<<<<<<< Updated upstream
import os
import sys
=======
>>>>>>> dev-new-version
import subprocess
import logging
from ctypes import cast, POINTER
from typing import Optional, List, Dict, Any
<<<<<<< HEAD
from pathlib import Path
=======
import logging
import shlex
import subprocess
from ctypes import POINTER, cast
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version

# Lazy import helpers
def _get_security_manager():
    from src.core.security.security_manager import SecurityManager

    return SecurityManager()


def _get_config():
    from src.utils.config import config

    return config


# -------------------------------------------------------------------------
# IMPORTS CONDICIONAIS (Graceful degradation)
# -------------------------------------------------------------------------
try:
<<<<<<< Updated upstream
    import win32gui
    import win32con
    import win32process
    import win32api
<<<<<<< HEAD
=======
    import win32api  # noqa: F401
    import win32con
    import win32gui
    import win32process  # noqa: F401

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    logging.warning(
        "âš ï¸ pywin32 nÃ£o disponÃ­vel - funcionalidades Win32 desabilitadas"
    )

try:
    import wmi

    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logging.warning(
        "âš ï¸ WMI nÃ£o disponÃ­vel - funcionalidades de hardware desabilitadas"
    )

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL

    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    logging.warning("âš ï¸ pycaw nÃ£o disponÃ­vel - controle de Ã¡udio desabilitado")

# -------------------------------------------------------------------------
# LOGGER
# -------------------------------------------------------------------------
logger = logging.getLogger(__name__)

SAFE_SHELL_EXECUTABLES = {
    "python",
    "python3",
    "pip",
    "git",
    "ollama",
    "whoami",
    "hostname",
    "ipconfig",
    "tasklist",
    "systeminfo",
    "wmic",
    "powershell",
    "pwsh",
}


# ============================================================================
# SYSTEM CONTROLLER
# ============================================================================
class SystemController:
    """
    Controle profundo do Windows via API.

    FILOSOFIA:
    - Prioriza API/CLI (rÃ¡pido, invisÃ­vel, robusto)
    - Fallback para automaÃ§Ã£o visual apenas quando necessÃ¡rio

    CAPACIDADES:
    - Gerenciamento de processos (kill, list, info)
    - Controle de janelas (find, focus, minimize, close)
    - Controle de Ã¡udio (volume global, volume por app)
    - InformaÃ§Ãµes de hardware (CPU, RAM, disco, BIOS)
    - ExecuÃ§Ã£o de comandos shell
    """

    def __init__(self):
        """Inicializa o System Controller"""
        logger.info("ðŸ”§ Inicializando System Controller...")

        # Verificar capacidades
        self.capabilities = {
            "win32": PYWIN32_AVAILABLE,
            "wmi": WMI_AVAILABLE,
            "pycaw": PYCAW_AVAILABLE,
            "psutil": True,  # Sempre disponÃ­vel
        }

        # Inicializar WMI se disponÃ­vel
        self.wmi_client = None
        if WMI_AVAILABLE:
            try:
                self.wmi_client = wmi.WMI()
                logger.info("âœ… WMI inicializado")
            except Exception as e:
                logger.warning(f"âš ï¸ Erro ao inicializar WMI: {e}")

        logger.info(f"âœ… System Controller online - Capacidades: {self.capabilities}")

    # -------------------------------------------------------------------------
    # PROCESS MANAGEMENT
    # -------------------------------------------------------------------------

    def kill_process_by_name(self, name: str) -> bool:
        """
        Mata processo por nome usando API (nÃ£o Task Manager).

        Args:
            name: Nome do processo (ex: "notepad.exe")

        Returns:
            True se matou pelo menos um processo
        """
        killed = False
        try:
            for proc in psutil.process_iter(["name", "pid"]):
                if proc.info["name"].lower() == name.lower():
                    proc.kill()
                    logger.info(
                        f"ðŸ”ª Processo {name} (PID {proc.info['pid']}) terminado"
                    )
                    killed = True
        except Exception as e:
            logger.error(f"âŒ Erro ao matar processo {name}: {e}")

        return killed

    def list_processes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os processos em execuÃ§Ã£o.

        Returns:
            Lista de dicts com info de processos
        """
        processes = []
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                processes.append(proc.info)
        except Exception as e:
            logger.error(f"âŒ Erro ao listar processos: {e}")

        return processes

    def get_process_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        ObtÃ©m informaÃ§Ãµes de um processo especÃ­fico.

        Args:
            name: Nome do processo

        Returns:
            Dict com info ou None se nÃ£o encontrado
        """
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent", "status"]
            ):
                if proc.info["name"].lower() == name.lower():
                    return proc.info
        except Exception as e:
            logger.error(f"âŒ Erro ao obter info de {name}: {e}")

        return None

    # -------------------------------------------------------------------------
    # WINDOW MANAGEMENT (Win32 API)
    # -------------------------------------------------------------------------

    def find_window_by_title(self, title: str, partial: bool = True) -> Optional[int]:
        """
        Encontra janela por tÃ­tulo usando Win32 API.

        Args:
            title: TÃ­tulo da janela
            partial: Se True, busca parcial

        Returns:
            Handle da janela ou None
        """
        if not PYWIN32_AVAILABLE:
            logger.warning("âš ï¸ pywin32 nÃ£o disponÃ­vel")
            return None

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if partial:
                    if title.lower() in window_title.lower():
                        windows.append(hwnd)
                else:
                    if title.lower() == window_title.lower():
                        windows.append(hwnd)

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
            return windows[0] if windows else None
        except Exception as e:
            logger.error(f"âŒ Erro ao buscar janela '{title}': {e}")
            return None

    def close_window(self, hwnd: int) -> bool:
        """
        Fecha janela por handle.

        Args:
            hwnd: Handle da janela

        Returns:
            True se fechou com sucesso
        """
        if not PYWIN32_AVAILABLE:
            return False

        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            logger.info(f"âœ… Janela {hwnd} fechada")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao fechar janela {hwnd}: {e}")
            return False

    def minimize_window(self, hwnd: int) -> bool:
        """Minimiza janela"""
        if not PYWIN32_AVAILABLE:
            return False

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao minimizar janela: {e}")
            return False

    # -------------------------------------------------------------------------
    # AUDIO CONTROL (PyCAW)
    # -------------------------------------------------------------------------

    def set_master_volume(self, level: float) -> bool:
        """
        Define volume mestre do sistema.

        Args:
            level: Volume de 0.0 a 1.0

        Returns:
            True se definiu com sucesso
        """
        if not PYCAW_AVAILABLE:
            logger.warning("âš ï¸ pycaw nÃ£o disponÃ­vel - usando fallback")
            return self._set_volume_fallback(level)

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level, None)
            logger.info(f"ðŸ”Š Volume mestre: {int(level * 100)}%")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao definir volume: {e}")
            return False

    def set_app_volume(self, app_name: str, level: float) -> bool:
        """
        Define volume de aplicativo especÃ­fico.

        Args:
            app_name: Nome do app (ex: "spotify.exe")
            level: Volume de 0.0 a 1.0

        Returns:
            True se definiu com sucesso
        """
        if not PYCAW_AVAILABLE:
            logger.warning(
                "âš ï¸ pycaw nÃ£o disponÃ­vel - controle por app indisponÃ­vel"
            )
            return False

        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if (
                    session.Process
                    and session.Process.name().lower() == app_name.lower()
                ):
                    volume = session.SimpleAudioVolume
                    volume.SetMasterVolume(level, None)
                    logger.info(f"ðŸ”Š Volume de {app_name}: {int(level * 100)}%")
                    return True

            logger.warning(f"âš ï¸ App {app_name} nÃ£o encontrado")
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao definir volume de {app_name}: {e}")
            return False

    def _set_volume_fallback(self, level: float) -> bool:
        """Fallback: usa NirCmd se disponÃ­vel"""
        try:
            volume_int = int(level * 65535)
            subprocess.run(
                ["nircmd.exe", "setsysvolume", str(volume_int)],
                capture_output=True,
                timeout=2,
            )
            return True
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # HARDWARE INFO (WMI)
    # -------------------------------------------------------------------------

    def get_hardware_info(self) -> Dict[str, Any]:
        """
        ObtÃ©m informaÃ§Ãµes de hardware via WMI.

        Returns:
            Dict com info de CPU, RAM, disco, BIOS
        """
        info = {"cpu": {}, "memory": {}, "disk": {}, "bios": {}}

        # CPU e RAM (psutil - sempre disponÃ­vel)
        try:
            info["cpu"] = {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            }

            mem = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
            }

            disk = psutil.disk_usage("/")
            info["disk"] = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": disk.percent,
            }
        except Exception as e:
            logger.error(f"âŒ Erro ao obter info bÃ¡sica: {e}")

        # BIOS (WMI - se disponÃ­vel)
        if self.wmi_client:
            try:
                for bios in self.wmi_client.Win32_BIOS():
                    info["bios"] = {
                        "manufacturer": bios.Manufacturer,
                        "version": bios.Version,
                        "serial": bios.SerialNumber,
                    }
                    break
            except Exception as e:
                logger.error(f"âŒ Erro ao obter info BIOS: {e}")

        return info

    # -------------------------------------------------------------------------
    # SHELL COMMANDS
    # -------------------------------------------------------------------------

    def execute_shell_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Executa comando shell diretamente.

        Args:
            command: Comando a executar
            timeout: Timeout em segundos

        Returns:
            Dict com stdout, stderr, returncode
        """
        try:
<<<<<<< HEAD
<<<<<<< Updated upstream
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
=======
            argv, validation_error = self._validate_shell_command(command)
            if validation_error:
                return {
                    "stdout": "",
                    "stderr": validation_error,
                    "returncode": -1,
                    "success": False,
                }

            result = subprocess.run(
                argv, shell=False, capture_output=True, text=True, timeout=timeout
>>>>>>> Stashed changes
=======
            if any(ch in command for ch in ["|", "&", ";", ">", "<", "$", "`"]):
                logger.warning(
                    "execute_shell_command: command contains shell operators — review for injection risk"
                )
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
>>>>>>> dev-new-version
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Comando excedeu timeout de {timeout}s",
                "returncode": -1,
                "success": False,
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}

    def _validate_shell_command(self, command: str):
        if not isinstance(command, str) or not command.strip():
            return None, "Comando vazio."

        blocked_operators = ("|", "&", ";", ">", "<", "`", "$(")
        if any(op in command for op in blocked_operators):
            return None, "Operadores de shell não são permitidos."

        try:
            argv = shlex.split(command, posix=False)
        except ValueError:
            return None, "Sintaxe de comando inválida."

        if not argv:
            return None, "Comando vazio."

        executable = Path(argv[0]).name.lower()
        if executable not in SAFE_SHELL_EXECUTABLES:
            return None, f"Executável '{executable}' não permitido."

        return argv, None


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
system_controller = SystemController()
