import asyncio
import time
from loguru import logger
from .config import settings
from .tools.system_executor import system_executor
from .utils.second_brain_connector import second_brain

class AutonomousBrain:
    """
    O loop de pensamento em background (Proatividade).
    O Jarvis agora 'acorda' sozinho para monitorar o ambiente e a agenda.
    """
    
    def __init__(self, websocket_manager=None):
        self.ws_manager = websocket_manager
        self._running = False
        self._last_system_check = 0
        self._check_interval = 600 # 10 Minutos

    async def start_background_thinking(self, websocket=None):
        """Inicia o loop proativo."""
        if self._running: return
        self._running = True
        logger.info("🧠 JARVIS Iniciou Modo de Pensamento Autônomo.")
        
        while self._running:
            try:
                # 1. MONITORAMENTO DE SAÚDE (A cada 10 min)
                health_report = system_executor.system_status_report()
                if "ALERTA" in health_report:
                    logger.warning(f"[Autônomo] {health_report}")
                    if websocket:
                        await websocket.send_json({
                            "type": "proactive_alert",
                            "message": health_report
                        })

                # 2. MONITORAMENTO DE AGENDA & TAREFAS (Obsidian)
                if second_brain.active_todos:
                    # Logica proativa: Se houver muitas tarefas ou algo urgente
                    logger.info(f"[Autônomo] Analisando {len(second_brain.active_todos)} tarefas do Obsidian...")
                    # Futuramente: Injetar analise de LLM proativa aqui
                
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                logger.error(f"Erro no loop autônomo: {e}")
                await asyncio.sleep(60)

autonomous_brain = AutonomousBrain()
