"""
Monitor Proativo do Jarvis (Proactive Monitor)
Detecta mudanças significativas na tela em tempo real e aciona o Agente de IA proativamente.
"""

import cv2
import numpy as np
import time
import threading
import logging
from pathlib import Path
from src.core.vision.screen_capture import screen_capture
from src.core.intelligence.ai_agent import ai_agent
from src.utils.config import config

logger = logging.getLogger(__name__)

class ProactiveMonitor:
    """Daemon que observa a tela em busca de mudanças (Deltas) e toma iniciativa"""

    def __init__(self, check_interval: float = 3.0, sensitivity: float = 0.05):
        self.check_interval = check_interval
        self.sensitivity = sensitivity # Porcentagem de pixels alterados para disparar
        self.running = False
        self.thread = None
        self.last_frame = None
        
        # Cooldown para não ser irritante (segundos)
        self.last_trigger_time = 0
        self.cooldown = 60 

    def start(self):
        """Inicia o monitoramento em background"""
        if self.running: return
        
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
        """Loop principal de observação"""
        while self.running:
            try:
                # Capturar frame atual (em baixa resolução para performance)
                screenshot = screen_capture.capture_fullscreen(capture_type='monitor')
                if not screenshot:
                    time.sleep(self.check_interval)
                    continue

                frame = cv2.imread(screenshot)
                if frame is None:
                    time.sleep(self.check_interval)
                    continue

                # Converter para escala de cinza e aplicar blur para ignorar ruído pequeno
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if self.last_frame is None:
                    self.last_frame = gray
                    time.sleep(self.check_interval)
                    continue

                # Calcular diferença absoluta entre o frame atual e o anterior
                frame_delta = cv2.absdiff(self.last_frame, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                
                # Dilatar para agrupar mudanças próximas
                thresh = cv2.dilate(thresh, None, iterations=2)
                
                # Calcular porcentagem de mudança
                change_percent = (np.count_nonzero(thresh) / thresh.size)
                
                if change_percent > self.sensitivity:
                    logger.info(f"Mudança significativa detectada: {change_percent:.2%}")
                    self._handle_change(screenshot, change_percent * 100)


                self.last_frame = gray
                
            except Exception as e:
                logger.error(f"Erro no loop do Monitor Proativo: {e}")
            
            time.sleep(self.check_interval)

    def _handle_change(self, screenshot_path: str, diff_percent: float):
        """Decide se deve ou não acionar a IA baseada no cooldown e estado"""
        current_time = time.time()
        
        if (current_time - self.last_trigger_time) < self.cooldown:
            logger.debug("Mudança ignorada devido ao cooldown.")
            return

        # Acionar o Agente de IA para análise proativa
        self.last_trigger_time = current_time
        threading.Thread(target=self._trigger_ai_analysis, args=(screenshot_path, diff_percent), daemon=True).start()


    def _trigger_ai_analysis(self, screenshot_path: str, diff_percent: float):
        """Analisa a mudança via IA de forma assíncrona"""
        try:
            logger.info("Solicitando análise proativa ao Agente de IA...")
            # O Agente decide se fala ou não após ver a imagem
            ai_agent.process_proactive_analysis({
                "screenshot_path": screenshot_path,
                "diff_percent": diff_percent
            })

        except Exception as e:
            logger.error(f"Erro ao disparar análise proativa: {e}")

# Instância global
proactive_monitor = ProactiveMonitor()
