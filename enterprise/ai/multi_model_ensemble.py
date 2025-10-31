"""
Multi-Model Ensemble Engine - Engine de Ensemble Avançado
Combina múltiplos modelos usando técnicas sofisticadas
"""

from typing import Dict, List, Any, Optional
import asyncio
from collections import defaultdict
from datetime import datetime
from core.logger import logger

class EnsemblePerformanceTracker:
    """Rastreia performance de estratégias de ensemble."""
    
    def __init__(self):
        self.performance_history: Dict[str, List[Dict]] = defaultdict(list)
    
    async def record_ensemble_performance(
        self,
        strategy: str,
        query: str,
        result: Dict[str, Any]
    ):
        """Registra performance de uma estratégia de ensemble."""
        self.performance_history[strategy].append({
            'query': query[:100],  # Truncar
            'confidence': result.get('confidence', 0.0),
            'timestamp': datetime.now(),
            'sources': result.get('sources', 0)
        })
        
        # Manter apenas últimas 1000
        if len(self.performance_history[strategy]) > 1000:
            self.performance_history[strategy] = self.performance_history[strategy][-1000:]
    
    def get_strategy_performance(self, strategy: str) -> Dict[str, Any]:
        """Retorna performance de uma estratégia."""
        history = self.performance_history.get(strategy, [])
        
        if not history:
            return {'avg_confidence': 0.0, 'count': 0}
        
        confidences = [h['confidence'] for h in history]
        return {
            'avg_confidence': sum(confidences) / len(confidences),
            'count': len(history),
            'recent_avg': sum(confidences[-10:]) / min(10, len(confidences)) if confidences else 0.0
        }

class MultiModelEnsembleEngine:
    """
    Engine de ensemble avançado.
    Combina múltiplos modelos usando técnicas sofisticadas.
    """
    
    def __init__(self):
        self.model_pool: Dict[str, Any] = {}
        self.performance_tracker = EnsemblePerformanceTracker()
        
        # Estratégias de ensemble
        self.ensemble_strategies = {
            'confidence_weighted': self._confidence_weighted_ensemble,
            'dynamic_weighting': self._dynamic_weight_ensemble,
            'meta_learning': self._meta_learning_ensemble,
            'expert_mixture': self._mixture_of_experts
        }
        
        logger.info("Multi-Model Ensemble Engine inicializado")
    
    async def ensemble_predictions(
        self,
        query: str,
        model_predictions: Dict[str, Any],
        strategy: str = 'dynamic_weighting'
    ) -> Dict[str, Any]:
        """
        Combina predições de múltiplos modelos.
        
        Args:
            query: Query original
            model_predictions: Dicionário model_name -> prediction
            strategy: Estratégia de ensemble
        
        Returns:
            Resultado combinado
        """
        if not model_predictions:
            return {'response': '', 'confidence': 0.0}
        
        # Validar estratégia
        if strategy not in self.ensemble_strategies:
            strategy = 'confidence_weighted'
            logger.warning(f"Estratégia inválida, usando: {strategy}")
        
        # Executar ensemble
        ensemble_method = self.ensemble_strategies[strategy]
        result = await ensemble_method(query, model_predictions)
        
        # Rastrear performance
        await self.performance_tracker.record_ensemble_performance(
            strategy, query, result
        )
        
        return result
    
    async def _confidence_weighted_ensemble(
        self,
        query: str,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ensemble com pesos baseados em confiança."""
        # Calcular pesos
        total_confidence = sum(
            p.get('confidence', 0.5)
            for p in predictions.values()
            if isinstance(p, dict) and p.get('response')
        )
        
        if total_confidence == 0:
            # Fallback: primeira resposta
            first_pred = next(iter(predictions.values()))
            return first_pred if isinstance(first_pred, dict) else {'response': str(first_pred), 'confidence': 0.5}
        
        # Combinar respostas ponderadas
        weighted_responses = []
        for model_name, pred in predictions.items():
            if isinstance(pred, dict) and pred.get('response'):
                weight = pred.get('confidence', 0.5) / total_confidence
                weighted_responses.append({
                    'response': pred['response'],
                    'weight': weight,
                    'model': model_name
                })
        
        # Selecionar resposta com maior peso (simplificado)
        best_response = max(weighted_responses, key=lambda x: x['weight'])
        
        # Calcular confiança média ponderada
        avg_confidence = sum(r['weight'] * predictions.get(r['model'], {}).get('confidence', 0.5) for r in weighted_responses)
        
        return {
            'response': best_response['response'],
            'confidence': avg_confidence,
            'sources': len(weighted_responses),
            'strategy': 'confidence_weighted',
            'models_used': [r['model'] for r in weighted_responses]
        }
    
    async def _dynamic_weight_ensemble(
        self,
        query: str,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ensemble com pesos dinâmicos baseados em contexto."""
        # 1. Calcular pesos contextuais
        contextual_weights = await self._calculate_contextual_weights(query, predictions)
        
        # 2. Obter pesos históricos
        historical_weights = await self._get_historical_weights(list(predictions.keys()))
        
        # 3. Combinar pesos
        final_weights = self._combine_weights(contextual_weights, historical_weights)
        
        # 4. Aplicar ensemble
        return await self._apply_weighted_ensemble(predictions, final_weights)
    
    async def _calculate_contextual_weights(
        self,
        query: str,
        predictions: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calcula pesos baseados em contexto da query."""
        weights = {}
        
        query_lower = query.lower()
        
        # Pesos baseados em características da query
        for model_name, pred in predictions.items():
            if isinstance(pred, dict) and pred.get('response'):
                # Score baseado em confiança
                confidence_score = pred.get('confidence', 0.5)
                
                # Score baseado em relevância (simplificado)
                relevance_score = 0.5  # TODO: Calcular relevância real
                
                # Combinação
                weights[model_name] = (confidence_score * 0.7 + relevance_score * 0.3)
        
        # Normalizar
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    async def _get_historical_weights(self, model_names: List[str]) -> Dict[str, float]:
        """Obtém pesos baseados em performance histórica."""
        weights = {}
        
        for model_name in model_names:
            # Usar performance tracker para obter histórico
            # Por enquanto, pesos iguais
            weights[model_name] = 1.0 / len(model_names)
        
        return weights
    
    def _combine_weights(
        self,
        contextual: Dict[str, float],
        historical: Dict[str, float]
    ) -> Dict[str, float]:
        """Combina pesos contextuais e históricos."""
        # Combinação 60% contextual, 40% histórico
        combined = {}
        
        all_models = set(contextual.keys()) | set(historical.keys())
        
        for model in all_models:
            ctx_weight = contextual.get(model, 0.0)
            hist_weight = historical.get(model, 0.0)
            combined[model] = ctx_weight * 0.6 + hist_weight * 0.4
        
        # Normalizar
        total = sum(combined.values())
        if total > 0:
            combined = {k: v / total for k, v in combined.items()}
        
        return combined
    
    async def _apply_weighted_ensemble(
        self,
        predictions: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Aplica ensemble ponderado."""
        weighted_responses = []
        
        for model_name, pred in predictions.items():
            if isinstance(pred, dict) and pred.get('response'):
                weight = weights.get(model_name, 0.0)
                weighted_responses.append({
                    'response': pred['response'],
                    'weight': weight,
                    'model': model_name
                })
        
        if not weighted_responses:
            return {'response': '', 'confidence': 0.0}
        
        # Selecionar melhor (simplificado)
        best = max(weighted_responses, key=lambda x: x['weight'])
        
        # Calcular confiança ponderada
        avg_confidence = sum(
            r['weight'] * predictions.get(r['model'], {}).get('confidence', 0.5)
            for r in weighted_responses
        )
        
        return {
            'response': best['response'],
            'confidence': avg_confidence,
            'sources': len(weighted_responses),
            'strategy': 'dynamic_weighting',
            'models_used': [r['model'] for r in weighted_responses]
        }
    
    async def _meta_learning_ensemble(
        self,
        query: str,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ensemble usando meta-learning."""
        # Por enquanto, usar dynamic weighting como fallback
        return await self._dynamic_weight_ensemble(query, predictions)
    
    async def _mixture_of_experts(
        self,
        query: str,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mixture of Experts para domínios específicos."""
        # 1. Classificar domínio da query
        domain = await self._classify_query_domain(query)
        
        # 2. Selecionar experts para o domínio
        domain_experts = await self._select_domain_experts(domain, predictions)
        
        # 3. Gate network para combinar experts (simplificado)
        expert_weights = await self._gate_network(query, domain_experts)
        
        # 4. Combinar predições dos experts
        return await self._combine_expert_predictions(domain_experts, expert_weights)
    
    async def _classify_query_domain(self, query: str) -> str:
        """Classifica domínio da query."""
        query_lower = query.lower()
        
        # Classificação simples baseada em palavras-chave
        if any(word in query_lower for word in ['código', 'programação', 'programar', 'função']):
            return 'code'
        elif any(word in query_lower for word in ['explicar', 'o que é', 'como funciona']):
            return 'explanation'
        elif any(word in query_lower for word in ['criar', 'fazer', 'gerar']):
            return 'generation'
        else:
            return 'general'
    
    async def _select_domain_experts(
        self,
        domain: str,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Seleciona experts para o domínio."""
        # Por enquanto, retornar todos os modelos
        # Em produção, filtrar por especialização do modelo
        return predictions
    
    async def _gate_network(
        self,
        query: str,
        experts: Dict[str, Any]
    ) -> Dict[str, float]:
        """Gate network para determinar pesos dos experts."""
        # Por enquanto, pesos iguais
        # Em produção, usar rede neural ou modelo de gating
        num_experts = len(experts)
        if num_experts == 0:
            return {}
        
        return {name: 1.0 / num_experts for name in experts.keys()}
    
    async def _combine_expert_predictions(
        self,
        experts: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Combina predições dos experts."""
        return await self._apply_weighted_ensemble(experts, weights)
    
    def get_ensemble_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de ensemble."""
        stats = {}
        for strategy in self.ensemble_strategies.keys():
            perf = self.performance_tracker.get_strategy_performance(strategy)
            stats[strategy] = perf
        
        return stats

