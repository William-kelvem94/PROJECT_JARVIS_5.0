from PyQt6.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class UISignals(QObject):
    """
    Hub central de comunicações para a interface gráfica.
    Permite que threads de background (AI, Sensores, Voz) atualizem a UI de forma segura.
    Singleton Pattern.
    """

    _instance = None

    # Sinais para atualização da interface
    update_status = pyqtSignal(str)  # Texto de status dinâmico
    update_listening_state = pyqtSignal(
        bool
    )  # True = Ouvindo, False = Idle/Processando
    update_boot_stage = pyqtSignal(str, int)  # (Mensagem, Progresso 0-100)
    update_cpu_usage = pyqtSignal(float)  # Valor de uso de CPU para gráficos
    show_notification = pyqtSignal(str, str)  # (título, mensagem) pop-up
    update_learning_status = pyqtSignal(str, bool)  # (tópico_atual, is_studying)
    update_curiosity_list = pyqtSignal(list)  # Lista de tÃ³picos pendentes

    # Approval requests (from ActionValidator -> UI)
    approval_request_received = pyqtSignal(object)  # Event object (pending approval)

    def __new__(cls):
        if cls._instance is None:
            inst = super(UISignals, cls).__new__(cls)
            # Ensure the underlying QObject is initialized immediately to
            # avoid PyQt runtime errors when attributes are accessed before
            # Python-level __init__ completes.
            QObject.__init__(inst)
            cls._instance = inst
        return cls._instance

    def __init__(self):
        # Evitar reinicialização lógica se já instanciado via Singleton
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Para QObject no PyQt6, precisamos chamar o super().__init__()
        # ANTES de qualquer acesso a atributos para evitar RuntimeError.
        super().__init__()

        self._initialized = True
        logger.info("UISignals: Central de Sinais Stark inicializada.")


# Instância global para fácil acesso
ui_signals = UISignals()
