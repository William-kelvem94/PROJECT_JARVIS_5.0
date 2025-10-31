"""
Circuit Breaker Pattern
Implementa padrão de circuit breaker para resiliência
"""

import time
from functools import wraps
from enum import Enum
from typing import Callable, Any, Optional
from core.logger import logger

class CircuitState(Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"  # Normal, permitindo requisições
    OPEN = "open"  # Falhou muito, bloqueando requisições
    HALF_OPEN = "half_open"  # Testando se recuperou

class CircuitBreaker:
    """
    Circuit Breaker para proteger contra falhas em cascata.
    Após N falhas, abre o circuito e bloqueia requisições por um período.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 2,
        expected_exception: type = Exception
    ):
        """
        Inicializa o circuit breaker.
        
        Args:
            failure_threshold: Número de falhas antes de abrir
            timeout: Tempo em segundos antes de tentar novamente (half-open)
            success_threshold: Sucessos necessários para fechar (half-open -> closed)
            expected_exception: Exceção esperada para contar como falha
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()
        
        logger.info(f"CircuitBreaker inicializado: threshold={failure_threshold}, timeout={timeout}s")
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator para aplicar circuit breaker a uma função.
        
        Args:
            func: Função a proteger
        
        Returns:
            Função wrapper
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função com proteção do circuit breaker.
        
        Args:
            func: Função a executar
            *args, **kwargs: Argumentos da função
        
        Returns:
            Resultado da função
        
        Raises:
            Exception: Se circuit breaker está aberto ou função falha
        """
        # Verificar estado atual
        self._check_state()
        
        if self.state == CircuitState.OPEN:
            raise Exception(
                f"Circuit breaker is OPEN. Failures: {self.failure_count}/"
                f"{self.failure_threshold}. Try again in {self.timeout - (time.time() - self.last_state_change):.1f}s"
            )
        
        # Tentar executar função
        try:
            result = func(*args, **kwargs)
            
            # Sucesso
            self._on_success()
            return result
            
        except self.expected_exception as e:
            # Falha esperada
            self._on_failure()
            raise e
            
        except Exception as e:
            # Outra exceção - não contar como falha se não for esperada
            # mas ainda propagar
            logger.warning(f"Exceção não esperada no circuit breaker: {e}")
            raise e
    
    def _check_state(self):
        """Atualiza estado do circuit breaker baseado no tempo."""
        now = time.time()
        
        if self.state == CircuitState.OPEN:
            # Verificar se já passou o timeout
            if now - self.last_state_change >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.last_state_change = now
                logger.info("Circuit breaker: OPEN -> HALF_OPEN (testando recuperação)")
    
    def _on_success(self):
        """Callback quando função executa com sucesso."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.debug(f"Sucesso no half-open: {self.success_count}/{self.success_threshold}")
            
            if self.success_count >= self.success_threshold:
                # Fechar circuit breaker
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = time.time()
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED (recuperado)")
        
        elif self.state == CircuitState.CLOSED:
            # Resetar contador de falhas em caso de sucesso
            if self.failure_count > 0:
                self.failure_count = 0
    
    def _on_failure(self):
        """Callback quando função falha."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.warning(f"Falha detectada: {self.failure_count}/{self.failure_threshold}")
        
        if self.state == CircuitState.HALF_OPEN:
            # Falhou no half-open, voltar para open
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.last_state_change = time.time()
            logger.warning("Circuit breaker: HALF_OPEN -> OPEN (ainda falhando)")
        
        elif self.state == CircuitState.CLOSED:
            # Verificar se atingiu threshold
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_state_change = time.time()
                logger.error(f"Circuit breaker: CLOSED -> OPEN (threshold atingido)")
    
    def reset(self):
        """Reseta o circuit breaker manualmente."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()
        logger.info("Circuit breaker resetado manualmente")
    
    def get_state(self) -> Dict[str, Any]:
        """Retorna estado atual do circuit breaker."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "success_count": self.success_count if self.state == CircuitState.HALF_OPEN else 0,
            "last_failure_time": self.last_failure_time,
            "time_since_last_state_change": time.time() - self.last_state_change if self.last_state_change else 0
        }

