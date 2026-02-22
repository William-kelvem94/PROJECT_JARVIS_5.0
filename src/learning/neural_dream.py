"""
O Gatilho do Sonho (DreamOrchestrator)
Monitora ociosisade do sistema para iniciar ciclos de aprendizado autÃ´nomo (Neural Dream).
"""

import threading
import time
import psutil
import logging
import datetime

# Logger setup
logger = logging.getLogger(__name__)


class DreamOrchestrator:
    def __init__(self, curiosity_engine=None):
        self.curiosity_engine = curiosity_engine
        self.is_dreaming = False
        self.stop_event = threading.Event()
        self.dream_thread = None
        self.monitor_thread = None

        # ConfiguraÃ§Ãµes de Gatilho
        self.IDLE_CPU_THRESHOLD = 15.0  # %
        self.IDLE_TIME_REQUIRED = (
            # segundos (10 min) - DEBUG: Usar 60s para teste rÃ¡pido se
            # necessÃ¡rio
            600
        )
        self.CHECK_INTERVAL = 60  # segundos

        self.idle_start_time = None

    def start_monitoring(self):
        """Inicia a thread de monitoramento em background"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return

        logger.info(
            "ðŸ’¤ DreamMonitor iniciado. Aguardando momento perfeito para sonhar..."
        )
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.stop_event.set()
        if self.is_dreaming:
            self.wake_up()

    def _monitor_loop(self):
        """Loop principal de verificaÃ§Ã£o de estado"""
        while not self.stop_event.is_set():
            try:
                if self._check_conditions():
                    if not self.is_dreaming:
                        self.start_dream_sequence()
                else:
                    if self.is_dreaming:
                        self.wake_up()

                time.sleep(self.CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Erro no DreamMonitor: {e}")
                time.sleep(60)

    def _check_conditions(self) -> bool:
        """Verifica CPU < 15% e Tomada Ligada"""
        try:
            # 1. Verificar Energia (ObrigatÃ³rio estar na tomada)
            battery = psutil.sensors_battery()
            # Se battery for None, Ã© um Desktop (sempre na tomada) -> True
            # Se battery existe, checar power_plugged
            plugged = battery.power_plugged if battery else True

            if not plugged:
                self.idle_start_time = None
                return False

            # 2. Verificar CPU (MÃ©dia de 5s para evitar picos falsos)
            cpu_usage = psutil.cpu_percent(interval=5)

            if cpu_usage < self.IDLE_CPU_THRESHOLD:
                if self.idle_start_time is None:
                    self.idle_start_time = datetime.datetime.now()
                    logger.debug("â³ InÃ­cio de contagem de ociosidade...")

                # Calcular tempo ocioso
                elapsed = (
                    datetime.datetime.now() - self.idle_start_time
                ).total_seconds()
                if elapsed >= self.IDLE_TIME_REQUIRED:
                    return True
            else:
                if self.idle_start_time:
                    logger.debug(
                        f"ðŸƒ Atividade detectada (CPU {cpu_usage}%). Resetando timer idle."
                    )
                self.idle_start_time = None

            return False

        except Exception as e:
            logger.warning(f"Erro ao verificar condiÃ§Ãµes de sonho: {e}")
            return False

    def start_dream_sequence(self):
        """Inicia o ciclo de sonho"""
        logger.info("ðŸŒŒ Entrando no Sonho Neural (Modo de Aprendizado AutÃ´nomo)...")
        self.is_dreaming = True

        # Iniciar thread de estudo
        if self.curiosity_engine:
            self.dream_thread = threading.Thread(
                target=self.curiosity_engine.run_study_cycle, daemon=True
            )
            self.dream_thread.start()
        else:
            logger.warning("CuriosityEngine nÃ£o conectado. Apenas sonhando acordado.")

    def wake_up(self):
        """Acorda o sistema imediatamente"""
        logger.info("â˜€ï¸ Acordando! InterrupÃ§Ã£o do usuÃ¡rio detectada.")
        self.is_dreaming = False
        self.idle_start_time = None

        if self.curiosity_engine:
            self.curiosity_engine.stop_study()

        if self.dream_thread and self.dream_thread.is_alive():
            # NÃ£o podemos matar threads em Python facilmente, mas o engine
            # deve checar flag is_dreaming
            pass


# InstÃ¢ncia Global (SerÃ¡ inicializada no main.py)
dream_orchestrator = DreamOrchestrator()
