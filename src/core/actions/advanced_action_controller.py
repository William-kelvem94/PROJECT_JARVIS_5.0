"""
Advanced Action Controller - Controle Total do PC
Gerencia automaÃ§Ã£o de interface, controle de aplicaÃ§Ãµes e sistema de arquivos
"""

import os
import sys
import logging
import subprocess
import psutil
import pyautogui
import pygetwindow as gw
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

logger = logging.getLogger(__name__)

# Configurar PyAutoGUI para seguranÃ§a
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class AdvancedActionController:
    """Controlador avanÃ§ado de aÃ§Ãµes do sistema"""
    
    def __init__(self):
        self.known_apps = self._discover_applications()
        self.macros = {}
        
    def _discover_applications(self) -> Dict[str, str]:
        """Descobre aplicaÃ§Ãµes instaladas no sistema"""
        apps = {}
        
        if sys.platform == "win32":
            # Locais comuns de instalaÃ§Ã£o no Windows
            search_paths = [
                Path(os.environ.get("ProgramFiles", "C:/Program Files")),
                Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")),
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
            ]
            
            common_apps = {
                "chrome": ["Google/Chrome/Application/chrome.exe"],
                "firefox": ["Mozilla Firefox/firefox.exe"],
                "edge": ["Microsoft/Edge/Application/msedge.exe"],
                "vscode": ["Microsoft VS Code/Code.exe"],
                "notepad++": ["Notepad++/notepad++.exe"],
                "spotify": ["Spotify/Spotify.exe"],
                "discord": ["Discord/Discord.exe"],
            }
            
            for app_name, possible_paths in common_apps.items():
                for base_path in search_paths:
                    for rel_path in possible_paths:
                        full_path = base_path / rel_path
                        if full_path.exists():
                            apps[app_name] = str(full_path)
                            break
                    if app_name in apps:
                        break
        
        logger.info(f"Descobertas {len(apps)} aplicaÃ§Ãµes")
        return apps
    
    def open_application(self, app_name: str) -> bool:
        """Abre uma aplicaÃ§Ã£o pelo nome"""
        try:
            # Validação básica de segurança
            if not app_name or not app_name.strip():
                logger.error("❌ Nome da aplicação vazio")
                return False
            
            # Prevenir injeção de comandos - permitir apenas caracteres seguros
            import re
            if not re.match(r'^[a-zA-Z0-9._\-\s]+$', app_name):
                logger.error(f"❌ Nome da aplicação contém caracteres inválidos: {app_name}")
                return False
            
            app_name_lower = app_name.lower()
            
            # Verificar se está nos apps conhecidos
            if app_name_lower in self.known_apps:
                subprocess.Popen([self.known_apps[app_name_lower]], shell=False)
                logger.info(f"✅ Aplicação aberta: {app_name}")
                return True
            
            # Tentar abrir diretamente (pode estar no PATH)
            subprocess.Popen([app_name], shell=False)
            logger.info(f"âœ… AplicaÃ§Ã£o aberta: {app_name}")
            return True
            
        except Exception as e:
            logger.error(f"âŒ Erro ao abrir {app_name}: {e}")
            return False
    
    def close_application(self, app_name: str) -> bool:
        """Fecha uma aplicaÃ§Ã£o pelo nome"""
        try:
            target_name = app_name.lower()
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = (proc.info.get('name') or '').lower()
                    exe_path = proc.info.get('exe') or ''
                    exe_name = os.path.basename(exe_path).lower() if exe_path else ''

                    # Comparar exatamente com o nome do processo ou nome do executável
                    if (
                        target_name == proc_name
                        or target_name == exe_name
                        or (exe_name.endswith(".exe") and target_name == exe_name[:-4])
                    ):
                        proc.terminate()
                        logger.info(f"✅ Aplicação fechada: {app_name}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            logger.warning(f"âš ï¸ AplicaÃ§Ã£o nÃ£o encontrada: {app_name}")
            return False
            
        except Exception as e:
            logger.error(f"âŒ Erro ao fechar {app_name}: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05):
        """Digita texto na posiÃ§Ã£o atual do cursor"""
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"âœ… Texto digitado: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao digitar: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1):
        """Pressiona uma tecla"""
        try:
            pyautogui.press(key, presses=presses)
            logger.info(f"âœ… Tecla pressionada: {key}")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao pressionar tecla: {e}")
            return False
    
    def hotkey(self, *keys):
        """Executa combinaÃ§Ã£o de teclas"""
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"âœ… Atalho executado: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao executar atalho: {e}")
            return False
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1):
        """Clica em uma posiÃ§Ã£o ou na posiÃ§Ã£o atual"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button, clicks=clicks)
            else:
                pyautogui.click(button=button, clicks=clicks)
            logger.info(f"âœ… Clique executado: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao clicar: {e}")
            return False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move o mouse para uma posiÃ§Ã£o"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao mover mouse: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Retorna posiÃ§Ã£o atual do mouse"""
        return pyautogui.position()
    
    def screenshot_region(self, x: int, y: int, width: int, height: int, filename: Optional[str] = None):
        """Captura uma regiÃ£o especÃ­fica da tela"""
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            if filename:
                screenshot.save(filename)
            return screenshot
        except Exception as e:
            logger.error(f"âŒ Erro ao capturar regiÃ£o: {e}")
            return None
    
    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Encontra uma imagem na tela e retorna sua posiÃ§Ã£o"""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return (center.x, center.y)
            return None
        except Exception as e:
            logger.error(f"âŒ Erro ao localizar imagem: {e}")
            return None
    
    def record_macro(self, name: str, actions: List[Dict[str, Any]]):
        """Grava uma macro (sequÃªncia de aÃ§Ãµes)"""
        self.macros[name] = actions
        logger.info(f"âœ… Macro gravada: {name} ({len(actions)} aÃ§Ãµes)")
    
    def play_macro(self, name: str) -> bool:
        """Executa uma macro gravada"""
        if name not in self.macros:
            logger.error(f"âŒ Macro nÃ£o encontrada: {name}")
            return False
        
        try:
            for index, action in enumerate(self.macros[name]):
                # Validar estrutura básica da ação
                if not isinstance(action, dict):
                    logger.error(f"❌ Ação inválida na macro '{name}' no índice {index}: esperado dict, obtido {type(action).__name__}")
                    continue

                action_type = action.get('type')
                if not action_type:
                    logger.error(f"❌ Tipo de ação ausente na macro '{name}' no índice {index}")
                    continue
                
                if action_type == 'click':
                    if 'x' not in action or 'y' not in action or action['x'] is None or action['y'] is None:
                        logger.error(f"❌ Ação 'click' inválida na macro '{name}' no índice {index}: campos 'x' e 'y' são obrigatórios")
                        continue
                    self.click(action['x'], action['y'])
                elif action_type == 'type':
                    text = action.get('text')
                    if text is None:
                        logger.error(f"❌ Ação 'type' inválida na macro '{name}' no índice {index}: campo 'text' é obrigatório")
                        continue
                    self.type_text(text)
                elif action_type == 'key':
                    key = action.get('key')
                    if key is None:
                        logger.error(f"❌ Ação 'key' inválida na macro '{name}' no índice {index}: campo 'key' é obrigatório")
                        continue
                    self.press_key(key)
                elif action_type == 'hotkey':
                    keys = action.get('keys')
                    if not keys:
                        logger.error(f"❌ Ação 'hotkey' inválida na macro '{name}' no índice {index}: campo 'keys' é obrigatório")
                        continue
                    self.hotkey(*keys)
                elif action_type == 'wait':
                    duration = action.get('duration', 0.5)
                    time.sleep(duration)
                else:
                    logger.error(f"❌ Tipo de ação desconhecido '{action_type}' na macro '{name}' no índice {index}")
                    continue
                
            logger.info(f"âœ… Macro executada: {name}")
            return True
            
        except Exception as e:
            logger.error(f"âŒ Erro ao executar macro: {e}")
            return False
    
    def window_manage(self, window_title: Optional[str] = None, operation: str = "focus", **kwargs):
        """Gerencia janelas do sistema"""
        try:
            # Se título não fornecido, usar janela ativa
            if not window_title:
                window = gw.getActiveWindow()
            else:
                windows = gw.getWindowsWithTitle(window_title)
                if not windows:
                    logger.warning(f"⚠️ Janela não encontrada: {window_title}")
                    return False
                window = windows[0]

            if not window:
                return False

            if operation == "focus":
                window.activate()
            elif operation == "minimize":
                window.minimize()
            elif operation == "maximize":
                window.maximize()
            elif operation == "close":
                window.close()
            elif operation == "resize":
                width = kwargs.get('width', window.width)
                height = kwargs.get('height', window.height)
                window.resizeTo(width, height)
            elif operation == "move":
                x = kwargs.get('x', window.left)
                y = kwargs.get('y', window.top)
                window.moveTo(x, y)
            
            logger.info(f"âœ… OperaÃ§Ã£o '{operation}' na janela: {window.title}")
            return True
        except Exception as e:
            logger.error(f"âŒ Erro ao gerenciar janela: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informaÃ§Ãµes do sistema"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage(os.path.abspath(os.sep)).percent,
            "running_processes": len(psutil.pids()),
            "screen_size": pyautogui.size()
        }


# InstÃ¢ncia global
advanced_action_controller = AdvancedActionController()
