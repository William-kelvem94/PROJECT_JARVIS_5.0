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
            # Não use interval=1 aqui, pois ele bloqueia a thread por 1 segundo inteiro.
            # O cpu_percent(interval=None) retorna o valor desde a última chamada.
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            if cpu > 70 or ram > 85:
                return 120  # 2 minutos sob carga (reduzido de 5 para ser mais responsivo)
            return 30  # 30 segundos ocioso
        except Exception:
            return 60  # fallback seguro

    async def _background_loop(self):
        # Primeira chamada para inicializar o psutil.cpu_percent()
        psutil.cpu_percent()
        
        while self._running:
            try:
                interval = self._adaptive_interval()

                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                
                # Só loga em debug para não poluir o terminal, a menos que seja crítico
                if cpu > 90 or ram > 95:
                    logger.warning(f"[Autônomo] CARGA EXTREMA: CPU: {cpu}%, RAM: {ram}%")
                else:
                    logger.debug(f"[Autônomo] CPU: {cpu}%, RAM: {ram}%, Próximo ciclo: {interval}s")

                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"[Autônomo] Erro no loop: {e}")
                await asyncio.sleep(60)

    def start_background_thinking(self):
        """Inicia o loop de pensamento em background."""
        self._running = True
        # Cria um novo loop de eventos para esta thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("JARVIS Iniciou Modo de Pensamento Autônomo (intervalo adaptativo).")
        try:
            loop.run_until_complete(self._background_loop())
        except Exception as e:
            logger.error(f"[Autônomo] Falha crítica na thread: {e}")
        finally:
            loop.close()

    def stop(self):
        """Para o loop autônomo."""
        self._running = False
        if self._task:
            try:
                self._task.cancel()
            except Exception:
                pass


autonomous_brain = AutonomousBrain()
