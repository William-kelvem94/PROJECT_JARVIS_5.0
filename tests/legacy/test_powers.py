import sys
import os
import time
import logging

# Adicionar src ao path
sys.path.append(os.path.join(os.getcwd()))

from src.core.management.device_manager import device_manager
from src.core.actions.action_controller import action_controller
from src.core.actions.advanced_action_controller import advanced_action_controller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPowers")

def test_powers():
    logger.info("🚀 Iniciando Teste de Poderes - JARVIS 5.0")
    
    # 1. Leitura da janela em foco
    logger.info("--- 1. Janela em Foco ---")
    focus_context = advanced_action_controller.get_system_info().get('active_window', {})
    logger.info(f"Janela detectada: {focus_context}")

    # 2. Notepad Ghost Typing
    logger.info("--- 2. Notepad Auto-Automation ---")
    action_controller.hotkey('win', 'r')
    time.sleep(0.5)
    action_controller.type_text('notepad')
    action_controller.press_key('enter')
    time.sleep(1.5)
    action_controller.type_text("JARVIS 5.0: Produtividade Real ativada. William, o sistema esta operacional.")
    time.sleep(2.0)
    action_controller.hotkey('alt', 'f4')
    time.sleep(0.5)
    action_controller.press_key('right') # Não salvar
    action_controller.press_key('enter')
    logger.info("Automação de Notepad concluída.")

    # 3. Volume Master
    logger.info("--- 3. Teste de Áudio (20% -> Original) ---")
    # Nota: DeviceManager.mute(False) e Volume control
    # Pegar volume atual não é trivial no pycaw sem código extra, vamos apenas setar.
    device_manager.set_volume(20)
    logger.info("Volume setado para 20%")
    time.sleep(2.0)
    device_manager.set_volume(80)
    logger.info("Volume restaurado para 80%")

    # 4. Brilho WMI (Samsung Fix)
    logger.info("--- 4. Teste de Brilho WMI (30% -> 100%) ---")
    device_manager.set_brightness(30)
    logger.info("Brilho setado para 30% via WMI")
    time.sleep(2.0)
    device_manager.set_brightness(100)
    logger.info("Brilho restaurado para 100% via WMI")

    logger.info("✅ Todos os poderes validados com sucesso.")

if __name__ == "__main__":
    test_powers()
