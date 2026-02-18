#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Advanced Device & System Manager
==============================================
Controle total do sistema operacional Windows:
- Hardware (CPU, GPU, RAM, Display, Audio)
- Rede (Interfaces, Firewall, Bandwidth)
- Energia (Power Plans, Shutdown, Sleep, Hibernate)
- Registro do Windows
- ServiÃ§os do Windows
- SeguranÃ§a e PrivilÃ©gios
- Monitoramento de SaÃºde do Sistema
"""

import logging
import os
import sys
import webbrowser
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

# Imports principais
import psutil

# Platform compatibility
from src.utils.platform_compat import (
    winreg,
    WINREG_AVAILABLE,
    win32api,
    win32con,
    win32security,
    PYWIN32_AVAILABLE,
    wmi,
    WMI_AVAILABLE,
    AudioUtilities,
    IAudioEndpointVolume,
    CLSCTX_ALL,
    PYCAW_AVAILABLE,
    ctypes,
)

# Define winreg constants for non-Windows platforms
if not WINREG_AVAILABLE or winreg is None:

    class _FakeWinreg:
        REG_SZ = 1
        REG_DWORD = 4
        KEY_READ = 0x20019
        KEY_SET_VALUE = 0x0002
        HKEY_LOCAL_MACHINE = None
        HKEY_CURRENT_USER = None

        def OpenKey(*args, **kwargs):
            raise NotImplementedError("winreg not available")

        def CreateKey(*args, **kwargs):
            raise NotImplementedError("winreg not available")

        def SetValueEx(*args, **kwargs):
            raise NotImplementedError("winreg not available")

        def QueryValueEx(*args, **kwargs):
            raise NotImplementedError("winreg not available")

        def CloseKey(*args, **kwargs):
            pass

        def DeleteValue(*args, **kwargs):
            raise NotImplementedError("winreg not available")

    winreg = _FakeWinreg()

# Imports opcionais com graceful degradation
try:
    import screen_brightness_control as sbc

    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False
    PYWIN32_AVAILABLE = False

logger = logging.getLogger(__name__)

# ================== ENUMS ==================


class PowerPlan(Enum):
    """Planos de energia do Windows"""

    BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
    HIGH_PERFORMANCE = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    POWER_SAVER = "a1841308-3541-4fab-bc81-f71556f20b4a"


class ServiceAction(Enum):
    """AÃ§Ãµes para serviÃ§os Windows"""

    START = "start"
    STOP = "stop"
    RESTART = "restart"
    PAUSE = "pause"
    RESUME = "continue"


class ProcessPriority(Enum):
    """Prioridades de processos"""

    REALTIME = (
        psutil.REALTIME_PRIORITY_CLASS
        if hasattr(psutil, "REALTIME_PRIORITY_CLASS")
        else 256
    )
    HIGH = psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, "HIGH_PRIORITY_CLASS") else 128
    ABOVE_NORMAL = (
        psutil.ABOVE_NORMAL_PRIORITY_CLASS
        if hasattr(psutil, "ABOVE_NORMAL_PRIORITY_CLASS")
        else 32768
    )
    NORMAL = (
        psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, "NORMAL_PRIORITY_CLASS") else 32
    )
    BELOW_NORMAL = (
        psutil.BELOW_NORMAL_PRIORITY_CLASS
        if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS")
        else 16384
    )
    IDLE = psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, "IDLE_PRIORITY_CLASS") else 64


# ================== MAIN CLASS ==================


class AdvancedDeviceManager:
    """
    Gerenciador AvanÃ§ado com Controle Total do Sistema Windows

    Features:
    - Hardware monitoring (CPU, GPU, RAM, Disk, Network)
    - Network control (interfaces, firewall, connections)
    - Power management (shutdown, sleep, hibernate, plans)
    - Windows Registry (safe read/write with backup)
    - Windows Services (start/stop/restart)
    - Display control (brightness, resolution, multi-monitor)
    - Audio control (volume, mute, devices)
    - Process management (priority, affinity, kill)
    - Security (admin checks, privileges, UAC)
    - Disk health (SMART, space analysis)
    """

    def __init__(self):
        """Inicializa o gerenciador com verificaÃ§Ãµes de dependÃªncias"""
        self.wmi_interface = None
        self.audio_interface = None
        self.is_admin = self._check_admin_rights()

        # Inicializa WMI se disponÃ­vel
        if WMI_AVAILABLE:
            try:
                self.wmi_interface = wmi.WMI()
            except Exception as e:
                logger.warning(f"âš ï¸ Falha ao inicializar WMI: {e}")

        # Inicializa interface de Ã¡udio se disponÃ­vel
        if PYCAW_AVAILABLE:
            try:
                self.audio_interface = self._get_audio_interface()
            except Exception as e:
                logger.warning(f"âš ï¸ Falha ao inicializar controle de Ã¡udio: {e}")

        logger.info(f"ðŸŽ›ï¸ DeviceManager inicializado (Admin: {self.is_admin})")

    # ==================== HARDWARE MONITORING ====================

    def get_system_info(self) -> Dict[str, Any]:
        """
        Coleta informaÃ§Ãµes completas do sistema

        Returns:
            Dict com CPU, RAM, Disk, Network, GPU, Battery info
        """
        try:
            info = {
                "cpu": self._get_cpu_info(),
                "memory": self._get_memory_info(),
                "disk": self._get_disk_info(),
                "network": self.get_network_info(),
                "gpu": self._get_gpu_info(),
                "battery": self._get_battery_info(),
                "timestamp": datetime.now().isoformat(),
            }
            return info
        except Exception as e:
            logger.error(f"âŒ Erro ao coletar info do sistema: {e}")
            return {}

    def _get_cpu_info(self) -> Dict[str, Any]:
        """InformaÃ§Ãµes detalhadas da CPU"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "usage_percent": psutil.cpu_percent(interval=1),
                "usage_per_core": psutil.cpu_percent(interval=1, percpu=True),
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
                "frequency_min": cpu_freq.min if cpu_freq else None,
                "frequency_max": cpu_freq.max if cpu_freq else None,
                "temperature_celsius": self._get_cpu_temperature(),
            }
        except Exception as e:
            logger.error(f"Erro ao obter info CPU: {e}")
            return {}

    def _get_cpu_temperature(self) -> Optional[float]:
        """Temperatura da CPU (requer sensores)"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Procura por diferentes nomes de sensores
                    for name in ["coretemp", "k10temp", "cpu_thermal"]:
                        if name in temps and temps[name]:
                            return temps[name][0].current
        except Exception:
            pass
        return None

    def _get_memory_info(self) -> Dict[str, Any]:
        """InformaÃ§Ãµes de memÃ³ria RAM e SWAP"""
        try:
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                "ram": {
                    "total_gb": round(vm.total / (1024**3), 2),
                    "available_gb": round(vm.available / (1024**3), 2),
                    "used_gb": round(vm.used / (1024**3), 2),
                    "percent": vm.percent,
                },
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "free_gb": round(swap.free / (1024**3), 2),
                    "percent": swap.percent,
                },
            }
        except Exception as e:
            logger.error(f"Erro ao obter info de memÃ³ria: {e}")
            return {}

    def _get_disk_info(self) -> List[Dict[str, Any]]:
        """InformaÃ§Ãµes de todos os discos"""
        disks = []
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "percent": usage.percent,
                        }
                    )
                except PermissionError:
                    continue
        except Exception as e:
            logger.error(f"Erro ao obter info de discos: {e}")
        return disks

    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """InformaÃ§Ãµes das GPUs (via WMI)"""
        gpus = []
        if not self.wmi_interface:
            return gpus

        try:
            for gpu in self.wmi_interface.Win32_VideoController():
                gpus.append(
                    {
                        "name": gpu.Name,
                        "driver_version": gpu.DriverVersion,
                        "video_memory_mb": (
                            int(gpu.AdapterRAM / (1024**2)) if gpu.AdapterRAM else None
                        ),
                        "status": gpu.Status,
                        "availability": gpu.Availability,
                    }
                )
        except Exception as e:
            logger.error(f"Erro ao obter info GPU: {e}")
        return gpus

    def _get_battery_info(self) -> Optional[Dict[str, Any]]:
        """InformaÃ§Ãµes da bateria (se houver)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "time_left_seconds": (
                        battery.secsleft
                        if battery.secsleft != psutil.POWER_TIME_UNLIMITED
                        else None
                    ),
                }
        except Exception as e:
            logger.error(f"Erro ao obter info de bateria: {e}")
        return None

    # ==================== NETWORK CONTROL ====================

    def get_network_info(self) -> Dict[str, Any]:
        """
        InformaÃ§Ãµes completas de rede

        Returns:
            Dict com interfaces, conexÃµes ativas e estatÃ­sticas
        """
        try:
            info = {
                "interfaces": self.list_network_interfaces(),
                "connections": self.list_network_connections(),
                "stats": self._get_network_stats(),
            }
            return info
        except Exception as e:
            logger.error(f"Erro ao obter info de rede: {e}")
            return {}

    def list_network_interfaces(self) -> List[Dict[str, Any]]:
        """Lista todas as interfaces de rede"""
        interfaces = []
        try:
            for iface_name, addrs in psutil.net_if_addrs().items():
                stats = psutil.net_if_stats().get(iface_name)
                iface_info = {
                    "name": iface_name,
                    "is_up": stats.isup if stats else False,
                    "speed_mbps": stats.speed if stats else None,
                    "addresses": [],
                }

                for addr in addrs:
                    iface_info["addresses"].append(
                        {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        }
                    )

                interfaces.append(iface_info)
        except Exception as e:
            logger.error(f"Erro ao listar interfaces de rede: {e}")
        return interfaces

    def list_network_connections(self, kind: str = "inet") -> List[Dict[str, Any]]:
        """
        Lista conexÃµes de rede ativas

        Args:
            kind: Tipo de conexÃ£o ('inet', 'tcp', 'udp', etc)
        """
        connections = []
        try:
            for conn in psutil.net_connections(kind=kind):
                connections.append(
                    {
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_addr": (
                            f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                        ),
                        "remote_addr": (
                            f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                        ),
                        "status": conn.status,
                        "pid": conn.pid,
                    }
                )
        except (psutil.AccessDenied, PermissionError):
            logger.warning("âš ï¸ Sem permissÃ£o para listar todas as conexÃµes")
        except Exception as e:
            logger.error(f"Erro ao listar conexÃµes: {e}")
        return connections

    def _get_network_stats(self) -> Dict[str, Any]:
        """EstatÃ­sticas de trÃ¡fego de rede"""
        try:
            stats = psutil.net_io_counters()
            return {
                "bytes_sent": stats.bytes_sent,
                "bytes_recv": stats.bytes_recv,
                "packets_sent": stats.packets_sent,
                "packets_recv": stats.packets_recv,
                "errors_in": stats.errin,
                "errors_out": stats.errout,
                "drops_in": stats.dropin,
                "drops_out": stats.dropout,
            }
        except Exception as e:
            logger.error(f"Erro ao obter stats de rede: {e}")
            return {}

    def enable_network_interface(
        self, interface_name: str, enable: bool = True
    ) -> bool:
        """
        Habilita/desabilita interface de rede

        Args:
            interface_name: Nome da interface
            enable: True para habilitar, False para desabilitar

        Returns:
            True se bem-sucedido
        """
        if not self.is_admin:
            logger.error("âŒ Requer privilÃ©gios administrativos")
            return False

        try:
            action = "enable" if enable else "disable"
            result = subprocess.run(
                ["netsh", "interface", "set", "interface", interface_name, action],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info(f"âœ… Interface {interface_name} {action}d")
                return True
            else:
                logger.error(f"âŒ Erro ao {action} interface: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"âŒ Erro ao modificar interface: {e}")
            return False

    def block_process_network(
        self, pid: int, program_path: Optional[str] = None
    ) -> bool:
        """
        Bloqueia conexÃµes de rede de um processo via Firewall do Windows

        Args:
            pid: ID do processo
            program_path: Caminho do executÃ¡vel (opcional, serÃ¡ detectado)

        Returns:
            True se bloqueado com sucesso
        """
        if not self.is_admin:
            logger.error("âŒ Requer privilÃ©gios administrativos")
            return False

        try:
            # ObtÃ©m caminho do executÃ¡vel se nÃ£o fornecido
            if not program_path:
                proc = psutil.Process(pid)
                program_path = proc.exe()

            rule_name = f"JARVIS_BLOCK_{pid}_{Path(program_path).stem}"

            # Cria regra de firewall
            result = subprocess.run(
                [
                    "netsh",
                    "advfirewall",
                    "firewall",
                    "add",
                    "rule",
                    f"name={rule_name}",
                    "dir=out",
                    "action=block",
                    f"program={program_path}",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                logger.info(f"ðŸ”¥ Processo {pid} bloqueado no firewall")
                return True
            else:
                logger.error(f"âŒ Erro ao criar regra de firewall: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"âŒ Erro ao bloquear processo: {e}")
            return False

    def unblock_process_network(self, rule_name: str) -> bool:
        """Remove regra de bloqueio do firewall"""
        if not self.is_admin:
            logger.error("âŒ Requer privilÃ©gios administrativos")
            return False

        try:
            result = subprocess.run(
                [
                    "netsh",
                    "advfirewall",
                    "firewall",
                    "delete",
                    "rule",
                    f"name={rule_name}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"âŒ Erro ao remover regra de firewall: {e}")
            return False

    # ==================== POWER MANAGEMENT ====================

    def shutdown(self, force: bool = False, timeout: int = 30) -> bool:
        """
        Desliga o sistema

        Args:
            force: ForÃ§a o desligamento sem salvar
            timeout: Tempo em segundos atÃ© o desligamento

        Returns:
            True se comando foi executado
        """
        try:
            if PYWIN32_AVAILABLE and timeout == 0:
                flags = win32con.EWX_SHUTDOWN
                if force:
                    flags |= win32con.EWX_FORCE
                win32api.ExitWindowsEx(flags, 0)
                logger.info("ðŸ”Œ Sistema desligando...")
                return True
            else:
                # Fallback usando shutdown.exe
                cmd = ["shutdown", "/s"]
                if force:
                    cmd.append("/f")
                if timeout > 0:
                    cmd.extend(["/t", str(timeout)])
                else:
                    cmd.extend(["/t", "0"])

                subprocess.Popen(cmd)
                logger.info(f"ðŸ”Œ Desligamento agendado em {timeout}s")
                return True
        except Exception as e:
            logger.error(f"âŒ Erro ao desligar sistema: {e}")
            return False

    def restart(self, force: bool = False, timeout: int = 30) -> bool:
        """
        Reinicia o sistema

        Args:
            force: ForÃ§a o reinÃ­cio sem salvar
            timeout: Tempo em segundos atÃ© o reinÃ­cio
        """
        try:
            if PYWIN32_AVAILABLE and timeout == 0:
                flags = win32con.EWX_REBOOT
                if force:
                    flags |= win32con.EWX_FORCE
                win32api.ExitWindowsEx(flags, 0)
                logger.info("ðŸ”„ Sistema reiniciando...")
                return True
            else:
                cmd = ["shutdown", "/r"]
                if force:
                    cmd.append("/f")
                if timeout > 0:
                    cmd.extend(["/t", str(timeout)])
                else:
                    cmd.extend(["/t", "0"])

                subprocess.Popen(cmd)
                logger.info(f"ðŸ”„ ReinÃ­cio agendado em {timeout}s")
                return True
        except Exception as e:
            logger.error(f"âŒ Erro ao reiniciar sistema: {e}")
            return False

    def cancel_shutdown(self) -> bool:
        """Cancela shutdown/restart agendado"""
        try:
            result = subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("âœ… Shutdown cancelado")
                return True
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao cancelar shutdown: {e}")
            return False

    def sleep(self) -> bool:
        """Coloca o sistema em modo sleep"""
        try:
            if PYWIN32_AVAILABLE:
                ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
                logger.info("ðŸ’¤ Sistema entrando em sleep...")
                return True
            else:
                # Fallback
                subprocess.run(
                    ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]
                )
                return True
        except Exception as e:
            logger.error(f"âŒ Erro ao colocar sistema em sleep: {e}")
            return False

    def hibernate(self) -> bool:
        """Hiberna o sistema"""
        try:
            if PYWIN32_AVAILABLE:
                ctypes.windll.powrprof.SetSuspendState(1, 1, 0)
                logger.info("ðŸ’¤ Sistema hibernando...")
                return True
            else:
                subprocess.run(["shutdown", "/h"])
                return True
        except Exception as e:
            logger.error(f"âŒ Erro ao hibernar sistema: {e}")
            return False

    def set_power_plan(self, plan: PowerPlan) -> bool:
        """
        Define o plano de energia ativo

        Args:
            plan: PowerPlan enum (BALANCED, HIGH_PERFORMANCE, POWER_SAVER)
        """
        try:
            result = subprocess.run(
                ["powercfg", "/setactive", plan.value],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info(f"âš¡ Plano de energia alterado para {plan.name}")
                return True
            else:
                logger.error(f"âŒ Erro ao definir plano: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"âŒ Erro ao definir plano de energia: {e}")
            return False

    def get_active_power_plan(self) -> Optional[str]:
        """Retorna o GUID do plano de energia ativo"""
        try:
            result = subprocess.run(
                ["powercfg", "/getactivescheme"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Parse output: "Power Scheme GUID: <guid> (Name)"
                output = result.stdout
                if "GUID:" in output:
                    guid = output.split("GUID:")[1].split("(")[0].strip()
                    return guid
        except Exception as e:
            logger.error(f"Erro ao obter plano ativo: {e}")
        return None

    # ==================== WINDOWS REGISTRY ====================

    def read_registry(self, hive: int, key_path: str, value_name: str) -> Optional[Any]:
        """
        LÃª valor do registro do Windows

        Args:
            hive: winreg.HKEY_* (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc)
            key_path: Caminho da chave (ex: "Software\\Microsoft\\Windows")
            value_name: Nome do valor

        Returns:
            Valor lido ou None se nÃ£o encontrado
        """
        try:
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
            value, reg_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            logger.info(f"ðŸ“– Lido do registro: {key_path}\\{value_name}")
            return value
        except FileNotFoundError:
            logger.warning(
                f"âš ï¸ Chave ou valor nÃ£o encontrado: {key_path}\\{value_name}"
            )
            return None
        except Exception as e:
            logger.error(f"âŒ Erro ao ler registro: {e}")
            return None

    def write_registry(
        self,
        hive: int,
        key_path: str,
        value_name: str,
        value: Any,
        value_type: int = winreg.REG_SZ,
        backup: bool = True,
    ) -> bool:
        """
        Escreve valor no registro do Windows (com backup opcional)

        Args:
            hive: winreg.HKEY_*
            key_path: Caminho da chave
            value_name: Nome do valor
            value: Valor a escrever
            value_type: Tipo do valor (REG_SZ, REG_DWORD, etc)
            backup: Se True, faz backup antes de modificar

        Returns:
            True se bem-sucedido
        """
        if not self.is_admin:
            logger.warning(
                "âš ï¸ ModificaÃ§Ã£o do registro pode requerer privilÃ©gios administrativos"
            )

        try:
            # Backup se solicitado
            if backup:
                old_value = self.read_registry(hive, key_path, value_name)
                if old_value is not None:
                    self._backup_registry_value(hive, key_path, value_name, old_value)

            # Escreve novo valor
            key = winreg.CreateKey(hive, key_path)
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)

            logger.info(f"âœï¸ Escrito no registro: {key_path}\\{value_name}")
            return True
        except PermissionError:
            logger.error("âŒ Sem permissÃ£o para modificar registro (requer admin)")
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao escrever no registro: {e}")
            return False

    def _backup_registry_value(
        self, hive: int, key_path: str, value_name: str, value: Any
    ) -> None:
        """Faz backup de valor do registro"""
        try:
            backup_dir = Path("data/registry_backups")
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "hive": hive,
                "key_path": key_path,
                "value_name": value_name,
                "old_value": str(value),
            }

            filename = (
                f"registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(backup_dir / filename, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"ðŸ’¾ Backup do registro salvo: {filename}")
        except Exception as e:
            logger.warning(f"âš ï¸ Falha ao fazer backup do registro: {e}")

    def delete_registry_value(
        self, hive: int, key_path: str, value_name: str, backup: bool = True
    ) -> bool:
        """Remove um valor do registro (com backup opcional)"""
        if not self.is_admin:
            logger.warning(
                "âš ï¸ DeleÃ§Ã£o do registro pode requerer privilÃ©gios administrativos"
            )

        try:
            # Backup se solicitado
            if backup:
                old_value = self.read_registry(hive, key_path, value_name)
                if old_value is not None:
                    self._backup_registry_value(hive, key_path, value_name, old_value)

            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)

            logger.info(f"ðŸ—‘ï¸ Valor removido do registro: {key_path}\\{value_name}")
            return True
        except FileNotFoundError:
            logger.warning(f"âš ï¸ Valor nÃ£o existe: {key_path}\\{value_name}")
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao deletar valor: {e}")
            return False

    # ==================== WINDOWS SERVICES ====================

    def list_services(self) -> List[Dict[str, Any]]:
        """Lista todos os serviÃ§os do Windows"""
        services = []

        if self.wmi_interface:
            try:
                for service in self.wmi_interface.Win32_Service():
                    services.append(
                        {
                            "name": service.Name,
                            "display_name": service.DisplayName,
                            "state": service.State,
                            "start_mode": service.StartMode,
                            "status": service.Status,
                            "path_name": service.PathName,
                            "process_id": service.ProcessId,
                        }
                    )
            except Exception as e:
                logger.error(f"Erro ao listar serviÃ§os via WMI: {e}")
        else:
            # Fallback: usa sc query
            try:
                result = subprocess.run(
                    ["sc", "query", "state=", "all"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                # Parse output (simplificado)
                logger.info("ðŸ“‹ ServiÃ§os listados via sc query")
            except Exception as e:
                logger.error(f"Erro ao listar serviÃ§os: {e}")

        return services

    def control_service(self, service_name: str, action: ServiceAction) -> bool:
        """
        Controla um serviÃ§o do Windows

        Args:
            service_name: Nome do serviÃ§o
            action: ServiceAction enum (START, STOP, RESTART, etc)

        Returns:
            True se comando foi bem-sucedido
        """
        if not self.is_admin:
            logger.error(
                "âŒ Controle de serviÃ§os requer privilÃ©gios administrativos"
            )
            return False

        try:
            if action == ServiceAction.RESTART:
                # Restart = Stop + Start
                self.control_service(service_name, ServiceAction.STOP)
                import time

                time.sleep(2)
                return self.control_service(service_name, ServiceAction.START)

            result = subprocess.run(
                ["net", action.value, service_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info(f"âœ… ServiÃ§o {service_name} - {action.value}")
                return True
            else:
                # Pode jÃ¡ estar no estado desejado
                if "already" in result.stdout.lower() or "jÃ¡" in result.stdout.lower():
                    logger.info(
                        f"â„¹ï¸ ServiÃ§o {service_name} jÃ¡ estÃ¡ no estado desejado"
                    )
                    return True
                logger.error(f"âŒ Erro ao controlar serviÃ§o: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"âŒ Erro ao controlar serviÃ§o {service_name}: {e}")
            return False

    def get_service_dependencies(self, service_name: str) -> List[str]:
        """Retorna lista de dependÃªncias de um serviÃ§o"""
        dependencies = []
        try:
            result = subprocess.run(
                ["sc", "enumdepend", service_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Parse output para extrair nomes de serviÃ§os
                for line in result.stdout.split("\n"):
                    if "SERVICE_NAME:" in line:
                        dep_name = line.split(":")[1].strip()
                        dependencies.append(dep_name)
        except Exception as e:
            logger.error(f"Erro ao obter dependÃªncias do serviÃ§o: {e}")
        return dependencies

    # ==================== DISPLAY CONTROL ====================

    def set_brightness(self, level: int) -> bool:
        """
        Ajusta o brilho do monitor (0-100) com fallback WMI.

        Args:
            level: NÃ­vel de brilho (0-100)
        """
        level = max(0, min(100, level))

        # 1. Tentar via screen_brightness_control (SBC)
        if SBC_AVAILABLE:
            try:
                sbc.set_brightness(level)
                logger.info(f"ðŸ’¡ Brilho ajustado para {level}% via SBC")
                return True
            except Exception as e:
                logger.warning(f"âš ï¸ Falha no SBC: {e}. Tentando fallback WMI...")

        # 2. Fallback Definitive: WMI (ForÃ§a o hardware do notebook - Samsung
        # Fix)
        try:
            import wmi

            wmi_inst = wmi.WMI(namespace="wmi")
            methods = wmi_inst.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(1, level)  # Timeout 1, NÃ­vel level
            logger.info(
                f"ðŸ’¡ Brilho ajustado para {level}% via WMI (Hardware Direct/Samsung Mode)"
            )
            return True
        except Exception as e:
            logger.error(f"âŒ Falha crÃ­tica no controle de brilho WMI: {e}")

        return False

    def get_brightness(self) -> Optional[int]:
        """Retorna brilho atual"""
        if not SBC_AVAILABLE:
            return None
        try:
            brightness = sbc.get_brightness()
            return brightness[0] if isinstance(brightness, list) else brightness
        except Exception as e:
            logger.error(f"Erro ao obter brilho: {e}")
            return None

    def get_display_info(self) -> List[Dict[str, Any]]:
        """InformaÃ§Ãµes dos monitores conectados"""
        displays = []

        if self.wmi_interface:
            try:
                for monitor in self.wmi_interface.Win32_DesktopMonitor():
                    displays.append(
                        {
                            "name": monitor.Name,
                            "device_id": monitor.DeviceID,
                            "pnp_device_id": monitor.PNPDeviceID,
                            "monitor_manufacturer": monitor.MonitorManufacturer,
                            "monitor_type": monitor.MonitorType,
                            "screen_width": monitor.ScreenWidth,
                            "screen_height": monitor.ScreenHeight,
                            "pixels_per_x_logical_inch": monitor.PixelsPerXLogicalInch,
                            "pixels_per_y_logical_inch": monitor.PixelsPerYLogicalInch,
                        }
                    )
            except Exception as e:
                logger.error(f"Erro ao obter info de displays: {e}")

        return displays

    def set_display_resolution(
        self, width: int, height: int, refresh_rate: int = 60
    ) -> bool:
        """
        Altera resoluÃ§Ã£o e taxa de atualizaÃ§Ã£o do display

        Args:
            width: Largura em pixels
            height: Altura em pixels
            refresh_rate: Taxa de atualizaÃ§Ã£o em Hz
        """
        if not PYWIN32_AVAILABLE:
            logger.error("âŒ pywin32 nÃ£o disponÃ­vel")
            return False

        try:
            devmode = win32api.EnumDisplaySettings(None, 0)
            devmode.PelsWidth = width
            devmode.PelsHeight = height
            devmode.DisplayFrequency = refresh_rate
            devmode.Fields = (
                win32con.DM_PELSWIDTH
                | win32con.DM_PELSHEIGHT
                | win32con.DM_DISPLAYFREQUENCY
            )

            result = win32api.ChangeDisplaySettings(devmode, 0)

            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                logger.info(
                    f"ðŸ–¥ï¸ ResoluÃ§Ã£o alterada para {width}x{height}@{refresh_rate}Hz"
                )
                return True
            else:
                error_msgs = {
                    win32con.DISP_CHANGE_RESTART: "Requer reinicializaÃ§Ã£o",
                    win32con.DISP_CHANGE_BADFLAGS: "Flags invÃ¡lidas",
                    win32con.DISP_CHANGE_BADPARAM: "ParÃ¢metros invÃ¡lidos",
                    win32con.DISP_CHANGE_FAILED: "Falha ao alterar",
                    win32con.DISP_CHANGE_BADMODE: "Modo nÃ£o suportado",
                }
                logger.error(f"âŒ {error_msgs.get(result, 'Erro desconhecido')}")
                return False
        except Exception as e:
            logger.error(f"âŒ Erro ao alterar resoluÃ§Ã£o: {e}")
            return False

    # ==================== AUDIO CONTROL ====================

    def _get_audio_interface(self):
        """ObtÃ©m interface de controle de Ã¡udio do Windows"""
        try:
            devices = AudioUtilities.GetSpeakers()
            # pycaw moderno retorna AudioDevice wrapper com .EndpointVolume
            if hasattr(devices, "EndpointVolume"):
                return devices.EndpointVolume
            # pycaw legado retorna IMMDevice COM com .Activate()
            elif hasattr(devices, "Activate"):
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                return cast(interface, POINTER(IAudioEndpointVolume))
            # Fallback: tentar _dev interno
            elif hasattr(devices, "_dev") and hasattr(devices._dev, "Activate"):
                interface = devices._dev.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                return cast(interface, POINTER(IAudioEndpointVolume))
            else:
                logger.warning(
                    "âš ï¸ NÃ£o foi possÃ­vel obter interface de volume (API pycaw desconhecida)"
                )
                return None
        except Exception as e:
            logger.error(f"Erro ao obter interface de Ã¡udio: {e}")
            return None

    def set_volume(self, level: float) -> bool:
        """
        Define volume do sistema (0.0 a 1.0)

        Args:
            level: NÃ­vel de volume (0.0 = mudo, 1.0 = mÃ¡ximo)
        """
        if self.audio_interface:
            try:
                level = max(0.0, min(1.0, level))
                self.audio_interface.SetMasterVolumeLevelScalar(level, None)
                logger.info(f"ðŸ”Š Volume ajustado para {int(level * 100)}%")
                return True
            except Exception as e:
                logger.error(f"âŒ Erro ao definir volume: {e}")
                return False
        else:
            # Fallback PowerShell (menos preciso)
            try:
                level_percent = int(level * 100)
                level_percent = max(0, min(100, level_percent))
                cmd = f"(new-object -com wscript.shell).SendKeys([char]174)*50; (new-object -com wscript.shell).SendKeys([char]175)*{level_percent//2}"
                subprocess.run(
                    ["powershell", "-Command", cmd], capture_output=True, timeout=5
                )
                logger.info(
                    f"ðŸ”Š Volume ajustado para aproximadamente {level_percent}%"
                )
                return True
            except Exception as e:
                logger.error(f"âŒ Falha ao ajustar volume: {e}")
                return False

    def get_volume(self) -> Optional[float]:
        """Retorna volume atual (0.0 a 1.0)"""
        if self.audio_interface:
            try:
                return self.audio_interface.GetMasterVolumeLevelScalar()
            except Exception as e:
                logger.error(f"Erro ao obter volume: {e}")
        return None

    def mute(self, muted: bool = True) -> bool:
        """Silencia/ativa Ã¡udio de saÃ­da (Speakers)"""
        if self.audio_interface:
            try:
                self.audio_interface.SetMute(1 if muted else 0, None)
                logger.info(
                    f"ðŸ”‡ Ãudio de saÃ­da {'mutado' if muted else 'desmutado'}"
                )
                return True
            except Exception as e:
                logger.error(f"âŒ Erro ao mutar Ã¡udio: {e}")
                return False
        return False

    def mute_microphone(self, muted: bool = True) -> bool:
        """
        Silencia/ativa o microfone padrÃ£o do sistema.
        Ãštil para comandos de 'Privacidade' ou 'Ficar em silÃªncio'.
        """
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL

            devices = AudioUtilities.GetMicrophone()
            if not devices:
                logger.warning("âš ï¸ Nenhum microfone encontrado para mutar.")
                return False

            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1 if muted else 0, None)
            logger.info(f"ðŸŽ™ï¸ Microfone {'mutado' if muted else 'desmutado'}")
            return True
        except Exception as e:
            logger.error(f"âŒ Falha ao mutar microfone: {e}")
            return False

    def lock_workstation(self) -> bool:
        """
        Bloqueia a tela do Windows instantaneamente (Win + L).
        AÃ§Ã£o FÃ­sica Real via user32.dll.
        """
        try:
            logger.info("ðŸ”’ Bloqueando estaÃ§Ã£o de trabalho...")
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao bloquear tela: {e}")
            return False

    def list_audio_devices(self) -> List[Dict[str, Any]]:
        """Lista dispositivos de Ã¡udio disponÃ­veis"""
        devices = []
        if PYCAW_AVAILABLE:
            try:
                for device in AudioUtilities.GetAllDevices():
                    devices.append(
                        {
                            "id": device.id,
                            "name": device.FriendlyName,
                            "state": str(device.state),
                        }
                    )
            except Exception as e:
                logger.error(f"Erro ao listar dispositivos de Ã¡udio: {e}")
        return devices

    # ==================== PROCESS MANAGEMENT ====================

    def list_processes(self, sort_by: str = "cpu") -> List[Dict[str, Any]]:
        """
        Lista todos os processos do sistema

        Args:
            sort_by: Ordenar por 'cpu', 'memory', 'name'
        """
        processes = []
        for proc in psutil.process_iter(
            [
                "pid",
                "name",
                "username",
                "cpu_percent",
                "memory_percent",
                "status",
                "create_time",
            ]
        ):
            try:
                info = proc.info
                info["create_time"] = datetime.fromtimestamp(
                    info["create_time"]
                ).isoformat()
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # OrdenaÃ§Ã£o
        if sort_by == "cpu":
            processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x.get("memory_percent", 0), reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda x: x.get("name", "").lower())

        return processes

    def kill_process(self, pid: int, force: bool = False, timeout: int = 5) -> bool:
        """
        Encerra um processo

        Args:
            pid: ID do processo
            force: True para kill forÃ§ado, False para terminate gracioso
            timeout: Tempo de espera para tÃ©rmino gracioso
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()

            if force:
                proc.kill()
                logger.info(
                    f"ðŸ’€ Processo {proc_name} (PID: {pid}) forÃ§ado a terminar"
                )
            else:
                proc.terminate()
                proc.wait(timeout=timeout)
                logger.info(
                    f"âœ‹ Processo {proc_name} (PID: {pid}) terminado graciosamente"
                )

            return True
        except psutil.NoSuchProcess:
            logger.warning(f"âš ï¸ Processo {pid} nÃ£o existe")
            return False
        except psutil.TimeoutExpired:
            logger.warning(f"âš ï¸ Timeout ao terminar processo {pid}, forÃ§ando...")
            try:
                proc.kill()
                return True
            except BaseException:
                return False
        except Exception as e:
            logger.error(f"âŒ Erro ao encerrar processo {pid}: {e}")
            return False

    def set_process_priority(self, pid: int, priority: ProcessPriority) -> bool:
        """
        Define prioridade de um processo

        Args:
            pid: ID do processo
            priority: ProcessPriority enum
        """
        try:
            proc = psutil.Process(pid)

            if hasattr(psutil, "WINDOWS"):
                # Windows usa nice() com valores de classe de prioridade
                proc.nice(priority.value)
            else:
                # Unix-like usa nice() com valores -20 a 19
                nice_value = 0
                if priority == ProcessPriority.REALTIME:
                    nice_value = -20
                elif priority == ProcessPriority.HIGH:
                    nice_value = -10
                elif priority == ProcessPriority.ABOVE_NORMAL:
                    nice_value = -5
                elif priority == ProcessPriority.NORMAL:
                    nice_value = 0
                elif priority == ProcessPriority.BELOW_NORMAL:
                    nice_value = 5
                elif priority == ProcessPriority.IDLE:
                    nice_value = 19
                proc.nice(nice_value)

            logger.info(
                f"âš–ï¸ Prioridade do processo {pid} alterada para {priority.name}"
            )
            return True
        except psutil.NoSuchProcess:
            logger.error(f"âŒ Processo {pid} nÃ£o existe")
            return False
        except psutil.AccessDenied:
            logger.error(
                f"âŒ Sem permissÃ£o para alterar prioridade do processo {pid}"
            )
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao definir prioridade: {e}")
            return False

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """InformaÃ§Ãµes detalhadas de um processo"""
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "exe": proc.exe(),
                    "cwd": proc.cwd(),
                    "cmdline": proc.cmdline(),
                    "username": proc.username(),
                    "create_time": datetime.fromtimestamp(
                        proc.create_time()
                    ).isoformat(),
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(interval=1),
                    "memory_percent": proc.memory_percent(),
                    "memory_info": proc.memory_info()._asdict(),
                    "num_threads": proc.num_threads(),
                    "nice": proc.nice(),
                }
        except psutil.NoSuchProcess:
            logger.error(f"âŒ Processo {pid} nÃ£o existe")
            return None
        except psutil.AccessDenied:
            logger.error(f"âŒ Acesso negado ao processo {pid}")
            return None
        except Exception as e:
            logger.error(f"âŒ Erro ao obter info do processo: {e}")
            return None

    # ==================== DISK HEALTH ====================

    def get_disk_smart_data(self, disk_path: str = "C:") -> Optional[Dict[str, Any]]:
        """
        ObtÃ©m dados S.M.A.R.T. do disco (via WMI)

        Args:
            disk_path: Caminho do disco (ex: "C:", "D:")
        """
        if not self.wmi_interface:
            logger.warning("âš ï¸ WMI nÃ£o disponÃ­vel para S.M.A.R.T.")
            return None

        try:
            # ObtÃ©m informaÃ§Ãµes do disco fÃ­sico
            for disk in self.wmi_interface.Win32_DiskDrive():
                smart_data = {
                    "model": disk.Model,
                    "serial_number": disk.SerialNumber,
                    "size_gb": (
                        round(int(disk.Size) / (1024**3), 2) if disk.Size else None
                    ),
                    "interface_type": disk.InterfaceType,
                    "media_type": disk.MediaType,
                    "status": disk.Status,
                    "availability": disk.Availability,
                    "partitions": disk.Partitions,
                }
                return smart_data
        except Exception as e:
            logger.error(f"âŒ Erro ao obter dados S.M.A.R.T.: {e}")
        return None

    def analyze_disk_space(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analisa uso de espaÃ§o em disco

        Args:
            path: Caminho do disco (None para detectar automaticamente)

        Returns:
            Dict com total, usado, livre, arquivos grandes, etc
        """
        if path is None:
            # Detectar disco principal automaticamente
            path = "C:\\" if os.name == "nt" else "/"  # Windows vs Unix-like

        try:
            usage = psutil.disk_usage(path)

            analysis = {
                "path": path,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent,
                "timestamp": datetime.now().isoformat(),
            }

            # Tenta encontrar arquivos grandes (opcional, pode ser lento)
            if os.path.exists(path):
                try:
                    large_files = []
                    for root, dirs, files in os.walk(path):
                        for file in files[:100]:  # Limita a 100 para nÃ£o travar
                            try:
                                filepath = os.path.join(root, file)
                                size = os.path.getsize(filepath)
                                if size > 100 * 1024 * 1024:  # > 100MB
                                    large_files.append(
                                        {
                                            "path": filepath,
                                            "size_mb": round(size / (1024**2), 2),
                                        }
                                    )
                            except (PermissionError, FileNotFoundError):
                                continue
                        if len(large_files) >= 10:  # Limita resultado
                            break

                    analysis["large_files"] = sorted(
                        large_files, key=lambda x: x["size_mb"], reverse=True
                    )[:10]
                except Exception as e:
                    logger.warning(
                        f"âš ï¸ NÃ£o foi possÃ­vel analisar arquivos grandes: {e}"
                    )

            return analysis
        except Exception as e:
            logger.error(f"âŒ Erro ao analisar disco: {e}")
            return {}

    def defragment_disk(self, drive_letter: str) -> bool:
        """
        Inicia desfragmentaÃ§Ã£o de disco (Windows 10+)

        Args:
            drive_letter: Letra da unidade (ex: "C")
        """
        if not self.is_admin:
            logger.error("âŒ DesfragmentaÃ§Ã£o requer privilÃ©gios administrativos")
            return False

        try:
            # Usa o desfragmentador do Windows
            result = subprocess.run(
                ["defrag", f"{drive_letter}:", "/O"],
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hora de timeout
            )

            if result.returncode == 0:
                logger.info(
                    f"âœ… DesfragmentaÃ§Ã£o do disco {drive_letter}: concluÃ­da"
                )
                return True
            else:
                logger.error(f"âŒ Erro na desfragmentaÃ§Ã£o: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.warning("âš ï¸ DesfragmentaÃ§Ã£o ultrapassou timeout de 1 hora")
            return False
        except Exception as e:
            logger.error(f"âŒ Erro ao desfragmentar: {e}")
            return False

    # ==================== SECURITY & PRIVILEGES ====================

    def _check_admin_rights(self) -> bool:
        """Verifica se o processo tem privilÃ©gios administrativos"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def request_admin_elevation(self) -> bool:
        """
        Solicita elevaÃ§Ã£o de privilÃ©gios (UAC)
        ATENÃ‡ÃƒO: Reinicia o script com privilÃ©gios elevados
        """
        if self.is_admin:
            logger.info("âœ… JÃ¡ executando com privilÃ©gios administrativos")
            return True

        try:
            logger.info("ðŸ” Solicitando elevaÃ§Ã£o de privilÃ©gios...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)  # Encerra instÃ¢ncia atual
        except Exception as e:
            logger.error(f"âŒ Erro ao solicitar elevaÃ§Ã£o: {e}")
            return False

    def get_user_privileges(self) -> List[str]:
        """Lista privilÃ©gios do usuÃ¡rio/processo atual"""
        privileges = []

        if not PYWIN32_AVAILABLE:
            logger.warning("âš ï¸ pywin32 nÃ£o disponÃ­vel para listar privilÃ©gios")
            return privileges

        try:
            # ObtÃ©m token do processo atual
            token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(), win32security.TOKEN_QUERY
            )

            # Lista privilÃ©gios
            privs = win32security.GetTokenInformation(
                token, win32security.TokenPrivileges
            )

            for priv_luid, priv_flags in privs:
                try:
                    priv_name = win32security.LookupPrivilegeName(None, priv_luid)
                    privileges.append(priv_name)
                except Exception:
                    continue

            win32api.CloseHandle(token)
        except Exception as e:
            logger.error(f"âŒ Erro ao obter privilÃ©gios: {e}")

        return privileges

    def check_uac_enabled(self) -> Optional[bool]:
        """Verifica se UAC estÃ¡ habilitado"""
        try:
            value = self.read_registry(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                "EnableLUA",
            )
            return bool(value) if value is not None else None
        except Exception as e:
            logger.error(f"Erro ao verificar UAC: {e}")
            return None

    # ==================== BROWSER & WEB ====================

    def open_browser(self, query: str = "", url: str = None) -> bool:
        """
        Abre o navegador padrÃ£o

        Args:
            query: Termo de pesquisa (Google/YouTube)
            url: URL direta (tem prioridade sobre query)
        """
        try:
            if url:
                target_url = url
            elif query:
                if "mÃºsica" in query.lower() or "tocar" in query.lower():
                    target_url = f"https://music.youtube.com/search?q={query}"
                else:
                    target_url = f"https://www.google.com/search?q={query}"
            else:
                target_url = "https://www.google.com"

            webbrowser.open(target_url)
            logger.info(f"ðŸŒ Navegador aberto: {target_url}")
            return True
        except Exception as e:
            logger.error(f"âŒ Falha ao abrir navegador: {e}")
            return False

    def get_foreground_window_info(self) -> Dict[str, Any]:
        """
        Retorna informaÃ§Ãµes sobre a janela atualmente em primeiro plano.
        """
        info = {"title": "Desconhecido", "process_name": "Desconhecido", "pid": 0}

        if not PYWIN32_AVAILABLE:
            return info

        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                info["title"] = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                info["pid"] = pid

                try:
                    proc = psutil.Process(pid)
                    info["process_name"] = proc.name()
                except BaseException:
                    pass
        except Exception as e:
            logger.debug(f"Erro ao obter info da janela em primeiro plano: {e}")

        return info

    # ==================== UTILITY METHODS ====================

    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Gera relatÃ³rio completo de saÃºde do sistema

        Returns:
            Dict com todas as mÃ©tricas importantes
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "is_admin": self.is_admin,
            "system_info": self.get_system_info(),
            "processes_count": len(psutil.pids()),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime_seconds": int(datetime.now().timestamp() - psutil.boot_time()),
        }

        # Adiciona alertas se necessÃ¡rio
        alerts = []
        if (
            report["system_info"].get("memory", {}).get("ram", {}).get("percent", 0)
            > 90
        ):
            alerts.append("âš ï¸ Uso de RAM crÃ­tico (>90%)")
        if report["system_info"].get("cpu", {}).get("usage_percent", 0) > 90:
            alerts.append("âš ï¸ Uso de CPU crÃ­tico (>90%)")

        for disk in report["system_info"].get("disk", []):
            if disk.get("percent", 0) > 90:
                alerts.append(
                    f"âš ï¸ Disco {disk.get('mountpoint')} quase cheio (>90%)"
                )

        report["alerts"] = alerts

        return report

    def export_system_report(self, filepath: Optional[str] = None) -> bool:
        """Exporta relatÃ³rio de sistema para arquivo JSON"""
        try:
            if not filepath:
                reports_dir = Path("data/system_reports")
                reports_dir.mkdir(parents=True, exist_ok=True)
                filepath = (
                    reports_dir
                    / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )

            report = self.get_system_health_report()

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"ðŸ“„ RelatÃ³rio exportado: {filepath}")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao exportar relatÃ³rio: {e}")
            return False


# ==================== SINGLETON PATTERN ====================

# InstÃ¢ncia global do gerenciador avanÃ§ado
device_manager = AdvancedDeviceManager()

# Manter compatibilidade com cÃ³digo antigo
__all__ = [
    "device_manager",
    "AdvancedDeviceManager",
    "PowerPlan",
    "ServiceAction",
    "ProcessPriority",
]
