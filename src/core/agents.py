from typing import Optional, List, Dict, Any
from loguru import logger
import abc

class BaseAgent(abc.ABC):
    @abc.abstractmethod
    async def run(self, input_text: str, context: Optional[str] = None) -> str:
        pass

class RealtimeAgent(BaseAgent):
    """
    Agente especializado em interações em tempo real (Gemini Realtime PRO).
    Integrado com o ecossistema JARVIS 5.0.
    """
    def __init__(self, model_name: str = "gemini-1.5-pro-realtime-next"):
        self.model_name = model_name
        logger.info(f"RealtimeAgent inicializado com modelo: {model_name}")

    async def run(self, input_text: str, context: Optional[str] = None) -> str:
        # Implementação futura do Stream Realtime
        logger.debug(f"Processando entrada realtime: {input_text[:50]}...")
        return f"[RealtimeAgent Stub] Echo: {input_text}"

class EngineerAgent(BaseAgent):
    """
    Agente com foco em tarefas de engenharia e modificação de código.
    """
    async def run(self, input_text: str, context: Optional[str] = None) -> str:
        from ...backend.app.engineer_brain import brain
        return await brain.reason(input_text, context or "")

# Singleton Factory
class AgentFactory:
    @staticmethod
    def get_agent(agent_type: str = "realtime") -> BaseAgent:
        if agent_type == "realtime":
            return RealtimeAgent()
        elif agent_type == "engineer":
            return EngineerAgent()
        return RealtimeAgent()
