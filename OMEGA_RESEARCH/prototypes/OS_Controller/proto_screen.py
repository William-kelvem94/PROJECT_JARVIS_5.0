import pyautogui
import os
from datetime import datetime

def capture_all_screens():
    """
    Captura todas as telas conectadas e salva como imagem.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot = pyautogui.screenshot()
        filename = f"screenshot_{timestamp}.png"
        # Salvando na pasta de protótipos
        save_path = os.path.join("D:\\DOCUMENTOS\\GitHub\\PROJECT_JARVIS_5.0\\OMEGA_RESEARCH\\prototypes\\OS_Controller", filename)
        screenshot.save(save_path)
        return save_path
    except Exception as e:
        print(f"Erro na captura de tela: {e}")
        return None

if __name__ == "__main__":
    path = capture_all_screens()
    if path:
        print(f"Tela capturada com sucesso: {path}")
