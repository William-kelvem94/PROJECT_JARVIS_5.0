"""
Controlador de ações do sistema
Habilita interação com mouse e teclado via PyAutoGUI
"""

import pyautogui
import time
import logging
from typing import Tuple, Optional, List, Dict, Any

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

    def click_text(self, target_text: str, ocr_regions: List[Dict[str, Any]]) -> bool:
        """
        Encontra um texto nas regiões OCR e clica no centro dele.
        Suporta busca parcial (case-insensitive).
        """
        try:
            target_lower = target_text.lower()
            for region in ocr_regions:
                text = region.get('text', '').lower()
                if target_lower in text:
                    # Calcular centro da região
                    x = region['x'] + (region['width'] // 2)
                    y = region['y'] + (region['height'] // 2)
                    
                    logger.info(f"Texto '{target_text}' encontrado em ({x}, {y}). Clicando...")
                    self.click_at(x, y)
                    return True
            
            logger.warning(f"Texto '{target_text}' não encontrado nas regiões OCR.")
            return False
        except Exception as e:
            logger.error(f"Erro ao clicar no texto: {e}")
            return False

    def fill_field(self, field_label: str, value: str, ocr_regions: List[Dict[str, Any]]) -> bool:
        """
        Tenta encontrar um rótulo (ex: 'Email') e clica no campo à direita ou abaixo para preencher.
        """
        try:
            target_lower = field_label.lower()
            label_region = None
            
            for region in ocr_regions:
                if target_lower in region.get('text', '').lower():
                    label_region = region
                    break
            
            if label_region:
                # Estratégia: Clicar 100 pixels à direita do centro do label (comum para inputs)
                x = label_region['x'] + label_region['width'] + 50
                y = label_region['y'] + (label_region['height'] // 2)
                
                logger.info(f"Campo para '{field_label}' estimado em ({x}, {y}). Preenchendo...")
                self.click_at(x, y)
                time.sleep(0.2)
                self.type_text(value)
                return True
                
            return False
        except Exception as e:
            logger.error(f"Erro ao preencher campo: {e}")
            return False

# Instância global
action_controller = ActionController()
