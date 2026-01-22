"""
Sistema de Retry com Backoff Exponencial
"""

import time
import random
from functools import wraps
from typing import Callable, Type, Tuple, Optional
from core.logger import logger

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator para retry com backoff exponencial.
    
    Args:
        max_attempts: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        exponential_base: Base para cálculo exponencial
        jitter: Se True, adiciona aleatoriedade ao delay
        exceptions: Tupla de exceções que devem triggerar retry
    
    Returns:
        Decorator
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(f"Falha após {max_attempts} tentativas em {func.__name__}: {e}")
                        raise e
                    
                    # Calcular delay
                    delay = min(
                        initial_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )
                    
                    # Adicionar jitter se habilitado
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(
                        f"Tentativa {attempt}/{max_attempts} falhou em {func.__name__}. "
                        f"Retentando em {delay:.2f}s: {e}"
                    )
                    
                    time.sleep(delay)
            
            # Não deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

