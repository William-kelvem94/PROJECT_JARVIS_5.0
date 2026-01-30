"""
System Controller - Controle Total do Sistema Operacional
Permite ao JARVIS controlar Windows, Ubuntu e Android
"""

import os
import platform
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from core.logger import logger


class SystemControllerBase:
    """Classe base para controladores de sistema."""
    
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        logger.info(f"System Controller inicializado: {self.system} ({self.machine})")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Executa comando no sistema."""
        raise NotImplementedError
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema."""
        raise NotImplementedError


class WindowsController(SystemControllerBase):
    """Controlador para Windows."""
    
    def __init__(self):
        super().__init__()
        self.powershell_available = self._check_powershell()
    
    def _check_powershell(self) -> bool:
        """Verifica se PowerShell está disponível."""
        try:
            subprocess.run(['powershell', '-Command', 'echo test'], 
                         capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def execute_command(self, command: str, use_powershell: bool = True) -> Dict[str, Any]:
        """
        Executa comando no Windows.
        
        Args:
            command: Comando a executar
            use_powershell: Se True, usa PowerShell, senão usa CMD
        """
        try:
            if use_powershell and self.powershell_available:
                result = subprocess.run(
                    ['powershell', '-Command', command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Abre aplicativo no Windows."""
        apps_map = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'explorer': 'explorer.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'vscode': 'code.exe',
        }
        
        app_executable = apps_map.get(app_name.lower(), app_name)
        return self.execute_command(f'Start-Process {app_executable}')
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Lista processos em execução."""
        cmd = "Get-Process | Select-Object Name, Id, CPU | ConvertTo-Json"
        result = self.execute_command(cmd)
        
        if result['success']:
            try:
                processes = json.loads(result['output'])
                return processes if isinstance(processes, list) else [processes]
            except:
                return []
        return []
    
    def kill_process(self, process_name: str) -> Dict[str, Any]:
        """Encerra processo por nome."""
        return self.execute_command(f'Stop-Process -Name {process_name} -Force')
    
    def get_system_info(self) -> Dict[str, Any]:
        """Informações detalhadas do sistema Windows."""
        info = {
            'system': self.system,
            'machine': self.machine,
            'version': platform.version(),
            'processor': platform.processor(),
        }
        
        # CPU e memória via PowerShell
        cpu_cmd = "Get-WmiObject Win32_Processor | Select-Object LoadPercentage | ConvertTo-Json"
        mem_cmd = "Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | ConvertTo-Json"
        
        cpu_result = self.execute_command(cpu_cmd)
        if cpu_result['success']:
            try:
                cpu_data = json.loads(cpu_result['output'])
                info['cpu_usage'] = cpu_data.get('LoadPercentage', 0)
            except:
                pass
        
        mem_result = self.execute_command(mem_cmd)
        if mem_result['success']:
            try:
                mem_data = json.loads(mem_result['output'])
                total = mem_data.get('TotalVisibleMemorySize', 0)
                free = mem_data.get('FreePhysicalMemory', 0)
                info['memory'] = {
                    'total_mb': total / 1024,
                    'free_mb': free / 1024,
                    'used_mb': (total - free) / 1024
                }
            except:
                pass
        
        return info
    
    def set_volume(self, level: int) -> Dict[str, Any]:
        """Define volume do sistema (0-100)."""
        level = max(0, min(100, level))
        cmd = f"[Audio]::Volume = {level / 100}"
        return self.execute_command(cmd)
    
    def take_screenshot(self, path: str) -> Dict[str, Any]:
        """Tira screenshot."""
        cmd = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
        $bitmap.Save('{path}')
        """
        return self.execute_command(cmd)


class LinuxController(SystemControllerBase):
    """Controlador para Linux/Ubuntu."""
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Executa comando no Linux."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Abre aplicativo no Linux."""
        apps_map = {
            'terminal': 'gnome-terminal',
            'firefox': 'firefox',
            'chrome': 'google-chrome',
            'vscode': 'code',
            'nautilus': 'nautilus',
            'files': 'nautilus',
            'calculator': 'gnome-calculator',
            'text-editor': 'gedit',
        }
        
        app_command = apps_map.get(app_name.lower(), app_name)
        return self.execute_command(f'{app_command} &')
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Lista processos em execução."""
        result = self.execute_command("ps aux --sort=-%cpu | head -20")
        
        if result['success']:
            lines = result['output'].split('\n')[1:]  # Skip header
            processes = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': ' '.join(parts[10:])
                        })
            return processes
        return []
    
    def kill_process(self, process_name: str) -> Dict[str, Any]:
        """Encerra processo por nome."""
        return self.execute_command(f'pkill -f {process_name}')
    
    def get_system_info(self) -> Dict[str, Any]:
        """Informações detalhadas do sistema Linux."""
        info = {
            'system': self.system,
            'machine': self.machine,
            'version': platform.version(),
            'processor': platform.processor(),
        }
        
        # CPU usage
        cpu_result = self.execute_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        if cpu_result['success']:
            try:
                info['cpu_usage'] = float(cpu_result['output'].strip().replace('%', ''))
            except:
                pass
        
        # Memory
        mem_result = self.execute_command("free -m | grep Mem | awk '{print $2, $3, $4}'")
        if mem_result['success']:
            try:
                parts = mem_result['output'].strip().split()
                info['memory'] = {
                    'total_mb': int(parts[0]),
                    'used_mb': int(parts[1]),
                    'free_mb': int(parts[2])
                }
            except:
                pass
        
        # Disk usage
        disk_result = self.execute_command("df -h / | tail -1 | awk '{print $2, $3, $4, $5}'")
        if disk_result['success']:
            try:
                parts = disk_result['output'].strip().split()
                info['disk'] = {
                    'total': parts[0],
                    'used': parts[1],
                    'free': parts[2],
                    'usage_percent': parts[3]
                }
            except:
                pass
        
        return info
    
    def set_volume(self, level: int) -> Dict[str, Any]:
        """Define volume do sistema (0-100)."""
        level = max(0, min(100, level))
        return self.execute_command(f'amixer set Master {level}%')
    
    def take_screenshot(self, path: str) -> Dict[str, Any]:
        """Tira screenshot usando gnome-screenshot ou scrot."""
        # Tentar gnome-screenshot primeiro
        result = self.execute_command(f'gnome-screenshot -f {path}')
        if not result['success']:
            # Tentar scrot
            result = self.execute_command(f'scrot {path}')
        return result


class AndroidController(SystemControllerBase):
    """Controlador para Android via ADB."""
    
    def __init__(self):
        super().__init__()
        self.adb_available = self._check_adb()
    
    def _check_adb(self) -> bool:
        """Verifica se ADB está disponível."""
        try:
            subprocess.run(['adb', 'version'], 
                         capture_output=True, timeout=5)
            return True
        except:
            logger.warning("ADB não disponível. Instale Android SDK Platform Tools.")
            return False
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Executa comando ADB."""
        if not self.adb_available:
            return {
                'success': False,
                'error': 'ADB não disponível'
            }
        
        try:
            result = subprocess.run(
                f'adb shell {command}',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Erro ao executar comando ADB: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_connected_devices(self) -> List[str]:
        """Lista dispositivos Android conectados."""
        try:
            result = subprocess.run(
                'adb devices',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')[1:]  # Skip header
                devices = [line.split()[0] for line in lines if line.strip() and 'device' in line]
                return devices
        except:
            pass
        return []
    
    def open_application(self, package_name: str) -> Dict[str, Any]:
        """Abre aplicativo no Android."""
        # Mapa de apps comuns
        apps_map = {
            'chrome': 'com.android.chrome',
            'youtube': 'com.google.android.youtube',
            'gmail': 'com.google.android.gm',
            'camera': 'com.android.camera2',
            'gallery': 'com.google.android.apps.photos',
            'settings': 'com.android.settings',
        }
        
        package = apps_map.get(package_name.lower(), package_name)
        return self.execute_command(f'monkey -p {package} 1')
    
    def get_system_info(self) -> Dict[str, Any]:
        """Informações do dispositivo Android."""
        info = {
            'system': 'Android',
            'devices': self.get_connected_devices()
        }
        
        if not info['devices']:
            info['status'] = 'No devices connected'
            return info
        
        # Informações do dispositivo
        model_result = self.execute_command('getprop ro.product.model')
        if model_result['success']:
            info['model'] = model_result['output'].strip()
        
        version_result = self.execute_command('getprop ro.build.version.release')
        if version_result['success']:
            info['android_version'] = version_result['output'].strip()
        
        battery_result = self.execute_command('dumpsys battery | grep level')
        if battery_result['success']:
            try:
                level = battery_result['output'].split(':')[1].strip()
                info['battery_level'] = f"{level}%"
            except:
                pass
        
        return info
    
    def send_text(self, text: str) -> Dict[str, Any]:
        """Envia texto para o dispositivo."""
        return self.execute_command(f'input text "{text}"')
    
    def take_screenshot(self, path: str) -> Dict[str, Any]:
        """Tira screenshot do Android."""
        device_path = '/sdcard/screenshot.png'
        result = self.execute_command(f'screencap -p {device_path}')
        
        if result['success']:
            # Transferir para PC
            try:
                subprocess.run(
                    f'adb pull {device_path} {path}',
                    shell=True,
                    timeout=30
                )
                return {'success': True, 'path': path}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return result


class UniversalSystemController:
    """
    Controlador universal que detecta o SO e usa o controlador apropriado.
    """
    
    def __init__(self):
        self.system = platform.system()
        
        if self.system == 'Windows':
            self.controller = WindowsController()
        elif self.system == 'Linux':
            self.controller = LinuxController()
        else:
            # macOS ou outros
            self.controller = LinuxController()  # Usar Linux como base
        
        # Android controller sempre disponível via ADB
        self.android_controller = AndroidController()
        
        logger.info(f" Universal System Controller inicializado para {self.system}")
    
    def execute_command(self, command: str, target: str = 'local') -> Dict[str, Any]:
        """
        Executa comando no sistema especificado.
        
        Args:
            command: Comando a executar
            target: 'local' ou 'android'
        """
        if target == 'android':
            return self.android_controller.execute_command(command)
        else:
            return self.controller.execute_command(command)
    
    def open_application(self, app_name: str, target: str = 'local') -> Dict[str, Any]:
        """Abre aplicativo."""
        if target == 'android':
            return self.android_controller.open_application(app_name)
        else:
            return self.controller.open_application(app_name)
    
    def get_system_info(self, target: str = 'local') -> Dict[str, Any]:
        """Retorna informações do sistema."""
        if target == 'android':
            return self.android_controller.get_system_info()
        else:
            return self.controller.get_system_info()
    
    def get_all_system_info(self) -> Dict[str, Any]:
        """Retorna informações de todos os sistemas disponíveis."""
        return {
            'local': self.controller.get_system_info(),
            'android': self.android_controller.get_system_info() if self.android_controller.adb_available else None
        }
    
    def get_running_processes(self, target: str = 'local') -> List[Dict[str, Any]]:
        """Lista processos em execução."""
        if target == 'local':
            return self.controller.get_running_processes()
        return []
    
    def kill_process(self, process_name: str, target: str = 'local') -> Dict[str, Any]:
        """Encerra processo."""
        if target == 'local':
            return self.controller.kill_process(process_name)
        return {'success': False, 'error': 'Not supported for this target'}
    
    def set_volume(self, level: int, target: str = 'local') -> Dict[str, Any]:
        """Define volume."""
        if target == 'local':
            return self.controller.set_volume(level)
        return {'success': False, 'error': 'Not supported for this target'}
    
    def take_screenshot(self, path: str, target: str = 'local') -> Dict[str, Any]:
        """Tira screenshot."""
        if target == 'android':
            return self.android_controller.take_screenshot(path)
        else:
            return self.controller.take_screenshot(path)
    
    def is_android_available(self) -> bool:
        """Verifica se controle Android está disponível."""
        return self.android_controller.adb_available and len(self.android_controller.get_connected_devices()) > 0


# Instância global
_system_controller = None


def get_system_controller() -> UniversalSystemController:
    """Retorna instância global do controlador de sistema."""
    global _system_controller
    if _system_controller is None:
        _system_controller = UniversalSystemController()
    return _system_controller
