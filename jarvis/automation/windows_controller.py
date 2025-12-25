"""
Controlador Avançado do Windows
Controle total do sistema operacional Windows
"""

import os
import sys
import subprocess
import psutil
import winreg
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui
import win32process
import win32clipboard
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import time
from ..core.logger import default_logger


class WindowsController:
    """Controlador avançado do sistema Windows"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Verificar privilégios administrativos
        self.is_admin = self._check_admin_privileges()
        if not self.is_admin:
            self.logger.warning("Executando sem privilégios administrativos. Algumas funções podem estar limitadas.")
        
        # Mapeamento de aplicações comuns
        self.app_paths = {
            'chrome': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ],
            'firefox': [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
            ],
            'edge': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
            ],
            'notepad': [r'C:\Windows\System32\notepad.exe'],
            'calculator': [r'C:\Windows\System32\calc.exe'],
            'paint': [r'C:\Windows\System32\mspaint.exe'],
            'cmd': [r'C:\Windows\System32\cmd.exe'],
            'powershell': [r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'],
            'explorer': [r'C:\Windows\explorer.exe']
        }
        
        # Cache de processos
        self.process_cache = {}
        self.last_cache_update = 0
        
        self.logger.info("Windows Controller inicializado")
    
    def _check_admin_privileges(self) -> bool:
        """Verifica se está executando com privilégios administrativos"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def execute_application(self, app_name: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Executa uma aplicação
        
        Args:
            app_name: Nome da aplicação
            args: Argumentos opcionais
            
        Returns:
            Resultado da execução
        """
        try:
            app_name_lower = app_name.lower()
            
            # Procurar caminho da aplicação
            app_path = None
            
            if app_name_lower in self.app_paths:
                for path in self.app_paths[app_name_lower]:
                    if os.path.exists(path):
                        app_path = path
                        break
            else:
                # Tentar encontrar no PATH
                app_path = self._find_in_path(app_name)
            
            if not app_path:
                # Tentar busca no registro do Windows
                app_path = self._find_in_registry(app_name)
            
            if not app_path:
                return {
                    'success': False,
                    'error': f'Aplicação "{app_name}" não encontrada'
                }
            
            # Executar aplicação
            cmd = [app_path]
            if args:
                cmd.extend(args)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            self.logger.info(f"Aplicação executada: {app_name} (PID: {process.pid})")
            
            return {
                'success': True,
                'pid': process.pid,
                'path': app_path,
                'command': ' '.join(cmd)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar aplicação {app_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close_application(self, app_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Fecha uma aplicação
        
        Args:
            app_name: Nome da aplicação
            force: Forçar fechamento
            
        Returns:
            Resultado da operação
        """
        try:
            processes = self._find_processes_by_name(app_name)
            
            if not processes:
                return {
                    'success': False,
                    'error': f'Nenhum processo encontrado para "{app_name}"'
                }
            
            closed_processes = []
            
            for proc in processes:
                try:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    
                    # Aguardar fechamento
                    proc.wait(timeout=5)
                    closed_processes.append(proc.pid)
                    
                except psutil.TimeoutExpired:
                    if not force:
                        # Tentar forçar se não fechou normalmente
                        proc.kill()
                        closed_processes.append(proc.pid)
                
                except Exception as e:
                    self.logger.warning(f"Erro ao fechar processo {proc.pid}: {e}")
            
            self.logger.info(f"Processos fechados: {closed_processes}")
            
            return {
                'success': True,
                'closed_processes': closed_processes,
                'total_closed': len(closed_processes)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao fechar aplicação {app_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def system_shutdown(self, delay: int = 0, force: bool = False) -> Dict[str, Any]:
        """
        Desliga o sistema
        
        Args:
            delay: Atraso em segundos
            force: Forçar desligamento
            
        Returns:
            Resultado da operação
        """
        try:
            if not self.is_admin:
                return {
                    'success': False,
                    'error': 'Privilégios administrativos necessários para desligar o sistema'
                }
            
            cmd = ['shutdown', '/s']
            
            if delay > 0:
                cmd.extend(['/t', str(delay)])
            else:
                cmd.extend(['/t', '0'])
            
            if force:
                cmd.append('/f')
            
            subprocess.run(cmd, check=True)
            
            self.logger.info(f"Sistema será desligado em {delay} segundos")
            
            return {
                'success': True,
                'delay': delay,
                'forced': force
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao desligar sistema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def system_restart(self, delay: int = 0, force: bool = False) -> Dict[str, Any]:
        """
        Reinicia o sistema
        
        Args:
            delay: Atraso em segundos
            force: Forçar reinicialização
            
        Returns:
            Resultado da operação
        """
        try:
            if not self.is_admin:
                return {
                    'success': False,
                    'error': 'Privilégios administrativos necessários para reiniciar o sistema'
                }
            
            cmd = ['shutdown', '/r']
            
            if delay > 0:
                cmd.extend(['/t', str(delay)])
            else:
                cmd.extend(['/t', '0'])
            
            if force:
                cmd.append('/f')
            
            subprocess.run(cmd, check=True)
            
            self.logger.info(f"Sistema será reiniciado em {delay} segundos")
            
            return {
                'success': True,
                'delay': delay,
                'forced': force
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar sistema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def system_hibernate(self) -> Dict[str, Any]:
        """
        Hiberna o sistema
        
        Returns:
            Resultado da operação
        """
        try:
            subprocess.run(['shutdown', '/h'], check=True)
            
            self.logger.info("Sistema hibernando")
            
            return {
                'success': True,
                'action': 'hibernate'
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao hibernar sistema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def system_sleep(self) -> Dict[str, Any]:
        """
        Coloca o sistema em suspensão
        
        Returns:
            Resultado da operação
        """
        try:
            # Usar API do Windows para suspensão
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            
            self.logger.info("Sistema em suspensão")
            
            return {
                'success': True,
                'action': 'sleep'
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao suspender sistema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Obtém informações do sistema
        
        Returns:
            Informações detalhadas do sistema
        """
        try:
            # Informações básicas
            info = {
                'os': {
                    'name': os.name,
                    'platform': sys.platform,
                    'version': sys.version,
                    'machine': os.environ.get('PROCESSOR_ARCHITECTURE', 'unknown')
                },
                'cpu': {
                    'count': psutil.cpu_count(),
                    'usage': psutil.cpu_percent(interval=1),
                    'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'used': psutil.virtual_memory().used,
                    'percentage': psutil.virtual_memory().percent
                },
                'disk': [],
                'network': psutil.net_io_counters()._asdict(),
                'processes': len(psutil.pids()),
                'uptime': time.time() - psutil.boot_time()
            }
            
            # Informações de disco
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info['disk'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percentage': (usage.used / usage.total) * 100
                    })
                except:
                    continue
            
            return info
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações do sistema: {e}")
            return {
                'error': str(e)
            }
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """
        Obtém lista de processos em execução
        
        Returns:
            Lista de processos
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Erro ao obter processos: {e}")
            return []
    
    def set_volume(self, level: int) -> Dict[str, Any]:
        """
        Define o volume do sistema
        
        Args:
            level: Nível do volume (0-100)
            
        Returns:
            Resultado da operação
        """
        try:
            # Normalizar nível
            level = max(0, min(100, level))
            
            # Usar nircmd se disponível, senão usar PowerShell
            try:
                subprocess.run([
                    'powershell', '-Command',
                    f'(New-Object -comObject WScript.Shell).SendKeys([char]175)'
                ], check=True, capture_output=True)
                
                # Calcular quantas vezes pressionar
                current_vol = self._get_current_volume()
                steps = abs(level - current_vol) // 2
                
                key = '[char]175' if level > current_vol else '[char]174'  # Volume up/down
                
                for _ in range(steps):
                    subprocess.run([
                        'powershell', '-Command',
                        f'(New-Object -comObject WScript.Shell).SendKeys({key})'
                    ], check=True, capture_output=True)
                    time.sleep(0.1)
                
            except:
                # Fallback: usar API do Windows
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterScalarVolume(level / 100.0, None)
            
            self.logger.info(f"Volume definido para {level}%")
            
            return {
                'success': True,
                'level': level
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao definir volume: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_in_path(self, app_name: str) -> Optional[str]:
        """Procura aplicação no PATH do sistema"""
        try:
            result = subprocess.run(
                ['where', app_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')[0]
        except:
            return None
    
    def _find_in_registry(self, app_name: str) -> Optional[str]:
        """Procura aplicação no registro do Windows"""
        try:
            # Procurar em App Paths
            key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{app_name}.exe"
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    path = winreg.QueryValue(key, "")
                    if os.path.exists(path):
                        return path
            except:
                pass
            
            # Procurar em programas instalados
            uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        subkey_name = winreg.EnumKey(key, i)
                        try:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if app_name.lower() in display_name.lower():
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    # Procurar executável na pasta de instalação
                                    for file in Path(install_location).rglob("*.exe"):
                                        if app_name.lower() in file.name.lower():
                                            return str(file)
                        except:
                            continue
            except:
                pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Erro ao procurar no registro: {e}")
            return None
    
    def _find_processes_by_name(self, name: str) -> List[psutil.Process]:
        """Encontra processos pelo nome"""
        processes = []
        name_lower = name.lower()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name_lower in proc.info['name'].lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def _get_current_volume(self) -> int:
        """Obtém o volume atual do sistema"""
        try:
            # Tentar usar pycaw se disponível
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_volume = volume.GetMasterScalarVolume()
            return int(current_volume * 100)
            
        except:
            # Fallback: assumir volume médio
            return 50
