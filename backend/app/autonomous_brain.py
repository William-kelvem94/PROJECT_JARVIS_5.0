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
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            if cpu > 70 or ram > 85:
                return 120  # 2 minutos sob carga
            return 30  # 30 segundos ocioso
        except Exception:
            return 60  # fallback seguro

    async def _background_loop(self):
        # Primeira chamada para inicializar o psutil.cpu_percent()
        psutil.cpu_percent()

        logger.info("JARVIS Iniciou Modo de Pensamento Autônomo (integrado ao loop principal).")

        while self._running:
            try:
                interval = self._adaptive_interval()
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent

                if cpu > 90 or ram > 95:
                    logger.warning(f"[Autônomo] CARGA EXTREMA: CPU: {cpu}%, RAM: {ram}%")
                else:
                    logger.debug(f"[Autônomo] CPU: {cpu}%, RAM: {ram}%, Próximo ciclo: {interval}s")

                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"[Autônomo] Erro no loop: {e}")
                await asyncio.sleep(60)

    def start_background_thinking(self):
        """
        Inicia o loop de pensamento.
        Se já houver um loop rodando, ele agenda a tarefa no loop atual.
        """
        self._running = True
        try:
            # Tenta pegar o loop de eventos atual (do FastAPI/Uvicorn)
            loop = asyncio.get_running_loop()
            self._task = loop.create_task(self._background_loop())
            logger.info("Sincronizando Cérebro Autônomo com loop de eventos principal.")
        except RuntimeError:
            # Fallback para quando não há loop rodando (inicialização manual ou testes)
            logger.warning("Nenhum loop de eventos detectado. Iniciando loop síncrono de fallback.")
            asyncio.run(self._background_loop())

    def stop(self):
        """Para o loop autônomo."""
        self._running = False
        if self._task:
            self._task.cancel()

autonomous_brain = AutonomousBrain()
