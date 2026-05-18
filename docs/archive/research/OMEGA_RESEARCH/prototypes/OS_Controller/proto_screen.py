from datetime import datetime
from pathlib import Path

import pyautogui


def capture_all_screens():
    """Capture all connected screens and save the image next to this archived prototype."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot = pyautogui.screenshot()
        save_path = Path(__file__).resolve().parent / f"screenshot_{timestamp}.png"
        screenshot.save(save_path)
        return str(save_path)
    except Exception as e:
        print(f"Erro na captura de tela: {e}")
        return None


if __name__ == "__main__":
    path = capture_all_screens()
    if path:
        print(f"Tela capturada com sucesso: {path}")
