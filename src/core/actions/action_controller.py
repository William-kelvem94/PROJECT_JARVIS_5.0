"""
Controlador de aÃ§Ãµes do sistema
Habilita interaÃ§Ã£o com mouse e teclado via PyAutoGUI
"""

import pyautogui
import time
import logging
from typing import Tuple, Optional, List, Dict, Any
from src.core.security.security_manager import SecurityManager

logger = logging.getLogger(__name__)

# ConfiguraÃ§Ãµes de seguranÃ§a do PyAutoGUI
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

class ActionController:
    """Classe para executar aÃ§Ãµes fÃ­sicas no sistema"""

    def click_at(self, x: int, y: int, clicks: int = 1, button: str = 'left'):
        """Clica em uma coordenada especÃ­fica"""
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
        """Executa combinaÃ§Ã£o de teclas (ex: 'ctrl', 'c')"""
        try:
            logger.info(f"Executando hotkey: {args}")
            pyautogui.hotkey(*args)
            return True
        except Exception as e:
            logger.error(f"Erro ao executar hotkey: {e}")
            return False

    def drag_and_drop(self, x_start: int, y_start: int, x_end: int, y_end: int, duration: float = 1.0):
        """Arrasta de um ponto a outro"""
        try:
            logger.info(f"Arrastando de ({x_start}, {y_start}) para ({x_end}, {y_end})")
            pyautogui.moveTo(x_start, y_start)
            pyautogui.dragTo(x_end, y_end, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Erro no drag and drop: {e}")
            return False

    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move o cursor para uma posiÃ§Ã£o especÃ­fica"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Erro ao mover cursor: {e}")
            return False

    def click_text(self, target_text: str, ocr_regions: List[Dict[str, Any]]) -> bool:
        """
        Encontra um texto nas regiÃµes OCR e clica no centro dele.
        Suporta busca parcial (case-insensitive).
        """
        try:
            target_lower = target_text.lower()
            for region in ocr_regions:
                text = region.get('text', '').lower()
                if target_lower in text:
                    # Calcular centro da regiÃ£o
                    x = region['x'] + (region['width'] // 2)
                    y = region['y'] + (region['height'] // 2)
                    
                    logger.info(f"Texto '{target_text}' encontrado em ({x}, {y}). Clicando...")
                    self.click_at(x, y)
                    return True
            
            logger.warning(f"Texto '{target_text}' nÃ£o encontrado nas regiÃµes OCR.")
            return False
        except Exception as e:
            logger.error(f"Erro ao clicar no texto: {e}")
            return False

    def read_clipboard(self) -> str:
        """LÃª o conteÃºdo atual da Ã¡rea de transferÃªncia com retry"""
        for _ in range(3):
            try:
                import pyperclip
                return pyperclip.paste()
            except ImportError:
                # Fallback
                break
            except Exception:
                time.sleep(0.1)
        
        # Fallback se pyperclip falhar ou nÃ£o existir
        try:
             import tkinter as tk
             root = tk.Tk()
             root.withdraw()
             return root.clipboard_get()
        except Exception as e:
             logger.error(f"Erro ao ler clipboard (Final): {e}")
             return ""

    def analyze_and_organize(self, target_path: str, mapping: Dict[str, str]) -> bool:
        """
        Organiza arquivos com base em um mapeamento fornecido pela IA.
        mapping: { 'nome_arquivo.ext': 'Pasta Destino' }
        """
        import shutil
        from pathlib import Path

        try:
            logger.info(f"ðŸ§  Organizando via IA em: {target_path}")
            if not SecurityManager.validate_path_access(target_path):
                logger.error(f"ðŸ›¡ï¸ Bloqueio Anti-Genesis: Caminho proibido {target_path}")
                return False

            target = Path(target_path)
            if not target.exists() or not target.is_dir():
                return False

            count = 0
            for filename, category in mapping.items():
                file_path = target / filename
                if file_path.exists() and file_path.is_file():
                    dest_dir = target / category
                    dest_dir.mkdir(exist_ok=True)
                    shutil.move(str(file_path), str(dest_dir / filename))
                    count += 1
            
            logger.info(f"âœ… {count} arquivos movidos com lÃ³gica soberana.")
            return True
        except Exception as e:
            logger.error(f"Erro na organizaÃ§Ã£o soberana: {e}")
            return False

    def get_active_window(self) -> str:
        """Retorna o título da janela ativa no momento"""
        try:
            active = pyautogui.getActiveWindowTitle()
            return active if active else "Desktop"
        except:
            return "Unknown"

    def manage_window(self, title: str, action: str = 'focus'):
        """Gerencia janelas por título (focus, minimize, maximize, close)"""
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle(title)
            if not wins: return False
            win = wins[0]
            if action == 'focus': win.activate()
            elif action == 'minimize': win.minimize()
            elif action == 'maximize': win.maximize()
            elif action == 'close': win.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao gerenciar janela '{title}': {e}")
            return False

    def system_power(self, action: str):
        """Controle de energia (lock, logoff, restart, shutdown)"""
        import os
        try:
            if action == 'lock':
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            elif action == 'restart':
                os.system("shutdown /r /t 1")
            elif action == 'shutdown':
                os.system("shutdown /s /t 1")
            return True
        except Exception as e:
            logger.error(f"Erro no comando de energia '{action}': {e}")
            return False

    def execute_power_shell(self, script: str) -> str:
        """Executa comando PowerShell avançado com captura de output"""
        import subprocess
        try:
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, timeout=30)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return str(e)

    def fill_field(self, field_label: str, value: str, ocr_regions: List[Dict[str, Any]]) -> bool:
        """
        Tenta encontrar um rÃ³tulo (ex: 'Email') e clica no campo Ã  direita ou abaixo para preencher.
        """
        try:
            target_lower = field_label.lower()
            label_region = None
            
            for region in ocr_regions:
                if target_lower in region.get('text', '').lower():
                    label_region = region
                    break
            
            if label_region:
                # EstratÃ©gia: Clicar 100 pixels Ã  direita do centro do label (comum para inputs)
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

# InstÃ¢ncia global
action_controller = ActionController()
