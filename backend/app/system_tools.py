from typing import Optional
from .tools import FileTools, SystemOSTools, BrowserTools, MemoryTools, AITools, PerceptionTools

class SystemTools(FileTools, SystemOSTools, BrowserTools, MemoryTools, AITools, PerceptionTools):
    """
    Ferramentas de Sistema Orquestradas do JARVIS 5.0.
    Esta classe agora é modular e herda funcionalidades de plugins independentes localizados em app/tools/.
    """
    def __init__(self):
        # Inicializa a classe base (que por sua vez chama o init de todas as herdadas)
        super().__init__()
        
    # Adicione aqui métodos específicos que ainda não foram modularizados se necessário
