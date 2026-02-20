import os
import signal
import logging
from pynput import keyboard

logger = logging.getLogger(__name__)


class KillSwitch:
    """
    Monitor de InterrupÃ§Ã£o de EmergÃªncia (Kill Switch).
    Atalho: Ctrl + Shift + Space.
    AÃ§Ã£o: Para imediatamente todas as threads de controle fÃ­sico/automaÃ§Ã£o.
    """

    def __init__(self):
        self.listener = None
        self.is_active = False

    def start(self):
        """Inicia o listener global de teclado"""
        try:
            self.listener = keyboard.GlobalHotKeys(
                {"<ctrl>+<shift>+<space>": self._emergency_stop}
            )
            self.listener.start()
            self.is_active = True
            logger.info(
                "ðŸ›¡ï¸ Kill Switch Ativo: [Ctrl + Shift + Space] para emergÃªncia."
            )
        except Exception as e:
            logger.error(f"NÃ£o foi possÃ­vel iniciar o Kill Switch: {e}")

    def _emergency_stop(self):
        """Para o sistema imediatamente"""
        logger.critical(
            "ðŸ”¥ INTERRUPÃ‡ÃƒO DE EMERGÃŠNCIA ATIVADA PELA TECLA DE ATALHO!"
        )

        # 1. Parar PyAutoGUI
        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            # ForÃ§ar erro movendo mouse para o canto (se possÃ­vel)
            pyautogui.moveTo(0, 0)
        except BaseException:
            pass

        # 2. Notificar o usuÃ¡rio via logs/hud
        print("\n" + "!" * 50)
        print("!!! EMERGÃŠNCIA: CONTROLE FÃSICO ENCERRADO !!!")
        print("!" * 50 + "\n")

        # 3. Encerrar o processo se necessÃ¡rio ou apenas threads de aÃ§Ã£o
        # No Singularity, queremos manter a consciÃªncia (Ã¡udio) se possÃ­vel,
        # mas aqui vamos forÃ§ar um sinal SIGINT para seguranÃ§a total.
        os.kill(os.getpid(), signal.SIGINT)


# InstÃ¢ncia global
kill_switch = KillSwitch()
