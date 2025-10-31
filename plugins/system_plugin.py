# Plugin de Sistema Operacional - Controle do PC

import os
import platform
import subprocess
import psutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.logger import logger

class SystemPlugin:
    """
    Plugin para controle do sistema operacional:
    - Abrir aplicativos
    - Gerenciar processos
    - Informações do sistema
    - Executar comandos
    """
    
    def __init__(self):
        self.system = platform.system()
        self.apps_paths = self._load_apps_paths()
        logger.info(f"SystemPlugin inicializado para {self.system}")
    
    def _load_apps_paths(self) -> Dict[str, str]:
        """Carrega caminhos comuns de aplicativos."""
        if self.system == "Windows":
            return {
                "calculadora": "calc.exe",
                "bloco de notas": "notepad.exe",
                "paint": "mspaint.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            }
        elif self.system == "Linux":
            return {
                "calculator": "gnome-calculator",
                "text editor": "gedit",
                "browser": "firefox",
            }
        else:
            return {}
    
    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Abre um aplicativo pelo nome."""
        try:
            app_name_lower = app_name.lower()
            
            # Procurar no dicionário de apps
            if app_name_lower in self.apps_paths:
                app_path = os.path.expandvars(self.apps_paths[app_name_lower])
                subprocess.Popen(app_path, shell=True)
                return {
                    "success": True,
                    "action": f"Abrir {app_name}",
                    "result": f"Aplicativo '{app_name}' aberto com sucesso!"
                }
            
            # Tentar abrir diretamente
            try:
                subprocess.Popen(app_name, shell=True)
                return {
                    "success": True,
                    "action": f"Abrir {app_name}",
                    "result": f"Tentativa de abrir '{app_name}' realizada."
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": f"Abrir {app_name}",
                    "result": f"Erro ao abrir: {str(e)}"
                }
        except Exception as e:
            logger.error(f"Erro ao abrir app: {e}")
            return {
                "success": False,
                "action": f"Abrir {app_name}",
                "result": f"Erro: {str(e)}"
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = {
                "system": platform.system(),
                "version": platform.version(),
                "processor": platform.processor(),
                "cpu_usage": f"{cpu_percent}%",
                "memory_total": f"{memory.total / (1024**3):.2f} GB",
                "memory_used": f"{memory.used / (1024**3):.2f} GB",
                "memory_percent": f"{memory.percent}%",
                "disk_total": f"{disk.total / (1024**3):.2f} GB",
                "disk_used": f"{disk.used / (1024**3):.2f} GB",
                "disk_free": f"{disk.free / (1024**3):.2f} GB"
            }
            
            return {
                "success": True,
                "action": "Informações do Sistema",
                "result": json.dumps(info, indent=2)
            }
        except Exception as e:
            logger.error(f"Erro ao obter info do sistema: {e}")
            return {
                "success": False,
                "action": "Informações do Sistema",
                "result": f"Erro: {str(e)}"
            }
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Executa um comando do sistema."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout if result.stdout else result.stderr
            
            return {
                "success": result.returncode == 0,
                "action": f"Executar: {command}",
                "result": output[:500]  # Limitar tamanho
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "action": f"Executar: {command}",
                "result": "Comando excedeu o tempo limite"
            }
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return {
                "success": False,
                "action": f"Executar: {command}",
                "result": f"Erro: {str(e)}"
            }
    
    def list_running_processes(self, limit: int = 10) -> Dict[str, Any]:
        """Lista processos em execução."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Ordenar por uso de CPU
            processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:limit]
            
            result = "\n".join([
                f"{p['name']}: CPU {p['cpu_percent']:.1f}%, RAM {p['memory_percent']:.1f}%"
                for p in processes
            ])
            
            return {
                "success": True,
                "action": "Processos em Execução",
                "result": result
            }
        except Exception as e:
            logger.error(f"Erro ao listar processos: {e}")
            return {
                "success": False,
                "action": "Processos em Execução",
                "result": f"Erro: {str(e)}"
            }

