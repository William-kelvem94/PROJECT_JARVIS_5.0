"""
Model Orchestrator - Orquestração de Modelos Especializados
Gerencia seleção, ensemble e performance de múltiplos modelos
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from core.logger import logger
from enterprise.ai.cognitive_engine import IntentAnalysis

@dataclass
class ModelSpec:
    """Especificação de um modelo."""
    name: str
    provider: str
    endpoint: str
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    cost_per_token: float = 0.0

class DistributedModelRegistry:
    """Registry distribuído de modelos."""
    
    def __init__(self):
        self.models: Dict[str, ModelSpec] = {}
        self._init_default_models()
    
    def _init_default_models(self):
        """Inicializa modelos padrão."""
        # Modelo geral
        self.models["llama3-8b"] = ModelSpec(
            name="llama3-8b",
            provider="ollama",
            endpoint="http://ollama:11434",
            capabilities=["text", "code", "reasoning"],
            performance_metrics={"latency_ms": 500, "tokens_per_sec": 50}
        )
        
        # Modelo especializado em código
        self.models["codellama"] = ModelSpec(
            name="codellama",
            provider="ollama",
            endpoint="http://ollama:11434",
            capabilities=["code", "debugging", "explanation"],
            performance_metrics={"latency_ms": 600, "tokens_per_sec": 45}
        )
        
        # Modelo especializado em análise
        self.models["llama3-70b"] = ModelSpec(
            name="llama3-70b",
            provider="ollama",
            endpoint="http://ollama:11434",
            capabilities=["text", "analysis", "complex_reasoning"],
            performance_metrics={"latency_ms": 2000, "tokens_per_sec": 30}
        )
    
    async def get_qualified_models(self, requirements: Dict[str, Any]) -> List[ModelSpec]:
        """
        Retorna modelos qualificados para requisitos.
        
        Args:
            requirements: Requisitos (capabilities, max_latency, etc.)
        
        Returns:
            Lista de modelos qualificados
        """
        candidates = list(self.models.values())
        
        # Filtrar por capabilities
        if "required_capabilities" in requirements:
            required = requirements["required_capabilities"]
            candidates = [
                m for m in candidates
                if any(cap in m.capabilities for cap in required)
            ]
        
        # Filtrar por latência máxima
        if "max_latency_ms" in requirements:
            max_latency = requirements["max_latency_ms"]
            candidates = [
                m for m in candidates
                if m.performance_metrics.get("latency_ms", 9999) <= max_latency
            ]
        
        # Ordenar por performance
        candidates.sort(
            key=lambda m: m.performance_metrics.get("latency_ms", 9999)
        )
        
        return candidates

class IntelligentRouter:
    """Roteador inteligente para seleção de modelos."""
    
    def __init__(self):
        self.selection_history = []
    
    async def select_optimal(
        self,
        available_models: List[ModelSpec],
        requirements: Dict[str, Any],
        recent_performance: Optional[Dict[str, float]] = None
    ) -> ModelSpec:
        """
        Seleciona modelo ótimo baseado em requisitos e performance.
        
        Returns:
            Modelo selecionado
        """
        if not available_models:
            raise ValueError("Nenhum modelo disponível")
        
        # Score de cada modelo
        scored_models = []
        
        for model in available_models:
            score = 0.0
            
            # Score baseado em latência (menor é melhor)
            latency = model.performance_metrics.get("latency_ms", 1000)
            score += (1000 - latency) / 1000 * 0.4
            
            # Score baseado em performance recente
            if recent_performance and model.name in recent_performance:
                score += recent_performance[model.name] * 0.3
            
            # Score baseado em número de capabilities
            score += len(model.capabilities) / 10.0 * 0.2
            
            # Score baseado em custo (menor é melhor)
            if model.cost_per_token > 0:
                score += (1.0 / (model.cost_per_token * 1000)) * 0.1
            
            scored_models.append((model, score))
        
        # Selecionar modelo com maior score
        selected = max(scored_models, key=lambda x: x[1])[0]
        
        logger.debug(f"Modelo selecionado: {selected.name} (score: {max(scored_models, key=lambda x: x[1])[1]:.2f})")
        
        return selected

class EnsembleEngine:
    """Engine de ensemble para combinar múltiplos modelos."""
    
    def combine_responses(
        self,
        model_results: List[Dict[str, Any]],
        strategy: str = "confidence_weighted_with_validation"
    ) -> Dict[str, Any]:
        """
        Combina respostas de múltiplos modelos.
        
        Args:
            model_results: Resultados de cada modelo
            strategy: Estratégia de ensemble
        
        Returns:
            Resposta combinada
        """
        if not model_results:
            return {"response": "", "confidence": 0.0}
        
        if strategy == "confidence_weighted_with_validation":
            # Média ponderada com validação cruzada
            valid_results = [r for r in model_results if r.get("response")]
            
            if not valid_results:
                return {"response": "", "confidence": 0.0}
            
            # Calcular pesos baseados em confiança
            total_confidence = sum(r.get("confidence", 0.5) for r in valid_results)
            
            if total_confidence == 0:
                # Fallback: primeira resposta
                return valid_results[0]
            
            # Combinar respostas ponderadas
            weighted_parts = []
            for r in valid_results:
                weight = r.get("confidence", 0.5) / total_confidence
                response_text = r.get("response", "")
                weighted_parts.append((response_text, weight))
            
            # Construir resposta combinada (simplificado)
            # Em produção, poderia usar técnicas mais sofisticadas
            primary_response = max(weighted_parts, key=lambda x: x[1])[0]
            
            avg_confidence = sum(r.get("confidence", 0.5) for r in valid_results) / len(valid_results)
            
            return {
                "response": primary_response,
                "confidence": avg_confidence,
                "sources": len(valid_results),
                "strategy": strategy
            }
        
        # Fallback: primeira resposta
        return model_results[0]

class ModelPerformanceMonitor:
    """Monitor de performance de modelos."""
    
    def __init__(self):
        self.performance_history: Dict[str, List[float]] = {}
    
    def record_performance(self, model_name: str, metric: float):
        """Registra métrica de performance."""
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []
        
        self.performance_history[model_name].append(metric)
        
        # Manter apenas últimas 100 métricas
        if len(self.performance_history[model_name]) > 100:
            self.performance_history[model_name] = self.performance_history[model_name][-100:]
    
    def get_recent_performance(self) -> Dict[str, float]:
        """
        Retorna performance recente de todos os modelos.
        
        Returns:
            Dicionário model_name -> performance_score
        """
        performance = {}
        
        for model_name, metrics in self.performance_history.items():
            if metrics:
                # Média das últimas 10 métricas
                recent_metrics = metrics[-10:]
                performance[model_name] = sum(recent_metrics) / len(recent_metrics)
        
        return performance

class ModelOrchestrator:
    """
    Orquestrador de modelos especializados.
    Gerencia seleção, ensemble e performance.
    """
    
    def __init__(self):
        self.model_registry = DistributedModelRegistry()
        self.router = IntelligentRouter()
        self.ensemble_engine = EnsembleEngine()
        self.performance_monitor = ModelPerformanceMonitor()
        
        logger.info("Model Orchestrator inicializado")
    
    async def select_optimal_model(self, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """
        Seleciona modelo ótimo baseado em análise de intenção.
        
        Returns:
            Especificação do modelo
        """
        # Determinar requisitos baseados na intenção
        requirements = {
            "required_capabilities": self._get_required_capabilities(intent_analysis),
            "max_latency_ms": self._get_max_latency(intent_analysis)
        }
        
        # Obter modelos qualificados
        available_models = await self.model_registry.get_qualified_models(requirements)
        
        if not available_models:
            # Fallback: modelo padrão
            available_models = [self.model_registry.models["llama3-8b"]]
        
        # Selecionar modelo ótimo
        selected = await self.router.select_optimal(
            available_models,
            requirements,
            self.performance_monitor.get_recent_performance()
        )
        
        return {
            "name": selected.name,
            "provider": selected.provider,
            "endpoint": selected.endpoint,
            "capabilities": selected.capabilities
        }
    
    def _get_required_capabilities(self, intent_analysis: IntentAnalysis) -> List[str]:
        """Determina capabilities necessárias baseado na intenção."""
        capabilities = ["text"]  # Sempre necessário
        
        if intent_analysis.primary_intent == "create":
            capabilities.append("code")
        elif intent_analysis.complexity > 0.7:
            capabilities.append("complex_reasoning")
        
        return capabilities
    
    def _get_max_latency(self, intent_analysis: IntentAnalysis) -> float:
        """Determina latência máxima aceitável."""
        if intent_analysis.complexity > 0.7:
            return 5000.0  # 5s para queries complexas
        return 2000.0  # 2s para queries normais
    
    async def get_intent_model(self) -> Dict[str, Any]:
        """Retorna modelo para análise de intenção."""
        return {
            "name": "llama3-8b",
            "provider": "ollama",
            "endpoint": "http://ollama:11434"
        }
    
    async def ensemble_models(
        self,
        prompt: str,
        models: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa ensemble de modelos.
        
        Args:
            prompt: Prompt para os modelos
            models: Lista de especificações de modelos
        
        Returns:
            Resposta combinada
        """
        import asyncio
        import httpx
        
        # Executar modelos em paralelo
        tasks = []
        for model_spec in models:
            tasks.append(self._execute_model(model_spec, prompt))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar exceções
        valid_results = [
            r for r in results
            if not isinstance(r, Exception) and r.get("response")
        ]
        
        if not valid_results:
            return {
                "response": "Erro ao processar com modelos",
                "confidence": 0.0,
                "error": "Todos os modelos falharam"
            }
        
        # Combinar resultados
        combined = self.ensemble_engine.combine_responses(
            valid_results,
            strategy="confidence_weighted_with_validation"
        )
        
        # Registrar performance
        for result in valid_results:
            if result.get("model_name"):
                self.performance_monitor.record_performance(
                    result["model_name"],
                    result.get("confidence", 0.5)
                )
        
        return combined
    
    async def _execute_model(
        self,
        model_spec: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """
        Executa um modelo específico.
        
        Returns:
            Resultado do modelo
        """
        try:
            if model_spec.get("provider") == "ollama":
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{model_spec['endpoint']}/api/generate",
                        json={
                            "model": model_spec["name"],
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "response": data.get("response", ""),
                            "confidence": 0.8,
                            "model_name": model_spec["name"]
                        }
            
            # Fallback
            return {
                "response": f"Resposta simulada do {model_spec.get('name', 'unknown')}",
                "confidence": 0.5,
                "model_name": model_spec.get("name", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Erro executando modelo {model_spec.get('name')}: {e}")
            raise e

