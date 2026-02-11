import threading
import logging
import time

logger = logging.getLogger(__name__)

class ModelLoadLock:
    """
    Trava global para evitar que múltiplos modelos neurais pesados 
    sejam carregados simultaneamente, prevenindo crashes 0xC0000005 (Access Violation)
    em sistemas com CPU/RAM limitadas.
    """
    _lock = threading.Lock()
    _active_model = None

    @classmethod
    def acquire(cls, model_name: str):
        """Bloqueia o carregamento de outros modelos."""
        logger.info(f"🔒 [STABILITY] Solicitando trava para carregar: {model_name}")
        cls._lock.acquire()
        cls._active_model = model_name
        logger.info(f"✅ [STABILITY] Trava adquirida por: {model_name}")

    @classmethod
    def release(cls):
        """Libera para o próximo modelo."""
        model = cls._active_model
        cls._active_model = None
        cls._lock.release()
        logger.info(f"🔓 [STABILITY] Trava liberada (anterior: {model})")
        # Pequeno delay para respiro do SO/CPU
        time.sleep(1.0)

# Instância global para facilidade de importação
model_load_lock = ModelLoadLock
