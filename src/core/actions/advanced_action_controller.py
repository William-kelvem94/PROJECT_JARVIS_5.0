"""
Advanced Action Controller - Controle Total do PC
Gerencia automação de interface, controle de aplicações e sistema de arquivos
"""

import os
import sys
import logging
import subprocess
import psutil
import pyautogui
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

logger = logging.getLogger(__name__)

# Configurar PyAutoGUI para segurança
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class AdvancedActionController:
    """Controlador avançado de ações do sistema"""
    
    def __init__(self):
        self.known_apps = self._discover_applications()
        self.macros = {}
        
    def _discover_applications(self) -> Dict[str, str]:
        """Descobre aplicações instaladas no sistema"""
        apps = {}
        
        if sys.platform == "win32":
            # Locais comuns de instalação no Windows
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
        
        logger.info(f"Descobertas {len(apps)} aplicações")
        return apps
    
    def open_application(self, app_name: str) -> bool:
        """Abre uma aplicação pelo nome"""
        try:
            app_name_lower = app_name.lower()
            
            # Verificar se está nos apps conhecidos
            if app_name_lower in self.known_apps:
                subprocess.Popen([self.known_apps[app_name_lower]])
                logger.info(f"✅ Aplicação aberta: {app_name}")
                return True
            
            # Tentar abrir diretamente (pode estar no PATH)
            subprocess.Popen([app_name])
            logger.info(f"✅ Aplicação aberta: {app_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao abrir {app_name}: {e}")
            return False
    
    def close_application(self, app_name: str) -> bool:
        """Fecha uma aplicação pelo nome"""
        try:
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    logger.info(f"✅ Aplicação fechada: {app_name}")
                    return True
            
            logger.warning(f"⚠️ Aplicação não encontrada: {app_name}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao fechar {app_name}: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05):
        """Digita texto na posição atual do cursor"""
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"✅ Texto digitado: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao digitar: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1):
        """Pressiona uma tecla"""
        try:
            pyautogui.press(key, presses=presses)
            logger.info(f"✅ Tecla pressionada: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao pressionar tecla: {e}")
            return False
    
    def hotkey(self, *keys):
        """Executa combinação de teclas"""
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"✅ Atalho executado: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao executar atalho: {e}")
            return False
    
    def click(self, x: int = None, y: int = None, button: str = 'left', clicks: int = 1):
        """Clica em uma posição ou na posição atual"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button, clicks=clicks)
            else:
                pyautogui.click(button=button, clicks=clicks)
            logger.info(f"✅ Clique executado: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao clicar: {e}")
            return False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move o mouse para uma posição"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao mover mouse: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Retorna posição atual do mouse"""
        return pyautogui.position()
    
    def screenshot_region(self, x: int, y: int, width: int, height: int, filename: str = None):
        """Captura uma região específica da tela"""
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            if filename:
                screenshot.save(filename)
            return screenshot
        except Exception as e:
            logger.error(f"❌ Erro ao capturar região: {e}")
            return None
    
    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Encontra uma imagem na tela e retorna sua posição"""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return (center.x, center.y)
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao localizar imagem: {e}")
            return None
    
    def record_macro(self, name: str, actions: List[Dict[str, Any]]):
        """Grava uma macro (sequência de ações)"""
        self.macros[name] = actions
        logger.info(f"✅ Macro gravada: {name} ({len(actions)} ações)")
    
    def play_macro(self, name: str) -> bool:
        """Executa uma macro gravada"""
        if name not in self.macros:
            logger.error(f"❌ Macro não encontrada: {name}")
            return False
        
        try:
            for action in self.macros[name]:
                action_type = action.get('type')
                
                if action_type == 'click':
                    self.click(action.get('x'), action.get('y'))
                elif action_type == 'type':
                    self.type_text(action.get('text'))
                elif action_type == 'key':
                    self.press_key(action.get('key'))
                elif action_type == 'hotkey':
                    self.hotkey(*action.get('keys'))
                elif action_type == 'wait':
                    time.sleep(action.get('duration', 0.5))
                
            logger.info(f"✅ Macro executada: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar macro: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "running_processes": len(psutil.pids()),
            "screen_size": pyautogui.size()
        }


# Instância global
advanced_action_controller = AdvancedActionController()
