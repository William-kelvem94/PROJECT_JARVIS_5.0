# src/core - Núcleo Principal do JARVIS 5.0
# Import centralizado dos principais componentes do core

from .agents import BaseAgent, RealtimeAgent, EngineerAgent, AgentFactory

__version__ = "5.0.0"

__all__ = ["BaseAgent", "RealtimeAgent", "EngineerAgent", "AgentFactory"]

