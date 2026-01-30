"""
JARVIS Ultimate - Infraestrutura de Vida Artificial

Este pacote contém todos os componentes do JARVIS Ultimate:
- Sistema RAG com aprendizado contínuo
- Controle inteligente de hardware
- Reconhecimento e síntese de voz
- Gerenciamento avançado de modelos de IA
"""

__version__ = "1.0.0"
__author__ = "JARVIS Ultimate"
__description__ = "Infraestrutura de Vida Artificial com IA"

from .config import config
from .main import JarvisUltimate

__all__ = ["config", "JarvisUltimate"]