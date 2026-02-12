"""JARVIS Core - Sistema Central de Inteligência Artificial

Este módulo contém todos os componentes centrais do JARVIS, incluindo:
- Orchestrator: Sistema de inicialização e monitoramento de saúde
- Intelligence: Módulos de IA e processamento cognitivo
- Vision: Processamento de visão computacional
- Audio: Processamento de voz e áudio
- Actions: Sistema de execução de comandos
- Management: Gerenciamento de sistema e recursos
- Security: Sistema de segurança e validação
- IoT: Controle de dispositivos inteligentes
- Engine: Motor de autonomia e geração de código
"""

from .orchestrator import StarkOrchestrator

# Safe imports - algumas classes podem não estar disponíveis
try:
    from .intelligence.ai_agent import AIAgent
except ImportError:
    AIAgent = None

try:
    from .vision.vision_system import VisionSystem
except ImportError:
    VisionSystem = None

try:
    from .audio.voice_controller import VoiceController
except ImportError:
    VoiceController = None

try:
    from .actions.action_controller import ActionController
except ImportError:
    ActionController = None

try:
    from .management.shutdown_manager import ShutdownManager
except ImportError:
    ShutdownManager = None

try:
    from .management.fallback_system import FallbackSystem
except ImportError:
    FallbackSystem = None

try:
    from .security.security_manager import SecurityManager
except ImportError:
    SecurityManager = None

try:
    from .iot.iot_manager import IOTManager
except ImportError:
    IOTManager = None

try:
    from .engine.autonomy import AutonomyCore
except ImportError:
    AutonomyCore = None

__all__ = [
    'StarkOrchestrator',
    'AIAgent', 
    'VisionSystem',
    'VoiceController',
    'ActionController', 
    'ShutdownManager',
    'FallbackSystem',
    'SecurityManager',
    'IOTManager',
    'AutonomyCore'
]
