"""
Sistema de Monitoramento e Telemetria
Rastreia performance, erros e saúde do sistema
"""

import time
import threading
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime
from core.logger import logger

class SystemMonitor:
    """
    Monitor do sistema que rastreia:
    - Tempos de resposta
    - Taxa de erros
    - Saúde dos módulos
    - Métricas de uso
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Inicializa o monitor do sistema.
        
        Args:
            max_history: Número máximo de métricas a manter em histórico
        """
        self.max_history = max_history
        
        # Métricas de performance
        self.metrics = {
            "response_times": deque(maxlen=max_history),
            "error_rates": {},  # module -> list of errors
            "module_health": {},  # module -> health status
            "request_counts": {},  # module -> count
            "success_counts": {},  # module -> count
        }
        
        # Lock para thread-safety
        self.lock = threading.Lock()
        
        logger.info("SystemMonitor inicializado")
    
    def track_performance(
        self,
        module: str,
        execution_time: float,
        success: bool = True
    ):
        """
        Rastreia performance de um módulo.
        
        Args:
            module: Nome do módulo
            execution_time: Tempo de execução em segundos
            success: Se execução foi bem-sucedida
        """
        with self.lock:
            timestamp = time.time()
            
            # Adicionar tempo de resposta
            self.metrics["response_times"].append({
                "module": module,
                "time": execution_time,
                "timestamp": timestamp,
                "success": success
            })
            
            # Contar requisições
            if module not in self.metrics["request_counts"]:
                self.metrics["request_counts"][module] = 0
                self.metrics["success_counts"][module] = 0
            
            self.metrics["request_counts"][module] += 1
            
            if success:
                self.metrics["success_counts"][module] += 1
    
    def track_error(self, module: str, error: Exception, context: Optional[Dict] = None):
        """
        Rastreia um erro.
        
        Args:
            module: Nome do módulo
            error: Exceção ocorrida
            context: Contexto adicional (opcional)
        """
        with self.lock:
            if module not in self.metrics["error_rates"]:
                self.metrics["error_rates"][module] = deque(maxlen=100)
            
            self.metrics["error_rates"][module].append({
                "error": str(error),
                "error_type": type(error).__name__,
                "timestamp": time.time(),
                "context": context
            })
            
            logger.warning(f"Erro rastreado em {module}: {error}")
    
    def set_module_health(self, module: str, health: str, details: Optional[Dict] = None):
        """
        Define saúde de um módulo.
        
        Args:
            module: Nome do módulo
            health: "healthy", "degraded", "unhealthy", "unknown"
            details: Detalhes adicionais (opcional)
        """
        with self.lock:
            self.metrics["module_health"][module] = {
                "status": health,
                "last_check": time.time(),
                "details": details or {}
            }
    
    def get_module_health(self, module: str) -> Dict[str, Any]:
        """
        Obtém saúde de um módulo.
        
        Args:
            module: Nome do módulo
        
        Returns:
            Status de saúde
        """
        with self.lock:
            return self.metrics["module_health"].get(module, {
                "status": "unknown",
                "last_check": None,
                "details": {}
            })
    
    def get_module_performance(self, module: str) -> Dict[str, Any]:
        """
        Obtém métricas de performance de um módulo.
        
        Args:
            module: Nome do módulo
        
        Returns:
            Métricas de performance
        """
        with self.lock:
            # Filtrar métricas do módulo
            module_times = [
                m for m in self.metrics["response_times"]
                if m["module"] == module
            ]
            
            if not module_times:
                return {
                    "module": module,
                    "total_requests": 0,
                    "avg_time": 0.0,
                    "min_time": 0.0,
                    "max_time": 0.0,
                    "success_rate": 0.0
                }
            
            times = [m["time"] for m in module_times]
            successes = [m for m in module_times if m.get("success", True)]
            
            total_requests = self.metrics["request_counts"].get(module, 0)
            success_count = self.metrics["success_counts"].get(module, 0)
            
            return {
                "module": module,
                "total_requests": total_requests,
                "successful_requests": success_count,
                "success_rate": success_count / total_requests if total_requests > 0 else 0.0,
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "recent_count": len(module_times)
            }
    
    def get_error_summary(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém resumo de erros.
        
        Args:
            module: Filtrar por módulo (None para todos)
        
        Returns:
            Resumo de erros
        """
        with self.lock:
            if module:
                errors = self.metrics["error_rates"].get(module, deque())
                return {
                    "module": module,
                    "error_count": len(errors),
                    "recent_errors": list(errors)[-10:]  # Últimos 10
                }
            else:
                summary = {}
                for mod, errors in self.metrics["error_rates"].items():
                    summary[mod] = {
                        "error_count": len(errors),
                        "recent_errors": list(errors)[-5] if errors else []
                    }
                return summary
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do sistema."""
        with self.lock:
            all_times = list(self.metrics["response_times"])
            
            if not all_times:
                return {
                    "total_requests": 0,
                    "avg_response_time": 0.0,
                    "modules_count": len(self.metrics["module_health"]),
                    "total_errors": 0
                }
            
            times = [m["time"] for m in all_times]
            
            # Calcular erros totais
            total_errors = sum(len(errors) for errors in self.metrics["error_rates"].values())
            
            return {
                "total_requests": len(all_times),
                "avg_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "modules_monitored": len(self.metrics["module_health"]),
                "modules_with_errors": len(self.metrics["error_rates"]),
                "total_errors": total_errors,
                "timestamp": time.time()
            }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Gera relatório completo de saúde do sistema."""
        with self.lock:
            report = {
                "timestamp": datetime.now().isoformat(),
                "overall_stats": self.get_overall_stats(),
                "modules": {}
            }
            
            # Status de cada módulo
            for module in set(list(self.metrics["module_health"].keys()) + 
                            list(self.metrics["request_counts"].keys())):
                report["modules"][module] = {
                    "health": self.get_module_health(module),
                    "performance": self.get_module_performance(module),
                    "errors": self.get_error_summary(module).get("error_count", 0)
                }
            
            return report
    
    def clear_metrics(self, module: Optional[str] = None):
        """
        Limpa métricas.
        
        Args:
            module: Se especificado, limpa apenas deste módulo
        """
        with self.lock:
            if module:
                # Limpar métricas específicas do módulo
                self.metrics["response_times"] = deque([
                    m for m in self.metrics["response_times"]
                    if m["module"] != module
                ], maxlen=self.max_history)
                
                if module in self.metrics["error_rates"]:
                    del self.metrics["error_rates"][module]
                
                if module in self.metrics["module_health"]:
                    del self.metrics["module_health"][module]
            else:
                # Limpar tudo
                self.metrics["response_times"].clear()
                self.metrics["error_rates"].clear()
                self.metrics["module_health"].clear()
                self.metrics["request_counts"].clear()
                self.metrics["success_counts"].clear()
            
            logger.info(f"Métricas limpas para {module or 'todo o sistema'}")

