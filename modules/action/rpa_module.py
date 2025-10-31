"""
Módulo de Automação Desktop (RPA)
Permite controle e automação de aplicativos desktop
"""

import os
import platform
import subprocess
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from core.logger import logger

try:
    # Configurar DISPLAY se não estiver definido (para Docker)
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':99'
    
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except (ImportError, KeyError, Exception) as e:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None
    logger.warning(f"pyautogui não disponível: {e}. Funcionalidade RPA desabilitada.")

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except (ImportError, Exception) as e:
    PYGETWINDOW_AVAILABLE = False
    gw = None
    logger.warning(f"pygetwindow não disponível: {e}")

class RPAModule:
    """
    Módulo de Automação Desktop usando RPA.
    Permite controle de aplicativos, cliques, digitação, etc.
    """
    
    def __init__(self):
        self.system = platform.system()
        self.app_windows = {}  # Cache de janelas abertas
        
        if PYAUTOGUI_AVAILABLE and pyautogui:
            # Configurar segurança do pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            logger.info("PyAutoGUI configurado")
        
        logger.info(f"RPAModule inicializado para {self.system}")
    
    def open_application(self, app_name: str, app_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Abre um aplicativo.
        
        Args:
            app_name: Nome do aplicativo
            app_path: Caminho opcional para o executável
        
        Returns:
            Resultado da operação
        """
        try:
            if app_path and os.path.exists(app_path):
                subprocess.Popen(app_path)
                logger.info(f"Aplicativo aberto: {app_path}")
                return {
                    "success": True,
                    "action": f"Abrir {app_name}",
                    "result": f"Aplicativo '{app_name}' aberto com sucesso!"
                }
            
            # Tentar encontrar aplicativo por nome
            if self.system == "Windows":
                # Usar start para abrir no Windows
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.system == "Linux":
                subprocess.Popen(app_name, shell=True)
            elif self.system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            
            # Aguardar aplicativo abrir
            time.sleep(2)
            
            # Tentar encontrar janela
            window = self._find_window(app_name)
            if window:
                self.app_windows[app_name] = window
            
            return {
                "success": True,
                "action": f"Abrir {app_name}",
                "result": f"Aplicativo '{app_name}' aberto com sucesso!"
            }
        except Exception as e:
            logger.error(f"Erro ao abrir aplicativo: {e}")
            return {
                "success": False,
                "action": f"Abrir {app_name}",
                "result": f"Erro: {str(e)}"
            }
    
    def _find_window(self, app_name: str):
        """Encontra janela de um aplicativo."""
        if not PYGETWINDOW_AVAILABLE or not gw:
            return None
        
        try:
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                return windows[0]
            
            # Tentar busca parcial
            all_windows = gw.getAllWindows() if gw else []
            for window in all_windows:
                if app_name.lower() in window.title.lower():
                    return window
        except Exception as e:
            logger.debug(f"Erro ao encontrar janela: {e}")
        
        return None
    
    def click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """
        Clica em coordenadas específicas.
        
        Args:
            x: Coordenada X
            y: Coordenada Y
            button: "left", "right", ou "middle"
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            return {
                "success": False,
                "result": "PyAutoGUI não disponível"
            }
        
        try:
            pyautogui.click(x, y, button=button)
            return {
                "success": True,
                "action": f"Clicar em ({x}, {y})",
                "result": "Clique executado"
            }
        except Exception as e:
            logger.error(f"Erro ao clicar: {e}")
            return {
                "success": False,
                "result": str(e)
            }
    
    def type_text(self, text: str, interval: float = 0.1) -> Dict[str, Any]:
        """
        Digita texto.
        
        Args:
            text: Texto para digitar
            interval: Intervalo entre caracteres
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            return {
                "success": False,
                "result": "PyAutoGUI não disponível"
            }
        
        try:
            pyautogui.write(text, interval=interval)
            return {
                "success": True,
                "action": "Digitar texto",
                "result": f"Texto digitado: {text[:50]}..."
            }
        except Exception as e:
            logger.error(f"Erro ao digitar: {e}")
            return {
                "success": False,
                "result": str(e)
            }
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """
        Pressiona uma tecla.
        
        Args:
            key: Tecla a pressionar (ex: "enter", "ctrl", "alt")
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            return {
                "success": False,
                "result": "PyAutoGUI não disponível"
            }
        
        try:
            pyautogui.press(key)
            return {
                "success": True,
                "action": f"Pressionar tecla {key}",
                "result": "Tecla pressionada"
            }
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla: {e}")
            return {
                "success": False,
                "result": str(e)
            }
    
    def hotkey(self, *keys: str) -> Dict[str, Any]:
        """
        Pressiona combinação de teclas.
        
        Args:
            *keys: Teclas a pressionar simultaneamente
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            return {
                "success": False,
                "result": "PyAutoGUI não disponível"
            }
        
        try:
            pyautogui.hotkey(*keys)
            return {
                "success": True,
                "action": f"Atalho: {'+'.join(keys)}",
                "result": "Atalho executado"
            }
        except Exception as e:
            logger.error(f"Erro ao executar atalho: {e}")
            return {
                "success": False,
                "result": str(e)
            }
    
    def screenshot(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Tira screenshot da tela.
        
        Args:
            save_path: Caminho opcional para salvar
        
        Returns:
            Caminho da imagem salva
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            return {
                "success": False,
                "result": "PyAutoGUI não disponível"
            }
        
        try:
            if not save_path:
                save_path = f"screenshot_{int(time.time())}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            return {
                "success": True,
                "action": "Screenshot",
                "result": f"Screenshot salvo em: {save_path}",
                "path": save_path
            }
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {e}")
            return {
                "success": False,
                "result": str(e)
            }
    
    def find_image_on_screen(self, image_path: str, confidence: float = 0.8) -> Dict[str, Any]:
        """
        Encontra imagem na tela (template matching).
        
        Args:
            image_path: Caminho da imagem template
            confidence: Nível de confiança (0.0 a 1.0)
        
        Returns:
            Coordenadas se encontrado
        """
        if not PYAUTOGUI_AVAILABLE or not pyautogui:
            return {
                "success": False,
                "result": "PyAutoGUI não disponível"
            }
        
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return {
                    "success": True,
                    "found": True,
                    "x": center.x,
                    "y": center.y
                }
            return {
                "success": True,
                "found": False
            }
        except Exception as e:
            logger.debug(f"Imagem não encontrada: {e}")
            return {
                "success": True,
                "found": False
            }
    
    def is_available(self) -> bool:
        """Verifica se o módulo RPA está disponível."""
        return PYAUTOGUI_AVAILABLE and pyautogui is not None

