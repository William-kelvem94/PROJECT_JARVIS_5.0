"""
JARVIS 5.0 - Cérebro Autônomo (Loop de Pensamento Proativo)
Monitora o sistema e o Obsidian em background com intervalo adaptativo.
"""

import asyncio
import psutil
from loguru import logger


class AutonomousBrain:
    def __init__(self):
        self._running = False
        self._task = None

    def _adaptive_interval(self) -> int:
        """Intervalo adaptativo baseado na carga do sistema."""
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            if cpu > 60 or ram > 80:
                return 300  # 5 minutos sob carga
            return 60  # 1 minuto ocioso
        except Exception:
            return 120  # fallback seguro

    async def _background_loop(self):
        while self._running:
            try:
                interval = self._adaptive_interval()

                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                logger.debug(f"[Autônomo] CPU: {cpu}%, RAM: {ram}%, Próximo ciclo: {interval}s")

                if cpu > 90 or ram > 95:
                    logger.warning("[Autônomo] ALERTA: O processador/memória está sob carga extrema.")

                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"[Autônomo] Erro no loop: {e}")
                await asyncio.sleep(60)

    def start_background_thinking(self):
        """Inicia o loop de pensamento em background."""
        self._running = True
        self._task = asyncio.run(self._background_loop())
        logger.info("JARVIS Iniciou Modo de Pensamento Autônomo (intervalo adaptativo).")

    def stop(self):
        """Para o loop autônomo."""
        self._running = False
        if self._task:
            try:
                self._task.cancel()
            except Exception:
                pass


autonomous_brain = AutonomousBrain()
