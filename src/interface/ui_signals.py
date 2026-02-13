from PyQt6.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class UISignals(QObject):
    """
    Hub central de comunicaÃ§Ãµes para a interface grÃ¡fica.
    Permite que threads de background (AI, Sensores, Voz) atualizem a UI de forma segura.
    Singleton Pattern.
    """
    _instance = None

    # Sinais para atualizaÃ§Ã£o da interface
    update_status = pyqtSignal(str)              # Texto de status dinÃ¢mico
    update_listening_state = pyqtSignal(bool)    # True = Ouvindo, False = Idle/Processando
    update_boot_stage = pyqtSignal(str, int)     # (Mensagem, Progresso 0-100)
    update_cpu_usage = pyqtSignal(float)         # Valor de uso de CPU para grÃ¡ficos
    show_notification = pyqtSignal(str, str)     # (tÃ­tulo, mensagem) pop-up

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UISignals, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Para QObject no PyQt6, precisamos chamar o super().__init__() 
        # ANTES de qualquer acesso a atributos para evitar RuntimeError.
        super().__init__()
        
        # Evitar reinicializaÃ§Ã£o lÃ³gica se jÃ¡ instanciado via Singleton
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        logger.info("ðŸ“¡ UISignals: Central de Sinais Stark inicializada.")

# InstÃ¢ncia global para fÃ¡cil acesso
ui_signals = UISignals()
