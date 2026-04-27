import asyncio
import time
import psutil
from loguru import logger
from .config import settings
from .tools.system_executor import system_executor
from .utils.second_brain_connector import second_brain

# Intervalos adaptativos: ocioso vs sob carga
_INTERVAL_IDLE = 60      # 1 min quando CPU/RAM baixos
_INTERVAL_BUSY = 300     # 5 min quando sob carga
_CPU_BUSY_THRESHOLD = 60 # % de CPU para considerar "ocupado"

class AutonomousBrain:
    """
    O loop de pensamento em background (Proatividade).
    O Jarvis agora 'acorda' sozinho para monitorar o ambiente e a agenda.
    O intervalo é adaptativo: menor quando ocioso, maior quando sob carga.
    """
    
    def __init__(self, websocket_manager=None):
        self.ws_manager = websocket_manager
        self._running = False
        self._last_system_check = 0

    def _adaptive_interval(self) -> int:
        """Retorna intervalo em segundos baseado na carga atual do sistema."""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            if cpu > _CPU_BUSY_THRESHOLD or ram > 80:
                return _INTERVAL_BUSY
        except Exception:
            pass
        return _INTERVAL_IDLE

    async def start_background_thinking(self, websocket=None):
        """Inicia o loop proativo."""
        if self._running: return
        self._running = True
        logger.info("🧠 JARVIS Iniciou Modo de Pensamento Autônomo.")
        
        while self._running:
            try:
                interval = self._adaptive_interval()
                logger.debug(f"[Autônomo] Próxima verificação em {interval}s.")

                # 1. MONITORAMENTO DE SAÚDE
                health_report = system_executor.system_status_report()
                if "ALERTA" in health_report:
                    logger.warning(f"[Autônomo] {health_report}")
                    if websocket:
                        await websocket.send_json({
                            "type": "proactive_alert",
                            "message": health_report
                        })

                # 2. MONITORAMENTO DE AGENDA & TAREFAS (Obsidian + GraphRAG)
                if second_brain.active_todos:
                    logger.info(f"[Autônomo] Analisando {len(second_brain.active_todos)} tarefas do Obsidian...")
                    try:
                        from .utils.obsidian_graph import obsidian_graph
                        for todo in second_brain.active_todos[:3]:
                            related = obsidian_graph.query_related(todo)
                            if related:
                                logger.info(f"[Autônomo] Insight: A tarefa '{todo}' está ligada a: {', '.join(related)}")
                    except: pass
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Erro no loop autônomo: {e}")
                await asyncio.sleep(60)

autonomous_brain = AutonomousBrain()
