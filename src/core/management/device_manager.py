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
- Serviços do Windows
- Segurança e Privilégios
- Monitoramento de Saúde do Sistema
"""

import logging
import os
import sys
import webbrowser
import subprocess
import winreg
import ctypes
from ctypes import cast, POINTER
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
from enum import Enum

# Imports principais
import psutil

# Imports opcionais com graceful degradation
try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False
    
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import win32api
    import win32con
    import win32security
    import win32process
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False

logger = logging.getLogger(__name__)

# ================== ENUMS ==================

class PowerPlan(Enum):
    """Planos de energia do Windows"""
    BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
    HIGH_PERFORMANCE = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    POWER_SAVER = "a1841308-3541-4fab-bc81-f71556f20b4a"

class ServiceAction(Enum):
    """Ações para serviços Windows"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    PAUSE = "pause"
    RESUME = "continue"

class ProcessPriority(Enum):
    """Prioridades de processos"""
    REALTIME = psutil.REALTIME_PRIORITY_CLASS if hasattr(psutil, 'REALTIME_PRIORITY_CLASS') else 256
    HIGH = psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, 'HIGH_PRIORITY_CLASS') else 128
    ABOVE_NORMAL = psutil.ABOVE_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'ABOVE_NORMAL_PRIORITY_CLASS') else 32768
    NORMAL = psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, 'NORMAL_PRIORITY_CLASS') else 32
    BELOW_NORMAL = psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS') else 16384
    IDLE = psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, 'IDLE_PRIORITY_CLASS') else 64

# ================== MAIN CLASS ==================

class AdvancedDeviceManager:
    """
    Gerenciador Avançado com Controle Total do Sistema Windows
    
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
        """Inicializa o gerenciador com verificações de dependências"""
        self.wmi_interface = None
        self.audio_interface = None
        self.is_admin = self._check_admin_rights()
        
        # Inicializa WMI se disponível
        if WMI_AVAILABLE:
            try:
                self.wmi_interface = wmi.WMI()
            except Exception as e:
                logger.warning(f"⚠️ Falha ao inicializar WMI: {e}")
        
        # Inicializa interface de áudio se disponível
        if PYCAW_AVAILABLE:
            try:
                self.audio_interface = self._get_audio_interface()
            except Exception as e:
                logger.warning(f"⚠️ Falha ao inicializar controle de áudio: {e}")
        
        logger.info(f"🎛️ DeviceManager inicializado (Admin: {self.is_admin})")
    
    # ==================== HARDWARE MONITORING ====================
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Coleta informações completas do sistema
        
        Returns:
            Dict com CPU, RAM, Disk, Network, GPU, Battery info
        """
        try:
            info = {
                'cpu': self._get_cpu_info(),
                'memory': self._get_memory_info(),
                'disk': self._get_disk_info(),
                'network': self.get_network_info(),
                'gpu': self._get_gpu_info(),
                'battery': self._get_battery_info(),
                'timestamp': datetime.now().isoformat()
            }
            return info
        except Exception as e:
            logger.error(f"❌ Erro ao coletar info do sistema: {e}")
            return {}
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Informações detalhadas da CPU"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                'cores_physical': psutil.cpu_count(logical=False),
                'cores_logical': psutil.cpu_count(logical=True),
                'usage_percent': psutil.cpu_percent(interval=1),
                'usage_per_core': psutil.cpu_percent(interval=1, percpu=True),
                'frequency_mhz': cpu_freq.current if cpu_freq else None,
                'frequency_min': cpu_freq.min if cpu_freq else None,
                'frequency_max': cpu_freq.max if cpu_freq else None,
                'temperature_celsius': self._get_cpu_temperature()
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
                    for name in ['coretemp', 'k10temp', 'cpu_thermal']:
                        if name in temps and temps[name]:
                            return temps[name][0].current
        except Exception:
            pass
        return None
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Informações de memória RAM e SWAP"""
        try:
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'ram': {
                    'total_gb': round(vm.total / (1024**3), 2),
                    'available_gb': round(vm.available / (1024**3), 2),
                    'used_gb': round(vm.used / (1024**3), 2),
                    'percent': vm.percent
                },
                'swap': {
                    'total_gb': round(swap.total / (1024**3), 2),
                    'used_gb': round(swap.used / (1024**3), 2),
                    'free_gb': round(swap.free / (1024**3), 2),
                    'percent': swap.percent
                }
            }
        except Exception as e:
            logger.error(f"Erro ao obter info de memória: {e}")
            return {}
    
    def _get_disk_info(self) -> List[Dict[str, Any]]:
        """Informações de todos os discos"""
        disks = []
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
        except Exception as e:
            logger.error(f"Erro ao obter info de discos: {e}")
        return disks
    
    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Informações das GPUs (via WMI)"""
        gpus = []
        if not self.wmi_interface:
            return gpus
        
        try:
            for gpu in self.wmi_interface.Win32_VideoController():
                gpus.append({
                    'name': gpu.Name,
                    'driver_version': gpu.DriverVersion,
                    'video_memory_mb': int(gpu.AdapterRAM / (1024**2)) if gpu.AdapterRAM else None,
                    'status': gpu.Status,
                    'availability': gpu.Availability
                })
        except Exception as e:
            logger.error(f"Erro ao obter info GPU: {e}")
        return gpus
    
    def _get_battery_info(self) -> Optional[Dict[str, Any]]:
        """Informações da bateria (se houver)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left_seconds': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except Exception as e:
            logger.error(f"Erro ao obter info de bateria: {e}")
        return None
    
    # ==================== NETWORK CONTROL ====================
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Informações completas de rede
        
        Returns:
            Dict com interfaces, conexões ativas e estatísticas
        """
        try:
            info = {
                'interfaces': self.list_network_interfaces(),
                'connections': self.list_network_connections(),
                'stats': self._get_network_stats()
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
                    'name': iface_name,
                    'is_up': stats.isup if stats else False,
                    'speed_mbps': stats.speed if stats else None,
                    'addresses': []
                }
                
                for addr in addrs:
                    iface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                interfaces.append(iface_info)
        except Exception as e:
            logger.error(f"Erro ao listar interfaces de rede: {e}")
        return interfaces
    
    def list_network_connections(self, kind: str = 'inet') -> List[Dict[str, Any]]:
        """
        Lista conexões de rede ativas
        
        Args:
            kind: Tipo de conexão ('inet', 'tcp', 'udp', etc)
        """
        connections = []
        try:
            for conn in psutil.net_connections(kind=kind):
                connections.append({
                    'fd': conn.fd,
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                })
        except (psutil.AccessDenied, PermissionError):
            logger.warning("⚠️ Sem permissão para listar todas as conexões")
        except Exception as e:
            logger.error(f"Erro ao listar conexões: {e}")
        return connections
    
    def _get_network_stats(self) -> Dict[str, Any]:
        """Estatísticas de tráfego de rede"""
        try:
            stats = psutil.net_io_counters()
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errors_in': stats.errin,
                'errors_out': stats.errout,
                'drops_in': stats.dropin,
                'drops_out': stats.dropout
            }
        except Exception as e:
            logger.error(f"Erro ao obter stats de rede: {e}")
            return {}
    
    def enable_network_interface(self, interface_name: str, enable: bool = True) -> bool:
        """
        Habilita/desabilita interface de rede
        
        Args:
            interface_name: Nome da interface
            enable: True para habilitar, False para desabilitar
            
        Returns:
            True se bem-sucedido
        """
        if not self.is_admin:
            logger.error("❌ Requer privilégios administrativos")
            return False
        
        try:
            action = "enable" if enable else "disable"
            result = subprocess.run(
                ['netsh', 'interface', 'set', 'interface', interface_name, action],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"✅ Interface {interface_name} {action}d")
                return True
            else:
                logger.error(f"❌ Erro ao {action} interface: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao modificar interface: {e}")
            return False
    
    def block_process_network(self, pid: int, program_path: Optional[str] = None) -> bool:
        """
        Bloqueia conexões de rede de um processo via Firewall do Windows
        
        Args:
            pid: ID do processo
            program_path: Caminho do executável (opcional, será detectado)
            
        Returns:
            True se bloqueado com sucesso
        """
        if not self.is_admin:
            logger.error("❌ Requer privilégios administrativos")
            return False
        
        try:
            # Obtém caminho do executável se não fornecido
            if not program_path:
                proc = psutil.Process(pid)
                program_path = proc.exe()
            
            rule_name = f"JARVIS_BLOCK_{pid}_{Path(program_path).stem}"
            
            # Cria regra de firewall
            result = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={rule_name}',
                'dir=out',
                'action=block',
                f'program={program_path}'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                logger.info(f"🔥 Processo {pid} bloqueado no firewall")
                return True
            else:
                logger.error(f"❌ Erro ao criar regra de firewall: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao bloquear processo: {e}")
            return False
    
    def unblock_process_network(self, rule_name: str) -> bool:
        """Remove regra de bloqueio do firewall"""
        if not self.is_admin:
            logger.error("❌ Requer privilégios administrativos")
            return False
        
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name={rule_name}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"❌ Erro ao remover regra de firewall: {e}")
            return False
    
    # ==================== POWER MANAGEMENT ====================
    
    def shutdown(self, force: bool = False, timeout: int = 30) -> bool:
        """
        Desliga o sistema
        
        Args:
            force: Força o desligamento sem salvar
            timeout: Tempo em segundos até o desligamento
            
        Returns:
            True se comando foi executado
        """
        try:
            if PYWIN32_AVAILABLE and timeout == 0:
                flags = win32con.EWX_SHUTDOWN
                if force:
                    flags |= win32con.EWX_FORCE
                win32api.ExitWindowsEx(flags, 0)
                logger.info("🔌 Sistema desligando...")
                return True
            else:
                # Fallback usando shutdown.exe
                cmd = ['shutdown', '/s']
                if force:
                    cmd.append('/f')
                if timeout > 0:
                    cmd.extend(['/t', str(timeout)])
                else:
                    cmd.extend(['/t', '0'])
                
                subprocess.Popen(cmd)
                logger.info(f"🔌 Desligamento agendado em {timeout}s")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao desligar sistema: {e}")
            return False
    
    def restart(self, force: bool = False, timeout: int = 30) -> bool:
        """
        Reinicia o sistema
        
        Args:
            force: Força o reinício sem salvar
            timeout: Tempo em segundos até o reinício
        """
        try:
            if PYWIN32_AVAILABLE and timeout == 0:
                flags = win32con.EWX_REBOOT
                if force:
                    flags |= win32con.EWX_FORCE
                win32api.ExitWindowsEx(flags, 0)
                logger.info("🔄 Sistema reiniciando...")
                return True
            else:
                cmd = ['shutdown', '/r']
                if force:
                    cmd.append('/f')
                if timeout > 0:
                    cmd.extend(['/t', str(timeout)])
                else:
                    cmd.extend(['/t', '0'])
                
                subprocess.Popen(cmd)
                logger.info(f"🔄 Reinício agendado em {timeout}s")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao reiniciar sistema: {e}")
            return False
    
    def cancel_shutdown(self) -> bool:
        """Cancela shutdown/restart agendado"""
        try:
            result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Shutdown cancelado")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao cancelar shutdown: {e}")
            return False
    
    def sleep(self) -> bool:
        """Coloca o sistema em modo sleep"""
        try:
            if PYWIN32_AVAILABLE:
                ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
                logger.info("💤 Sistema entrando em sleep...")
                return True
            else:
                # Fallback
                subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao colocar sistema em sleep: {e}")
            return False
    
    def hibernate(self) -> bool:
        """Hiberna o sistema"""
        try:
            if PYWIN32_AVAILABLE:
                ctypes.windll.powrprof.SetSuspendState(1, 1, 0)
                logger.info("💤 Sistema hibernando...")
                return True
            else:
                subprocess.run(['shutdown', '/h'])
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao hibernar sistema: {e}")
            return False
    
    def set_power_plan(self, plan: PowerPlan) -> bool:
        """
        Define o plano de energia ativo
        
        Args:
            plan: PowerPlan enum (BALANCED, HIGH_PERFORMANCE, POWER_SAVER)
        """
        try:
            result = subprocess.run(
                ['powercfg', '/setactive', plan.value],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"⚡ Plano de energia alterado para {plan.name}")
                return True
            else:
                logger.error(f"❌ Erro ao definir plano: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao definir plano de energia: {e}")
            return False
    
    def get_active_power_plan(self) -> Optional[str]:
        """Retorna o GUID do plano de energia ativo"""
        try:
            result = subprocess.run(
                ['powercfg', '/getactivescheme'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse output: "Power Scheme GUID: <guid> (Name)"
                output = result.stdout
                if 'GUID:' in output:
                    guid = output.split('GUID:')[1].split('(')[0].strip()
                    return guid
        except Exception as e:
            logger.error(f"Erro ao obter plano ativo: {e}")
        return None
    
    # ==================== WINDOWS REGISTRY ====================
    
    def read_registry(self, hive: int, key_path: str, value_name: str) -> Optional[Any]:
        """
        Lê valor do registro do Windows
        
        Args:
            hive: winreg.HKEY_* (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc)
            key_path: Caminho da chave (ex: "Software\\Microsoft\\Windows")
            value_name: Nome do valor
            
        Returns:
            Valor lido ou None se não encontrado
        """
        try:
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
            value, reg_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            logger.info(f"📖 Lido do registro: {key_path}\\{value_name}")
            return value
        except FileNotFoundError:
            logger.warning(f"⚠️ Chave ou valor não encontrado: {key_path}\\{value_name}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao ler registro: {e}")
            return None
    
    def write_registry(self, hive: int, key_path: str, value_name: str, 
                      value: Any, value_type: int = winreg.REG_SZ,
                      backup: bool = True) -> bool:
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
            logger.warning("⚠️ Modificação do registro pode requerer privilégios administrativos")
        
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
            
            logger.info(f"✏️ Escrito no registro: {key_path}\\{value_name}")
            return True
        except PermissionError:
            logger.error("❌ Sem permissão para modificar registro (requer admin)")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao escrever no registro: {e}")
            return False
    
    def _backup_registry_value(self, hive: int, key_path: str, 
                               value_name: str, value: Any) -> None:
        """Faz backup de valor do registro"""
        try:
            backup_dir = Path("data/registry_backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'hive': hive,
                'key_path': key_path,
                'value_name': value_name,
                'old_value': str(value)
            }
            
            filename = f"registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"💾 Backup do registro salvo: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao fazer backup do registro: {e}")
    
    def delete_registry_value(self, hive: int, key_path: str, value_name: str,
                             backup: bool = True) -> bool:
        """Remove um valor do registro (com backup opcional)"""
        if not self.is_admin:
            logger.warning("⚠️ Deleção do registro pode requerer privilégios administrativos")
        
        try:
            # Backup se solicitado
            if backup:
                old_value = self.read_registry(hive, key_path, value_name)
                if old_value is not None:
                    self._backup_registry_value(hive, key_path, value_name, old_value)
            
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)
            
            logger.info(f"🗑️ Valor removido do registro: {key_path}\\{value_name}")
            return True
        except FileNotFoundError:
            logger.warning(f"⚠️ Valor não existe: {key_path}\\{value_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao deletar valor: {e}")
            return False
    
    # ==================== WINDOWS SERVICES ====================
    
    def list_services(self) -> List[Dict[str, Any]]:
        """Lista todos os serviços do Windows"""
        services = []
        
        if self.wmi_interface:
            try:
                for service in self.wmi_interface.Win32_Service():
                    services.append({
                        'name': service.Name,
                        'display_name': service.DisplayName,
                        'state': service.State,
                        'start_mode': service.StartMode,
                        'status': service.Status,
                        'path_name': service.PathName,
                        'process_id': service.ProcessId
                    })
            except Exception as e:
                logger.error(f"Erro ao listar serviços via WMI: {e}")
        else:
            # Fallback: usa sc query
            try:
                result = subprocess.run(
                    ['sc', 'query', 'state=', 'all'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Parse output (simplificado)
                logger.info("📋 Serviços listados via sc query")
            except Exception as e:
                logger.error(f"Erro ao listar serviços: {e}")
        
        return services
    
    def control_service(self, service_name: str, action: ServiceAction) -> bool:
        """
        Controla um serviço do Windows
        
        Args:
            service_name: Nome do serviço
            action: ServiceAction enum (START, STOP, RESTART, etc)
            
        Returns:
            True se comando foi bem-sucedido
        """
        if not self.is_admin:
            logger.error("❌ Controle de serviços requer privilégios administrativos")
            return False
        
        try:
            if action == ServiceAction.RESTART:
                # Restart = Stop + Start
                self.control_service(service_name, ServiceAction.STOP)
                import time
                time.sleep(2)
                return self.control_service(service_name, ServiceAction.START)
            
            result = subprocess.run(
                ['net', action.value, service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Serviço {service_name} - {action.value}")
                return True
            else:
                # Pode já estar no estado desejado
                if "already" in result.stdout.lower() or "já" in result.stdout.lower():
                    logger.info(f"ℹ️ Serviço {service_name} já está no estado desejado")
                    return True
                logger.error(f"❌ Erro ao controlar serviço: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao controlar serviço {service_name}: {e}")
            return False
    
    def get_service_dependencies(self, service_name: str) -> List[str]:
        """Retorna lista de dependências de um serviço"""
        dependencies = []
        try:
            result = subprocess.run(
                ['sc', 'enumdepend', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse output para extrair nomes de serviços
                for line in result.stdout.split('\n'):
                    if 'SERVICE_NAME:' in line:
                        dep_name = line.split(':')[1].strip()
                        dependencies.append(dep_name)
        except Exception as e:
            logger.error(f"Erro ao obter dependências do serviço: {e}")
        return dependencies
    
    # ==================== DISPLAY CONTROL ====================
    
    def set_brightness(self, level: int) -> bool:
        """
        Ajusta o brilho do monitor (0-100)
        
        Args:
            level: Nível de brilho (0-100)
        """
        if not SBC_AVAILABLE:
            logger.warning("⚠️ screen_brightness_control não instalado.")
            return False
        try:
            level = max(0, min(100, level))
            sbc.set_brightness(level)
            logger.info(f"💡 Brilho ajustado para {level}%")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao ajustar brilho: {e}")
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
        """Informações dos monitores conectados"""
        displays = []
        
        if self.wmi_interface:
            try:
                for monitor in self.wmi_interface.Win32_DesktopMonitor():
                    displays.append({
                        'name': monitor.Name,
                        'device_id': monitor.DeviceID,
                        'pnp_device_id': monitor.PNPDeviceID,
                        'monitor_manufacturer': monitor.MonitorManufacturer,
                        'monitor_type': monitor.MonitorType,
                        'screen_width': monitor.ScreenWidth,
                        'screen_height': monitor.ScreenHeight,
                        'pixels_per_x_logical_inch': monitor.PixelsPerXLogicalInch,
                        'pixels_per_y_logical_inch': monitor.PixelsPerYLogicalInch
                    })
            except Exception as e:
                logger.error(f"Erro ao obter info de displays: {e}")
        
        return displays
    
    def set_display_resolution(self, width: int, height: int, 
                              refresh_rate: int = 60) -> bool:
        """
        Altera resolução e taxa de atualização do display
        
        Args:
            width: Largura em pixels
            height: Altura em pixels
            refresh_rate: Taxa de atualização em Hz
        """
        if not PYWIN32_AVAILABLE:
            logger.error("❌ pywin32 não disponível")
            return False
        
        try:
            devmode = win32api.EnumDisplaySettings(None, 0)
            devmode.PelsWidth = width
            devmode.PelsHeight = height
            devmode.DisplayFrequency = refresh_rate
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYFREQUENCY
            
            result = win32api.ChangeDisplaySettings(devmode, 0)
            
            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                logger.info(f"🖥️ Resolução alterada para {width}x{height}@{refresh_rate}Hz")
                return True
            else:
                error_msgs = {
                    win32con.DISP_CHANGE_RESTART: "Requer reinicialização",
                    win32con.DISP_CHANGE_BADFLAGS: "Flags inválidas",
                    win32con.DISP_CHANGE_BADPARAM: "Parâmetros inválidos",
                    win32con.DISP_CHANGE_FAILED: "Falha ao alterar",
                    win32con.DISP_CHANGE_BADMODE: "Modo não suportado"
                }
                logger.error(f"❌ {error_msgs.get(result, 'Erro desconhecido')}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao alterar resolução: {e}")
            return False
    
    # ==================== AUDIO CONTROL ====================
    
    def _get_audio_interface(self):
        """Obtém interface de controle de áudio do Windows"""
        try:
            devices = AudioUtilities.GetSpeakers()
            # pycaw moderno retorna AudioDevice wrapper com .EndpointVolume
            if hasattr(devices, 'EndpointVolume'):
                return devices.EndpointVolume
            # pycaw legado retorna IMMDevice COM com .Activate()
            elif hasattr(devices, 'Activate'):
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                return cast(interface, POINTER(IAudioEndpointVolume))
            # Fallback: tentar _dev interno
            elif hasattr(devices, '_dev') and hasattr(devices._dev, 'Activate'):
                interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                return cast(interface, POINTER(IAudioEndpointVolume))
            else:
                logger.warning("⚠️ Não foi possível obter interface de volume (API pycaw desconhecida)")
                return None
        except Exception as e:
            logger.error(f"Erro ao obter interface de áudio: {e}")
            return None
    
    def set_volume(self, level: float) -> bool:
        """
        Define volume do sistema (0.0 a 1.0)
        
        Args:
            level: Nível de volume (0.0 = mudo, 1.0 = máximo)
        """
        if self.audio_interface:
            try:
                level = max(0.0, min(1.0, level))
                self.audio_interface.SetMasterVolumeLevelScalar(level, None)
                logger.info(f"🔊 Volume ajustado para {int(level * 100)}%")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao definir volume: {e}")
                return False
        else:
            # Fallback PowerShell (menos preciso)
            try:
                level_percent = int(level * 100)
                level_percent = max(0, min(100, level_percent))
                cmd = f"(new-object -com wscript.shell).SendKeys([char]174)*50; (new-object -com wscript.shell).SendKeys([char]175)*{level_percent//2}"
                subprocess.run(["powershell", "-Command", cmd], capture_output=True, timeout=5)
                logger.info(f"🔊 Volume ajustado para aproximadamente {level_percent}%")
                return True
            except Exception as e:
                logger.error(f"❌ Falha ao ajustar volume: {e}")
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
        """
        Silencia/ativa áudio do sistema
        
        Args:
            muted: True para mutar, False para desmutar
        """
        if self.audio_interface:
            try:
                self.audio_interface.SetMute(1 if muted else 0, None)
                logger.info(f"🔇 Áudio {'mutado' if muted else 'desmutado'}")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao mutar áudio: {e}")
                return False
        return False
    
    def is_muted(self) -> Optional[bool]:
        """Verifica se áudio está mutado"""
        if self.audio_interface:
            try:
                return bool(self.audio_interface.GetMute())
            except Exception as e:
                logger.error(f"Erro ao verificar mute: {e}")
        return None
    
    def list_audio_devices(self) -> List[Dict[str, Any]]:
        """Lista dispositivos de áudio disponíveis"""
        devices = []
        if PYCAW_AVAILABLE:
            try:
                for device in AudioUtilities.GetAllDevices():
                    devices.append({
                        'id': device.id,
                        'name': device.FriendlyName,
                        'state': str(device.state)
                    })
            except Exception as e:
                logger.error(f"Erro ao listar dispositivos de áudio: {e}")
        return devices
    
    # ==================== PROCESS MANAGEMENT ====================
    
    def list_processes(self, sort_by: str = 'cpu') -> List[Dict[str, Any]]:
        """
        Lista todos os processos do sistema
        
        Args:
            sort_by: Ordenar por 'cpu', 'memory', 'name'
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 
                                        'memory_percent', 'status', 'create_time']):
            try:
                info = proc.info
                info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Ordenação
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x.get('name', '').lower())
        
        return processes
    
    def kill_process(self, pid: int, force: bool = False, timeout: int = 5) -> bool:
        """
        Encerra um processo
        
        Args:
            pid: ID do processo
            force: True para kill forçado, False para terminate gracioso
            timeout: Tempo de espera para término gracioso
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            if force:
                proc.kill()
                logger.info(f"💀 Processo {proc_name} (PID: {pid}) forçado a terminar")
            else:
                proc.terminate()
                proc.wait(timeout=timeout)
                logger.info(f"✋ Processo {proc_name} (PID: {pid}) terminado graciosamente")
            
            return True
        except psutil.NoSuchProcess:
            logger.warning(f"⚠️ Processo {pid} não existe")
            return False
        except psutil.TimeoutExpired:
            logger.warning(f"⚠️ Timeout ao terminar processo {pid}, forçando...")
            try:
                proc.kill()
                return True
            except:
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar processo {pid}: {e}")
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
            
            if hasattr(psutil, 'WINDOWS'):
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
            
            logger.info(f"⚖️ Prioridade do processo {pid} alterada para {priority.name}")
            return True
        except psutil.NoSuchProcess:
            logger.error(f"❌ Processo {pid} não existe")
            return False
        except psutil.AccessDenied:
            logger.error(f"❌ Sem permissão para alterar prioridade do processo {pid}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao definir prioridade: {e}")
            return False
    
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Informações detalhadas de um processo"""
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'exe': proc.exe(),
                    'cwd': proc.cwd(),
                    'cmdline': proc.cmdline(),
                    'username': proc.username(),
                    'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
                    'status': proc.status(),
                    'cpu_percent': proc.cpu_percent(interval=1),
                    'memory_percent': proc.memory_percent(),
                    'memory_info': proc.memory_info()._asdict(),
                    'num_threads': proc.num_threads(),
                    'nice': proc.nice()
                }
        except psutil.NoSuchProcess:
            logger.error(f"❌ Processo {pid} não existe")
            return None
        except psutil.AccessDenied:
            logger.error(f"❌ Acesso negado ao processo {pid}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao obter info do processo: {e}")
            return None
    
    # ==================== DISK HEALTH ====================
    
    def get_disk_smart_data(self, disk_path: str = "C:") -> Optional[Dict[str, Any]]:
        """
        Obtém dados S.M.A.R.T. do disco (via WMI)
        
        Args:
            disk_path: Caminho do disco (ex: "C:", "D:")
        """
        if not self.wmi_interface:
            logger.warning("⚠️ WMI não disponível para S.M.A.R.T.")
            return None
        
        try:
            # Obtém informações do disco físico
            for disk in self.wmi_interface.Win32_DiskDrive():
                smart_data = {
                    'model': disk.Model,
                    'serial_number': disk.SerialNumber,
                    'size_gb': round(int(disk.Size) / (1024**3), 2) if disk.Size else None,
                    'interface_type': disk.InterfaceType,
                    'media_type': disk.MediaType,
                    'status': disk.Status,
                    'availability': disk.Availability,
                    'partitions': disk.Partitions
                }
                return smart_data
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados S.M.A.R.T.: {e}")
        return None
    
    def analyze_disk_space(self, path: str = "C:\\") -> Dict[str, Any]:
        """
        Analisa uso de espaço em disco
        
        Returns:
            Dict com total, usado, livre, arquivos grandes, etc
        """
        try:
            usage = psutil.disk_usage(path)
            
            analysis = {
                'path': path,
                'total_gb': round(usage.total / (1024**3), 2),
                'used_gb': round(usage.used / (1024**3), 2),
                'free_gb': round(usage.free / (1024**3), 2),
                'percent': usage.percent,
                'timestamp': datetime.now().isoformat()
            }
            
            # Tenta encontrar arquivos grandes (opcional, pode ser lento)
            if os.path.exists(path):
                try:
                    large_files = []
                    for root, dirs, files in os.walk(path):
                        for file in files[:100]:  # Limita a 100 para não travar
                            try:
                                filepath = os.path.join(root, file)
                                size = os.path.getsize(filepath)
                                if size > 100 * 1024 * 1024:  # > 100MB
                                    large_files.append({
                                        'path': filepath,
                                        'size_mb': round(size / (1024**2), 2)
                                    })
                            except (PermissionError, FileNotFoundError):
                                continue
                        if len(large_files) >= 10:  # Limita resultado
                            break
                    
                    analysis['large_files'] = sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:10]
                except Exception as e:
                    logger.warning(f"⚠️ Não foi possível analisar arquivos grandes: {e}")
            
            return analysis
        except Exception as e:
            logger.error(f"❌ Erro ao analisar disco: {e}")
            return {}
    
    def defragment_disk(self, drive_letter: str) -> bool:
        """
        Inicia desfragmentação de disco (Windows 10+)
        
        Args:
            drive_letter: Letra da unidade (ex: "C")
        """
        if not self.is_admin:
            logger.error("❌ Desfragmentação requer privilégios administrativos")
            return False
        
        try:
            # Usa o desfragmentador do Windows
            result = subprocess.run(
                ['defrag', f'{drive_letter}:', '/O'],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora de timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Desfragmentação do disco {drive_letter}: concluída")
                return True
            else:
                logger.error(f"❌ Erro na desfragmentação: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Desfragmentação ultrapassou timeout de 1 hora")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao desfragmentar: {e}")
            return False
    
    # ==================== SECURITY & PRIVILEGES ====================
    
    def _check_admin_rights(self) -> bool:
        """Verifica se o processo tem privilégios administrativos"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def request_admin_elevation(self) -> bool:
        """
        Solicita elevação de privilégios (UAC)
        ATENÇÃO: Reinicia o script com privilégios elevados
        """
        if self.is_admin:
            logger.info("✅ Já executando com privilégios administrativos")
            return True
        
        try:
            logger.info("🔐 Solicitando elevação de privilégios...")
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                " ".join(sys.argv), 
                None, 
                1
            )
            sys.exit(0)  # Encerra instância atual
        except Exception as e:
            logger.error(f"❌ Erro ao solicitar elevação: {e}")
            return False
    
    def get_user_privileges(self) -> List[str]:
        """Lista privilégios do usuário/processo atual"""
        privileges = []
        
        if not PYWIN32_AVAILABLE:
            logger.warning("⚠️ pywin32 não disponível para listar privilégios")
            return privileges
        
        try:
            # Obtém token do processo atual
            token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32security.TOKEN_QUERY
            )
            
            # Lista privilégios
            privs = win32security.GetTokenInformation(
                token, 
                win32security.TokenPrivileges
            )
            
            for priv_luid, priv_flags in privs:
                try:
                    priv_name = win32security.LookupPrivilegeName(None, priv_luid)
                    privileges.append(priv_name)
                except Exception:
                    continue
            
            win32api.CloseHandle(token)
        except Exception as e:
            logger.error(f"❌ Erro ao obter privilégios: {e}")
        
        return privileges
    
    def check_uac_enabled(self) -> Optional[bool]:
        """Verifica se UAC está habilitado"""
        try:
            value = self.read_registry(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                "EnableLUA"
            )
            return bool(value) if value is not None else None
        except Exception as e:
            logger.error(f"Erro ao verificar UAC: {e}")
            return None
    
    # ==================== BROWSER & WEB ====================
    
    def open_browser(self, query: str = "", url: str = None) -> bool:
        """
        Abre o navegador padrão
        
        Args:
            query: Termo de pesquisa (Google/YouTube)
            url: URL direta (tem prioridade sobre query)
        """
        try:
            if url:
                target_url = url
            elif query:
                if "música" in query.lower() or "tocar" in query.lower():
                    target_url = f"https://music.youtube.com/search?q={query}"
                else:
                    target_url = f"https://www.google.com/search?q={query}"
            else:
                target_url = "https://www.google.com"
            
            webbrowser.open(target_url)
            logger.info(f"🌐 Navegador aberto: {target_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao abrir navegador: {e}")
            return False
    
    # ==================== UTILITY METHODS ====================
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de saúde do sistema
        
        Returns:
            Dict com todas as métricas importantes
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'is_admin': self.is_admin,
            'system_info': self.get_system_info(),
            'processes_count': len(psutil.pids()),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'uptime_seconds': int(datetime.now().timestamp() - psutil.boot_time())
        }
        
        # Adiciona alertas se necessário
        alerts = []
        if report['system_info'].get('memory', {}).get('ram', {}).get('percent', 0) > 90:
            alerts.append("⚠️ Uso de RAM crítico (>90%)")
        if report['system_info'].get('cpu', {}).get('usage_percent', 0) > 90:
            alerts.append("⚠️ Uso de CPU crítico (>90%)")
        
        for disk in report['system_info'].get('disk', []):
            if disk.get('percent', 0) > 90:
                alerts.append(f"⚠️ Disco {disk.get('mountpoint')} quase cheio (>90%)")
        
        report['alerts'] = alerts
        
        return report
    
    def export_system_report(self, filepath: Optional[str] = None) -> bool:
        """Exporta relatório de sistema para arquivo JSON"""
        try:
            if not filepath:
                reports_dir = Path("data/system_reports")
                reports_dir.mkdir(parents=True, exist_ok=True)
                filepath = reports_dir / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report = self.get_system_health_report()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Relatório exportado: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao exportar relatório: {e}")
            return False

# ==================== SINGLETON PATTERN ====================

# Instância global do gerenciador avançado
device_manager = AdvancedDeviceManager()

# Manter compatibilidade com código antigo
__all__ = ['device_manager', 'AdvancedDeviceManager', 'PowerPlan', 'ServiceAction', 'ProcessPriority']
