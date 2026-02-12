import os
import signal
import logging
import threading
from pynput import keyboard

logger = logging.getLogger(__name__)

class KillSwitch:
    """
    Monitor de Interrupção de Emergência (Kill Switch).
    Atalho: Ctrl + Shift + Space.
    Ação: Para imediatamente todas as threads de controle físico/automação.
    """
    def __init__(self):
        self.listener = None
        self.is_active = False

    def start(self):
        """Inicia o listener global de teclado"""
        try:
            self.listener = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+<space>': self._emergency_stop
            })
            self.listener.start()
            self.is_active = True
            logger.info("🛡️ Kill Switch Ativo: [Ctrl + Shift + Space] para emergência.")
        except Exception as e:
            logger.error(f"Não foi possível iniciar o Kill Switch: {e}")

    def _emergency_stop(self):
        """Para o sistema imediatamente"""
        logger.critical("🔥 INTERRUPÇÃO DE EMERGÊNCIA ATIVADA PELA TECLA DE ATALHO!")
        
        # 1. Parar PyAutoGUI
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            # Forçar erro movendo mouse para o canto (se possível)
            pyautogui.moveTo(0, 0)
        except: pass

        # 2. Notificar o usuário via logs/hud
        print("\n" + "!"*50)
        print("!!! EMERGÊNCIA: CONTROLE FÍSICO ENCERRADO !!!")
        print("!"*50 + "\n")

        # 3. Encerrar o processo se necessário ou apenas threads de ação
        # No Singularity, queremos manter a consciência (áudio) se possível,
        # mas aqui vamos forçar um sinal SIGINT para segurança total.
        os.kill(os.getpid(), signal.SIGINT)

# Instância global
kill_switch = KillSwitch()
