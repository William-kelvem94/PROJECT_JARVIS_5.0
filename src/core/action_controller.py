"""
Controlador de ações do sistema
Habilita interação com mouse e teclado via PyAutoGUI
"""

import pyautogui
import time
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Configurações de segurança do PyAutoGUI
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

class ActionController:
    """Classe para executar ações físicas no sistema"""

    def click_at(self, x: int, y: int, clicks: int = 1, button: str = 'left'):
        """Clica em uma coordenada específica"""
        try:
            logger.info(f"Clicando em ({x}, {y}) - {clicks}x {button}")
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            return True
        except Exception as e:
            logger.error(f"Erro ao clicar: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.1):
        """Digita um texto"""
        try:
            logger.info(f"Digitando texto: {text[:20]}...")
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Erro ao digitar: {e}")
            return False

    def press_key(self, key: str):
        """Pressiona uma tecla especial (ex: 'enter', 'esc')"""
        try:
            logger.info(f"Pressionando tecla: {key}")
            pyautogui.press(key)
            return True
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla: {e}")
            return False

    def hotkey(self, *args):
        """Executa combinação de teclas (ex: 'ctrl', 'c')"""
        try:
            logger.info(f"Executando hotkey: {args}")
            pyautogui.hotkey(*args)
            return True
        except Exception as e:
            logger.error(f"Erro ao executar hotkey: {e}")
            return False

    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move o mouse suavemente"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Erro ao mover mouse: {e}")
            return False

# Instância global
action_controller = ActionController()
