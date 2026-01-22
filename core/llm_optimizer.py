"""
LLM Optimizer - Otimização automática de parâmetros baseado em recursos
Ajusta dinamicamente parâmetros para melhor performance
"""

from typing import Dict, Any, Optional
from core.logger import logger

class LLMOptimizer:
    """
    Otimizador de parâmetros LLM baseado em recursos do sistema.
    Ajusta automaticamente para melhor performance mantendo qualidade.
    """
    
    def __init__(self, capabilities: Dict[str, Any]):
        """
        Inicializa otimizador com capacidades do sistema.
        
        Args:
            capabilities: Dicionário de capacidades do CapabilityDetector
        """
        self.capabilities = capabilities
        self._calculate_optimal_params()
        
    def _calculate_optimal_params(self):
        """Calcula parâmetros ótimos baseado em recursos."""
        memory_total = self.capabilities.get("memory", {}).get("total_gb", 0)
        memory_available = self.capabilities.get("memory", {}).get("available_gb", 0)
        cpu_cores = self.capabilities.get("cpu", {}).get("cores", 0)
        gpu_available = self.capabilities.get("gpu", {}).get("cuda_available", False)
        
        # Calcular score de recursos (0.0 a 1.0)
        resource_score = 0.0
        
        # Score de RAM (peso 40%)
        if memory_total >= 32:
            resource_score += 0.4
        elif memory_total >= 16:
            resource_score += 0.3
        elif memory_total >= 8:
            resource_score += 0.2
        else:
            resource_score += 0.1
        
        # Score de CPU (peso 30%)
        if cpu_cores >= 16:
            resource_score += 0.3
        elif cpu_cores >= 8:
            resource_score += 0.2
        elif cpu_cores >= 4:
            resource_score += 0.15
        else:
            resource_score += 0.1
        
        # Score de GPU (peso 30%)
        if gpu_available:
            resource_score += 0.3
        
        self.resource_score = min(1.0, resource_score)
        
        # Calcular parâmetros ótimos
        if self.resource_score >= 0.8:
            # Sistema robusto - pode usar parâmetros mais completos
            self.optimal_params = {
                "max_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 50,
                "repeat_penalty": 1.1,
                "num_threads": min(cpu_cores, 8),
                "num_gpu": 1 if gpu_available else 0,
                "batch_size": 512
            }
        elif self.resource_score >= 0.5:
            # Sistema médio - balanceado
            self.optimal_params = {
                "max_tokens": 200,
                "temperature": 0.65,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "num_threads": min(cpu_cores, 6),
                "num_gpu": 1 if gpu_available else 0,
                "batch_size": 256
            }
        else:
            # Sistema limitado - otimizado para velocidade
            self.optimal_params = {
                "max_tokens": 150,
                "temperature": 0.6,
                "top_p": 0.85,
                "top_k": 30,
                "repeat_penalty": 1.15,
                "num_threads": min(cpu_cores, 4),
                "num_gpu": 0,
                "batch_size": 128
            }
        
        # Ajustar baseado em RAM disponível
        if memory_available < 4:
            # RAM muito limitada - reduzir ainda mais
            self.optimal_params["max_tokens"] = min(self.optimal_params["max_tokens"], 100)
            self.optimal_params["batch_size"] = min(self.optimal_params["batch_size"], 64)
        
        logger.info(f"Parâmetros ótimos calculados (score: {self.resource_score:.2f}): max_tokens={self.optimal_params['max_tokens']}, threads={self.optimal_params['num_threads']}")
    
    def get_optimal_params(self, **override) -> Dict[str, Any]:
        """
        Retorna parâmetros ótimos, permitindo override.
        
        Args:
            **override: Parâmetros para sobrescrever
        
        Returns:
            Dicionário de parâmetros otimizados
        """
        params = self.optimal_params.copy()
        params.update(override)
        return params
    
    def optimize_for_speed(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Otimiza parâmetros existentes para velocidade máxima.
        
        Args:
            base_params: Parâmetros base
        
        Returns:
            Parâmetros otimizados para velocidade
        """
        optimized = base_params.copy()
        
        # Reduzir tokens para respostas mais rápidas
        if "max_tokens" in optimized:
            optimized["max_tokens"] = min(optimized["max_tokens"], 200)
        
        # Temperature mais baixa = menos sampling = mais rápido
        if "temperature" in optimized:
            optimized["temperature"] = min(optimized["temperature"], 0.65)
        
        # Reduzir top_k para menos computação
        if "top_k" in optimized:
            optimized["top_k"] = min(optimized.get("top_k", 40), 35)
        
        return optimized
    
    def get_timeout(self) -> int:
        """
        Calcula timeout ótimo baseado em recursos.
        
        Returns:
            Timeout em segundos
        """
        if self.resource_score >= 0.8:
            return 60  # Sistema robusto
        elif self.resource_score >= 0.5:
            return 45  # Sistema médio
        else:
            return 30  # Sistema limitado

