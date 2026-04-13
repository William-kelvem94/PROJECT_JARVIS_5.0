from typing import Optional, TYPE_CHECKING
from .tools import FileTools, SystemOSTools, BrowserTools, MemoryTools, AITools, PerceptionTools

if TYPE_CHECKING:
    from livekit.rtc import Room

class SystemTools(FileTools, SystemOSTools, BrowserTools, MemoryTools, AITools, PerceptionTools):
    """
    Ferramentas de Sistema Orquestradas do JARVIS 5.0.
    Esta classe agora é modular e herda funcionalidades de plugins independentes localizados em app/tools/.
    """
    def __init__(self, room: Optional["Room"] = None):
        # Inicializa a classe base (que por sua vez chama o init de todas as herdadas)
        super().__init__(room=room)
        
    # Adicione aqui métodos específicos que ainda não foram modularizados se necessário
