"""
JARVIS 5.0 - Advanced Utilities
================================
Utilitários avançados para otimização de performance e segurança.
"""

import logging
import importlib
from typing import Any, Dict
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

logger = logging.getLogger(__name__)


class LazyLoader:
    """
    Lazy loader para módulos com cache inteligente.
    Evita imports pesados até que sejam necessários.
    """

    _modules: Dict[str, Any] = {}
    _loading_lock = threading.Lock()

    @classmethod
    def get_module(cls, name: str, package: str = "src") -> Any:
        """
        Carrega módulo sob demanda com cache.

        Args:
            name: Nome do módulo (ex: "core.actions.action_controller")
            package: Pacote base

        Returns:
            Módulo carregado
        """
        full_name = f"{package}.{name}" if package else name

        if full_name not in cls._modules:
            with cls._loading_lock:
                if full_name not in cls._modules:  # Double-check
                    try:
                        cls._modules[full_name] = importlib.import_module(full_name)
                        logger.debug(f"Lazy loaded module: {full_name}")
                    except ImportError as e:
                        logger.error(f"Failed to load module {full_name}: {e}")
                        raise

        return cls._modules[full_name]


class MemoryManager:
    """
    Gerenciador avançado de memória para otimização de recursos.
    """

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Retorna uso detalhado de memória"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": mem.total / (1024**3),
            "used_gb": mem.used / (1024**3),
            "free_gb": mem.free / (1024**3),
            "percent": mem.percent,
        }

    @staticmethod
    def force_garbage_collection():
        """Força coleta de lixo"""
        before = psutil.Process().memory_info().rss
        gc.collect()
        after = psutil.Process().memory_info().rss
        saved = before - after
        logger.info(f"Garbage collection: saved {saved / 1024 / 1024:.2f} MB")
        return saved

    @staticmethod
    def monitor_memory_threshold(threshold_mb: int = 1024) -> bool:
        """
        Monitora se uso de memória excedeu threshold.

        Args:
            threshold_mb: Threshold em MB

        Returns:
            True se excedeu o limite
        """
        usage = psutil.Process().memory_info().rss / 1024 / 1024
        if usage > threshold_mb:
            logger.warning(
                f"Memory usage exceeded threshold: {usage:.2f} MB > {threshold_mb} MB"
            )
            return True
        return False


class AsyncRunner:
    """
    Executor para operações assíncronas com controle de recursos.
    """

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="JARVIS-Async"
        )

    async def run_in_thread(self, func, *args, **kwargs):
        """
        Executa função síncrona em thread separada.

        Args:
            func: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados

        Returns:
            Resultado da função
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)

    def shutdown(self):
        """Encerra o executor"""
        self.executor.shutdown(wait=True)


# Singleton instances
lazy_loader = LazyLoader()
memory_manager = MemoryManager()
async_runner = AsyncRunner()

# Cleanup on exit
import atexit

atexit.register(async_runner.shutdown)
