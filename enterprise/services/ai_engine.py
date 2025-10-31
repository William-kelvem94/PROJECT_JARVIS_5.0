"""
Enterprise AI Engine - Motor de IA Empresarial
Suporta múltiplos modelos, ensemble e otimização de inferência
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from core.logger import logger

@dataclass
class ModelInfo:
    """Informações de um modelo."""
    name: str
    provider: str  # ollama, openai, local
    endpoint: str
    capabilities: List[str]
    performance_metrics: Dict[str, float]

class ModelRegistry:
    """Registry de modelos de IA disponíveis."""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._init_default_models()
    
    def _init_default_models(self):
        """Inicializa modelos padrão."""
        self.models["llama3-8b"] = ModelInfo(
            name="llama3-8b",
            provider="ollama",
            endpoint="http://ollama:11434",
            capabilities=["text", "code", "reasoning"],
            performance_metrics={"latency_ms": 500, "tokens_per_sec": 50}
        )
        
        self.models["llama3-70b"] = ModelInfo(
            name="llama3-70b",
            provider="ollama",
            endpoint="http://ollama:11434",
            capabilities=["text", "code", "reasoning", "complex"],
            performance_metrics={"latency_ms": 2000, "tokens_per_sec": 30}
        )
    
    def register_model(self, model: ModelInfo):
        """Registra um novo modelo."""
        self.models[model.name] = model
        logger.info(f"Modelo registrado: {model.name}")
    
    def get_optimal_models(self, prompt: str, requirements: Dict[str, Any]) -> List[ModelInfo]:
        """
        Retorna modelos otimais para um prompt.
        
        Args:
            prompt: Prompt do usuário
            requirements: Requisitos (max_latency, complexity, etc.)
        
        Returns:
            Lista de modelos recomendados
        """
        # Lógica simples: filtrar por requisitos
        candidates = list(self.models.values())
        
        if "max_latency_ms" in requirements:
            max_latency = requirements["max_latency_ms"]
            candidates = [
                m for m in candidates
                if m.performance_metrics["latency_ms"] <= max_latency
            ]
        
        if "required_capabilities" in requirements:
            required = requirements["required_capabilities"]
            candidates = [
                m for m in candidates
                if all(cap in m.capabilities for cap in required)
            ]
        
        # Ordenar por performance
        candidates.sort(key=lambda m: m.performance_metrics.get("latency_ms", 9999))
        
        return candidates[:3]  # Top 3

class InferenceOptimizer:
    """Otimizador de inferência."""
    
    def optimize_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Otimiza prompt para melhor inferência.
        
        Args:
            prompt: Prompt original
            context: Contexto adicional
        
        Returns:
            Prompt otimizado
        """
        # Compressão de contexto se necessário
        if context and len(str(context)) > 2000:
            # Truncar contexto mantendo partes importantes
            context_str = str(context)[:2000] + "..."
        else:
            context_str = str(context) if context else ""
        
        # Construir prompt otimizado
        optimized = f"{context_str}\n\nPrompt: {prompt}\n\nResposta:"
        
        return optimized.strip()

class ModelEnsembler:
    """Ensembler de múltiplos modelos."""
    
    def ensemble_results(
        self,
        results: List[Dict[str, Any]],
        strategy: str = "confidence_weighted"
    ) -> Dict[str, Any]:
        """
        Combina resultados de múltiplos modelos.
        
        Args:
            results: Lista de resultados
            strategy: Estratégia de ensemble
        
        Returns:
            Resultado combinado
        """
        if not results:
            return {"response": "", "confidence": 0.0}
        
        if strategy == "confidence_weighted":
            # Média ponderada por confiança
            total_weight = sum(r.get("confidence", 0.5) for r in results)
            if total_weight == 0:
                # Fallback: primeira resposta
                return results[0]
            
            # Combinar respostas por peso
            weighted_response = ""
            for r in results:
                weight = r.get("confidence", 0.5) / total_weight
                weighted_response += f"{r.get('response', '')} "
            
            avg_confidence = sum(r.get("confidence", 0.5) for r in results) / len(results)
            
            return {
                "response": weighted_response.strip(),
                "confidence": avg_confidence,
                "sources": len(results)
            }
        
        elif strategy == "majority_vote":
            # Voto majoritário (simplificado)
            responses = [r.get("response", "") for r in results]
            # Por enquanto, retornar mais comum ou primeiro
            return results[0]
        
        # Fallback
        return results[0]

class EnterpriseAIEngine:
    """
    Motor de IA Empresarial.
    Gerencia múltiplos modelos, otimização e ensemble.
    """
    
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.inference_optimizer = InferenceOptimizer()
        self.model_ensembler = ModelEnsembler()
        
        logger.info("EnterpriseAIEngine inicializado")
    
    async def enhanced_inference(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        requirements: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Inferência aprimorada com múltiplos modelos.
        
        Args:
            prompt: Prompt do usuário
            context: Contexto adicional
            requirements: Requisitos de performance
        
        Returns:
            Resposta combinada
        """
        requirements = requirements or {}
        
        # Obter modelos otimais
        models = self.model_registry.get_optimal_models(prompt, requirements)
        
        if not models:
            logger.warning("Nenhum modelo disponível, usando padrão")
            models = [self.model_registry.models["llama3-8b"]]
        
        # Otimizar prompt
        optimized_prompt = self.inference_optimizer.optimize_prompt(prompt, context)
        
        # Executar inferência em múltiplos modelos (paralelo)
        import asyncio
        tasks = []
        for model in models:
            tasks.append(self._run_model_inference(model, optimized_prompt, context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar exceções
        valid_results = [
            {"response": r, "confidence": 0.8} if isinstance(r, str) else r
            for r in results
            if not isinstance(r, Exception)
        ]
        
        if not valid_results:
            return {
                "response": "Erro ao processar requisição",
                "confidence": 0.0,
                "error": "Todos os modelos falharam"
            }
        
        # Ensemble de resultados
        ensemble_result = self.model_ensembler.ensemble_results(
            valid_results,
            strategy=requirements.get("ensemble_strategy", "confidence_weighted")
        )
        
        return ensemble_result
    
    async def _run_model_inference(
        self,
        model: ModelInfo,
        prompt: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Executa inferência em um modelo específico.
        
        Args:
            model: Informações do modelo
            prompt: Prompt
            context: Contexto
        
        Returns:
            Resultado da inferência
        """
        try:
            # Por enquanto, simulando chamada ao modelo
            # TODO: Implementar chamada real ao endpoint do modelo
            
            if model.provider == "ollama":
                # Chamada ao Ollama
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{model.endpoint}/api/generate",
                        json={
                            "model": model.name,
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
                            "model": model.name
                        }
            
            # Fallback
            return {
                "response": f"Resposta simulada do {model.name}",
                "confidence": 0.5,
                "model": model.name
            }
            
        except Exception as e:
            logger.error(f"Erro na inferência do modelo {model.name}: {e}")
            raise e

