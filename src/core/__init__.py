"""JARVIS Core - Sistema Central de InteligÃªncia Artificial

Este mÃ³dulo contÃ©m todos os componentes centrais do JARVIS, incluindo:
- Orchestrator: Sistema de inicializaÃ§Ã£o e monitoramento de saÃºde
- Intelligence: MÃ³dulos de IA e processamento cognitivo
- Vision: Processamento de visÃ£o computacional
- Audio: Processamento de voz e Ã¡udio
- Actions: Sistema de execuÃ§Ã£o de comandos
- Management: Gerenciamento de sistema e recursos
- Security: Sistema de seguranÃ§a e validaÃ§Ã£o
- IoT: Controle de dispositivos inteligentes
- Engine: Motor de autonomia e geraÃ§Ã£o de cÃ³digo
"""

# Lazy import to avoid heavy dependencies at startup
def __getattr__(name):
    if name == "StarkOrchestrator":
        try:
            from .management.orchestrator import StarkOrchestrator
            return StarkOrchestrator
        except ImportError as e:
            print(f"WARNING: StarkOrchestrator not available: {e}")
            return None
    elif name == "AIAgent":
        try:
            from .intelligence.ai_agent import AIAgent
            return AIAgent
        except ImportError as e:
            print(f"WARNING: AIAgent not available: {e}")
            return None
    elif name == "VisionSystem":
        try:
            from .vision.vision_system import VisionSystem
            return VisionSystem
        except ImportError as e:
            print(f"WARNING: VisionSystem not available: {e}")
            return None
    elif name == "VoiceController":
        try:
            from .audio.voice_controller import VoiceController
            return VoiceController
        except ImportError as e:
            print(f"WARNING: VoiceController not available: {e}")
            return None
    elif name == "ActionController":
        try:
            from .actions.action_controller import ActionController
            return ActionController
        except ImportError as e:
            print(f"WARNING: ActionController not available: {e}")
            return None
    elif name == "ShutdownManager":
        try:
            from .management.shutdown_manager import ShutdownManager
            return ShutdownManager
        except ImportError as e:
            print(f"WARNING: ShutdownManager not available: {e}")
            return None
    elif name == "FallbackSystem":
        try:
            from .management.fallback_system import FallbackSystem
            return FallbackSystem
        except ImportError as e:
            print(f"WARNING: FallbackSystem not available: {e}")
            return None
    elif name == "SecurityManager":
        try:
            from .security.security_manager import SecurityManager
            return SecurityManager
        except ImportError as e:
            print(f"WARNING: SecurityManager not available: {e}")
            return None
    elif name == "IOTManager":
        try:
            from .iot.iot_manager import IOTManager
            return IOTManager
        except ImportError as e:
            print(f"WARNING: IOTManager not available: {e}")
            return None
    elif name == "AutonomyCore":
        try:
            from .engine.autonomy import AutonomyCore
            return AutonomyCore
        except ImportError as e:
            print(f"WARNING: AutonomyCore not available: {e}")
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Initialize all to None to avoid import errors
AIAgent = None
VisionSystem = None
VoiceController = None
ActionController = None
ShutdownManager = None
FallbackSystem = None
SecurityManager = None
IOTManager = None
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
