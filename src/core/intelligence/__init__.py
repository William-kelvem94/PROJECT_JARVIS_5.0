"""
🧠 JARVIS Intelligence System - Sistema de Inteligência
=====================================================

Este módulo contém o núcleo inteligente do JARVIS, incluindo agentes de IA,
processamento de linguagem natural, tomada de decisões, gerenciamento de memória
e sistemas neurais avançados.

Módulos Principais:
- ai_agent: Agente principal de IA
- decision_engine: Motor de decisões
- memory_manager: Gerenciamento de memória
- context_sanitizer: Sanitização de contexto
- neural_systems: Sistemas neurais
- perception_engine: Motor de percepção
- knowledge_graph: Grafo de conhecimento

Exemplo de uso:
    from src.core.intelligence import AIAgent, DecisionEngine

    agent = AIAgent()
    decision = DecisionEngine()
"""

from .ai_agent import AIAgent
from .decision_engine import DecisionEngine
from .memory_manager import MemoryManager
from .context_sanitizer import ContextSanitizer
from .neural_systems import NeuralSystemsLoader
from .perception_engine import PerceptionEngine
from .knowledge_graph import KnowledgeGraph

__all__ = [
    'AIAgent',
    'DecisionEngine',
    'MemoryManager',
    'ContextSanitizer',
    'NeuralSystemsLoader',
    'PerceptionEngine',
    'KnowledgeGraph'
]
