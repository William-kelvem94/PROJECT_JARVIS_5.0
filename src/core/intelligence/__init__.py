"""
ðŸ§  JARVIS Intelligence System - Sistema de InteligÃªncia
=====================================================

Este mÃ³dulo contÃ©m o nÃºcleo inteligente do JARVIS, incluindo agentes de IA,
processamento de linguagem natural, tomada de decisÃµes, gerenciamento de memÃ³ria
e sistemas neurais avanÃ§ados.

MÃ³dulos Principais:
- ai_agent: Agente principal de IA
- decision_engine: Motor de decisÃµes
- memory_manager: Gerenciamento de memÃ³ria
- context_sanitizer: SanitizaÃ§Ã£o de contexto
- neural_systems: Sistemas neurais
- perception_engine: Motor de percepÃ§Ã£o
- knowledge_graph: Grafo de conhecimento

Exemplo de uso:
    from src.core.intelligence import AIAgent, DecisionEngine

    agent = AIAgent()
    decision = DecisionEngine()
"""

from .ai_agent import AIAgent
from .decision_engine import DecisionEngine
from .memory import UnifiedMemoryManager as MemoryManager, memory_manager
from .context_sanitizer import ContextSanitizer
from .neural_systems import NeuralSystemsLoader
from .perception_engine import PerceptionEngine
from .knowledge_graph import KnowledgeGraph

__all__ = [
    "AIAgent",
    "DecisionEngine",
    "MemoryManager",
    "memory_manager",
    "ContextSanitizer",
    "NeuralSystemsLoader",
    "PerceptionEngine",
    "KnowledgeGraph",
]
