"""
Health Checks para Módulos
Verifica saúde e disponibilidade de cada módulo
"""

import time
from typing import Dict, Any, List, Optional, Callable
from core.logger import logger

class HealthCheck:
    """
    Health check para um módulo.
    Executa verificações periódicas.
    """
    
    def __init__(
        self,
        module_name: str,
        check_function: Callable[[], bool],
        check_interval: float = 30.0,
        timeout: float = 5.0
    ):
        """
        Inicializa health check.
        
        Args:
            module_name: Nome do módulo
            check_function: Função que retorna True se saudável
            check_interval: Intervalo entre verificações (segundos)
            timeout: Timeout máximo para verificação
        """
        self.module_name = module_name
        self.check_function = check_function
        self.check_interval = check_interval
        self.timeout = timeout
        
        self.last_check = None
        self.last_result = None
        self.consecutive_failures = 0
        
        logger.info(f"HealthCheck criado para {module_name}")
    
    def check(self) -> Dict[str, Any]:
        """
        Executa verificação de saúde.
        
        Returns:
            Resultado do health check
        """
        start_time = time.time()
        
        try:
            result = self.check_function()
            check_time = time.time() - start_time
            
            if result:
                self.consecutive_failures = 0
                status = "healthy"
            else:
                self.consecutive_failures += 1
                status = "degraded" if self.consecutive_failures < 3 else "unhealthy"
            
            self.last_result = result
            self.last_check = time.time()
            
            return {
                "module": self.module_name,
                "status": status,
                "healthy": result,
                "check_time": check_time,
                "consecutive_failures": self.consecutive_failures,
                "timestamp": self.last_check
            }
            
        except Exception as e:
            self.consecutive_failures += 1
            self.last_check = time.time()
            
            logger.error(f"Erro no health check de {self.module_name}: {e}")
            
            return {
                "module": self.module_name,
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "consecutive_failures": self.consecutive_failures,
                "timestamp": self.last_check
            }
    
    def is_due(self) -> bool:
        """Verifica se é hora de executar check."""
        if self.last_check is None:
            return True
        return (time.time() - self.last_check) >= self.check_interval


class HealthCheckManager:
    """
    Gerencia health checks de múltiplos módulos.
    """
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        logger.info("HealthCheckManager inicializado")
    
    def register_check(
        self,
        module_name: str,
        check_function: Callable[[], bool],
        check_interval: float = 30.0
    ):
        """
        Registra health check para um módulo.
        
        Args:
            module_name: Nome do módulo
            check_function: Função que verifica saúde
            check_interval: Intervalo entre verificações
        """
        health_check = HealthCheck(module_name, check_function, check_interval)
        self.health_checks[module_name] = health_check
        logger.info(f"Health check registrado: {module_name}")
    
    def check_all(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Executa health checks de todos os módulos.
        
        Args:
            force: Se True, força verificação mesmo se não for hora
        
        Returns:
            Resultados de todos os health checks
        """
        results = {}
        
        for module_name, health_check in self.health_checks.items():
            if force or health_check.is_due():
                results[module_name] = health_check.check()
        
        return results
    
    def get_status(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém status de um módulo.
        
        Args:
            module_name: Nome do módulo
        
        Returns:
            Status ou None se não encontrado
        """
        health_check = self.health_checks.get(module_name)
        if health_check:
            return health_check.check()
        return None
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtém status de todos os módulos."""
        return {
            name: check.check() if check.is_due() else {
                "module": name,
                "status": "cached",
                "last_check": check.last_check
            }
            for name, check in self.health_checks.items()
        }

