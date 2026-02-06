# ============================================================================
# JARVIS SINGULARITY - System Controller (God Mode)
# ============================================================================
# Controle profundo do Windows via API programática
# Prioriza comandos diretos sobre automação visual
# ============================================================================

import os
import sys
import subprocess
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

# -------------------------------------------------------------------------
# IMPORTS CONDICIONAIS (Graceful degradation)
# -------------------------------------------------------------------------
try:
    import win32gui
    import win32con
    import win32process
    import win32api
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    logging.warning("⚠️ pywin32 não disponível - funcionalidades Win32 desabilitadas")

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logging.warning("⚠️ WMI não disponível - funcionalidades de hardware desabilitadas")

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    logging.warning("⚠️ pycaw não disponível - controle de áudio desabilitado")

import psutil  # Sempre disponível (fallback)

# -------------------------------------------------------------------------
# LOGGER
# -------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ============================================================================
# SYSTEM CONTROLLER
# ============================================================================
class SystemController:
    """
    Controle profundo do Windows via API.
    
    FILOSOFIA:
    - Prioriza API/CLI (rápido, invisível, robusto)
    - Fallback para automação visual apenas quando necessário
    
    CAPACIDADES:
    - Gerenciamento de processos (kill, list, info)
    - Controle de janelas (find, focus, minimize, close)
    - Controle de áudio (volume global, volume por app)
    - Informações de hardware (CPU, RAM, disco, BIOS)
    - Execução de comandos shell
    """
    
    def __init__(self):
        """Inicializa o System Controller"""
        logger.info("🔧 Inicializando System Controller...")
        
        # Verificar capacidades
        self.capabilities = {
            "win32": PYWIN32_AVAILABLE,
            "wmi": WMI_AVAILABLE,
            "pycaw": PYCAW_AVAILABLE,
            "psutil": True  # Sempre disponível
        }
        
        # Inicializar WMI se disponível
        self.wmi_client = None
        if WMI_AVAILABLE:
            try:
                self.wmi_client = wmi.WMI()
                logger.info("✅ WMI inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar WMI: {e}")
        
        logger.info(f"✅ System Controller online - Capacidades: {self.capabilities}")
    
    # -------------------------------------------------------------------------
    # PROCESS MANAGEMENT
    # -------------------------------------------------------------------------
    
    def kill_process_by_name(self, name: str) -> bool:
        """
        Mata processo por nome usando API (não Task Manager).
        
        Args:
            name: Nome do processo (ex: "notepad.exe")
        
        Returns:
            True se matou pelo menos um processo
        """
        killed = False
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'].lower() == name.lower():
                    proc.kill()
                    logger.info(f"🔪 Processo {name} (PID {proc.info['pid']}) terminado")
                    killed = True
        except Exception as e:
            logger.error(f"❌ Erro ao matar processo {name}: {e}")
        
        return killed
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os processos em execução.
        
        Returns:
            Lista de dicts com info de processos
        """
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                processes.append(proc.info)
        except Exception as e:
            logger.error(f"❌ Erro ao listar processos: {e}")
        
        return processes
    
    def get_process_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de um processo específico.
        
        Args:
            name: Nome do processo
        
        Returns:
            Dict com info ou None se não encontrado
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                if proc.info['name'].lower() == name.lower():
                    return proc.info
        except Exception as e:
            logger.error(f"❌ Erro ao obter info de {name}: {e}")
        
        return None
    
    # -------------------------------------------------------------------------
    # WINDOW MANAGEMENT (Win32 API)
    # -------------------------------------------------------------------------
    
    def find_window_by_title(self, title: str, partial: bool = True) -> Optional[int]:
        """
        Encontra janela por título usando Win32 API.
        
        Args:
            title: Título da janela
            partial: Se True, busca parcial
        
        Returns:
            Handle da janela ou None
        """
        if not PYWIN32_AVAILABLE:
            logger.warning("⚠️ pywin32 não disponível")
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
            logger.error(f"❌ Erro ao buscar janela '{title}': {e}")
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
            logger.info(f"✅ Janela {hwnd} fechada")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao fechar janela {hwnd}: {e}")
            return False
    
    def minimize_window(self, hwnd: int) -> bool:
        """Minimiza janela"""
        if not PYWIN32_AVAILABLE:
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao minimizar janela: {e}")
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
            logger.warning("⚠️ pycaw não disponível - usando fallback")
            return self._set_volume_fallback(level)
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level, None)
            logger.info(f"🔊 Volume mestre: {int(level * 100)}%")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao definir volume: {e}")
            return False
    
    def set_app_volume(self, app_name: str, level: float) -> bool:
        """
        Define volume de aplicativo específico.
        
        Args:
            app_name: Nome do app (ex: "spotify.exe")
            level: Volume de 0.0 a 1.0
        
        Returns:
            True se definiu com sucesso
        """
        if not PYCAW_AVAILABLE:
            logger.warning("⚠️ pycaw não disponível - controle por app indisponível")
            return False
        
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name().lower() == app_name.lower():
                    volume = session.SimpleAudioVolume
                    volume.SetMasterVolume(level, None)
                    logger.info(f"🔊 Volume de {app_name}: {int(level * 100)}%")
                    return True
            
            logger.warning(f"⚠️ App {app_name} não encontrado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao definir volume de {app_name}: {e}")
            return False
    
    def _set_volume_fallback(self, level: float) -> bool:
        """Fallback: usa NirCmd se disponível"""
        try:
            volume_int = int(level * 65535)
            subprocess.run(['nircmd.exe', 'setsysvolume', str(volume_int)], 
                         capture_output=True, timeout=2)
            return True
        except:
            return False
    
    # -------------------------------------------------------------------------
    # HARDWARE INFO (WMI)
    # -------------------------------------------------------------------------
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """
        Obtém informações de hardware via WMI.
        
        Returns:
            Dict com info de CPU, RAM, disco, BIOS
        """
        info = {
            "cpu": {},
            "memory": {},
            "disk": {},
            "bios": {}
        }
        
        # CPU e RAM (psutil - sempre disponível)
        try:
            info["cpu"] = {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            }
            
            mem = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent
            }
            
            disk = psutil.disk_usage('/')
            info["disk"] = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": disk.percent
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter info básica: {e}")
        
        # BIOS (WMI - se disponível)
        if self.wmi_client:
            try:
                for bios in self.wmi_client.Win32_BIOS():
                    info["bios"] = {
                        "manufacturer": bios.Manufacturer,
                        "version": bios.Version,
                        "serial": bios.SerialNumber
                    }
                    break
            except Exception as e:
                logger.error(f"❌ Erro ao obter info BIOS: {e}")
        
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
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Comando excedeu timeout de {timeout}s",
                "returncode": -1,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "success": False
            }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
system_controller = SystemController()
