"""
Monitor Proativo do Jarvis (Proactive Monitor)
Detecta mudanÃ§as significativas na tela em tempo real e aciona o Agente de IA proativamente.
"""

import cv2
import numpy as np
import time
import threading
import logging
from src.core.vision.screen_capture import screen_capture
from src.core.intelligence.ai_agent import ai_agent
from src.core.infrastructure.async_event_bus import EventType

logger = logging.getLogger(__name__)


class ProactiveMonitor:
    """Daemon que observa a tela em busca de mudanÃ§as (Deltas) e toma iniciativa"""

    def __init__(self, check_interval: float = 300.0, sensitivity: float = 0.15):
        # ðŸ†• Carregar do ai_config se disponÃ­vel
        try:
            from src.utils.config import config

            self.check_interval = config.get_ai_config(
                "vision.proactive_monitor.check_interval", check_interval
            )
            # Aumentar threshold ( threshold maior = menos triggers falsos)
            self.sensitivity = 0.25  # PadrÃ£o mais conservador para evitar sobrecarga
            self.cooldown = config.get_ai_config(
                "vision.proactive_monitor.cooldown", 900.0
            )
            logger.info(
                f"âš™ï¸ Monitor Proativo Otimizado: Intervalo={self.check_interval}s, Threshold={self.sensitivity}, Cooldown={self.cooldown}s"
            )
        except Exception as e:
            logger.warning(
                f"âš ï¸ Erro ao carregar config para ProactiveMonitor, usando defaults: {e}"
            )
            self.check_interval = check_interval
            self.sensitivity = sensitivity
            self.cooldown = 600.0

        self.running = False
        self.thread = None
        self.last_frame = None

        # Cooldown para nÃ£o ser irritante (segundos)
        self.last_trigger_time = 0

        # [EVENT BUS]
        self.event_bus = None

    def connect_event_bus(self, event_bus):
        """Connects Proactive Monitor to AsyncEventBus."""
        self.event_bus = event_bus
        logger.info("✅ Proactive Monitor connected to Event Bus.")

    def start(self):
        """Inicia o monitoramento em background"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"Monitor Proativo iniciado (Intervalo: {self.check_interval}s)")

    def stop(self):
        """Para o monitoramento"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _monitor_loop(self):
        """Loop principal de observaÃ§Ã£o"""
<<<<<<< Updated upstream
        consecutive_high_load = 0
<<<<<<< HEAD
        
=======
        consecutive_high_load = 0  # noqa: F841

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version
        while self.running:
            try:
                # ðŸ›¡ï¸ SAFETY CHECK: System Resource Monitor
                import psutil

                cpu_load = psutil.cpu_percent(interval=None)  # Non-blocking

                # Se CPU > 80%, reduz frequÃªncia mas MANTÃ‰M ATIVO
                if cpu_load > 85:
                    logger.debug(
                        f"CPU Alta ({cpu_load}%) - VisÃ£o em modo LOW FREQUENCY (10s)."
                    )
                    time.sleep(10)  # Modo econÃ´mico
                    continue
                elif cpu_load > 60:
                    time.sleep(5)  # Modo normal
                # Se livre, continua a cada self.check_interval (padrÃ£o 2s ou config)

                # Capturar frame atual (em baixa resoluÃ§Ã£o para performance)
                screenshot = screen_capture.capture_fullscreen(capture_type="monitor")
                if not screenshot:
                    time.sleep(self.check_interval)
                    continue

                frame = cv2.imread(screenshot)
                if frame is None:
                    time.sleep(self.check_interval)
                    continue

                # Converter para escala de cinza e aplicar blur para ignorar ruÃ­do pequeno
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if self.last_frame is None:
                    self.last_frame = gray
                    time.sleep(self.check_interval)
                    continue

                # Calcular diferenÃ§a absoluta entre o frame atual e o anterior
                if self.last_frame.shape != gray.shape:
                    logger.warning(
                        "DimensÃµes da tela mudaram. Reiniciando referÃªncia."
                    )
                    self.last_frame = gray
                    continue

                frame_delta = cv2.absdiff(self.last_frame, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

                # Dilatar para agrupar mudanÃ§as prÃ³ximas
                thresh = cv2.dilate(thresh, None, iterations=2)

                # Calcular porcentagem de mudanÃ§a
                change_percent = np.count_nonzero(thresh) / thresh.size

                if change_percent > self.sensitivity:
                    logger.info(
                        f"MudanÃ§a significativa detectada: {change_percent:.2%}"
                    )
                    self._handle_change(screenshot, change_percent * 100)

                self.last_frame = gray

            except Exception as e:
                logger.error(f"Erro no loop do Monitor Proativo: {e}")

            time.sleep(self.check_interval)

    def _handle_change(self, screenshot_path: str, diff_percent: float):
        """Decide se deve ou nÃ£o acionar a IA baseada no cooldown e estado"""
        current_time = time.time()

        if (current_time - self.last_trigger_time) < self.cooldown:
            logger.debug("MudanÃ§a ignorada devido ao cooldown.")
            return

        # Acionar o Agente de IA para anÃ¡lise proativa
        self.last_trigger_time = current_time

        # [PHASE 2.3] Event-Driven Trigger
        if self.event_bus:
            try:
                import asyncio

                # Use loop do bus ou pega o loop corrente (que deve estar rodando na main thread)
                # Como estamos em thread, precisamos de threadsafe calls
                loop = self.event_bus.loop if hasattr(self.event_bus, "loop") else None
                if loop and loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.event_bus.publish(
                            EventType.VISION_SCREEN_CHANGE,
                            {
                                "screenshot_path": screenshot_path,
                                "diff_percent": diff_percent,
                                "ts": current_time,
                            },
                        ),
                        loop,
                    )
                else:
                    logger.warning("Event Bus loop not available for Proactive Monitor")
            except Exception as e:
                logger.error(f"Failed to publish vision event: {e}")
        else:
            # Legacy Fallback
            threading.Thread(
                target=self._trigger_ai_analysis,
                args=(screenshot_path, diff_percent),
                daemon=True,
            ).start()

    def _trigger_ai_analysis(self, screenshot_path: str, diff_percent: float):
        """Analisa a mudanÃ§a via IA de forma assÃ­ncrona"""
        try:
            logger.info("Solicitando anÃ¡lise proativa ao Agente de IA...")
            # O Agente decide se fala ou nÃ£o apÃ³s ver a imagem
            ai_agent.process_proactive_analysis(
                {"screenshot_path": screenshot_path, "diff_percent": diff_percent}
            )

        except Exception as e:
            logger.error(f"Erro ao disparar anÃ¡lise proativa: {e}")


# InstÃ¢ncia global
proactive_monitor = ProactiveMonitor()
