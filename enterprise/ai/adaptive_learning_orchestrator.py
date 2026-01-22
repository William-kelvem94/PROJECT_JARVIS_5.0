"""
Adaptive Learning Orchestrator - Orquestrador de Aprendizado Adaptativo
Identifica oportunidades de melhoria e aplica estratégias específicas
"""

from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from core.logger import logger

class LearningStrategy(Enum):
    """Estratégias de aprendizado disponíveis."""
    FINE_TUNING = "fine_tuning"
    PROMPT_ENGINEERING = "prompt_engineering"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    ARCHITECTURE_ADAPTATION = "architecture_adaptation"

@dataclass
class LearningOpportunity:
    """Oportunidade de aprendizado identificada."""
    pattern: str
    confidence_boost: float
    strategy: LearningStrategy
    priority: int
    expected_impact: float
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BehavioralPatternMiner:
    """Minera padrões comportamentais nas interações."""
    
    async def extract_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """
        Extrai padrões comportamentais das interações.
        
        Returns:
            Lista de padrões identificados
        """
        patterns = []
        
        # Agrupar interações por tipo
        interaction_types = {}
        for interaction in interactions:
            intent = interaction.get('intent', interaction.get('primary_intent', 'unknown'))
            if intent not in interaction_types:
                interaction_types[intent] = []
            interaction_types[intent].append(interaction)
        
        # Analisar padrões para cada tipo
        for intent, group in interaction_types.items():
            if len(group) >= 3:  # Mínimo para padrão
                pattern = await self._analyze_intent_pattern(group)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    async def _analyze_intent_pattern(self, interactions: List[Dict]) -> Optional[Dict]:
        """Analisa padrão para um tipo de intenção."""
        if len(interactions) < 3:
            return None
        
        # Análise temporal
        timestamps = [i.get('timestamp', 0) for i in interactions if i.get('timestamp')]
        time_pattern = await self._analyze_temporal_pattern(timestamps) if timestamps else {}
        
        # Análise de contexto
        contexts = [i.get('context', {}) for i in interactions]
        context_pattern = await self._analyze_context_pattern(contexts)
        
        # Calcular confiança do padrão
        confidence = await self._calculate_pattern_confidence(interactions)
        
        return {
            'intent': interactions[0].get('intent', 'unknown'),
            'frequency': len(interactions),
            'temporal_pattern': time_pattern,
            'context_pattern': context_pattern,
            'confidence': confidence,
            'avg_quality': sum(
                i.get('quality_metrics', {}).get('relevance', 0.5)
                for i in interactions
            ) / len(interactions) if interactions else 0.0
        }
    
    async def _analyze_temporal_pattern(self, timestamps: List[float]) -> Dict:
        """Analisa padrão temporal."""
        if len(timestamps) < 2:
            return {"type": "sparse"}
        
        # Calcular intervalo médio
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        return {
            "type": "periodic" if avg_interval > 0 else "random",
            "avg_interval": avg_interval,
            "count": len(timestamps)
        }
    
    async def _analyze_context_pattern(self, contexts: List[Dict]) -> Dict:
        """Analisa padrão de contexto."""
        # Extrair entidades comuns
        all_entities = []
        for ctx in contexts:
            if isinstance(ctx, dict):
                entities = ctx.get('entities', [])
                if isinstance(entities, list):
                    all_entities.extend(entities)
        
        # Contar frequência
        entity_counts = {}
        for entity in all_entities:
            entity_str = str(entity)
            entity_counts[entity_str] = entity_counts.get(entity_str, 0) + 1
        
        # Entidades mais frequentes
        common_entities = sorted(
            entity_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "common_entities": [e[0] for e in common_entities],
            "entity_diversity": len(entity_counts)
        }
    
    async def _calculate_pattern_confidence(self, interactions: List[Dict]) -> float:
        """Calcula confiança do padrão."""
        if not interactions:
            return 0.0
        
        # Baseado em frequência e consistência
        frequency_score = min(1.0, len(interactions) / 10.0)
        
        # Consistência de qualidade
        qualities = [
            i.get('quality_metrics', {}).get('relevance', 0.5)
            for i in interactions
        ]
        consistency_score = 1.0 - (max(qualities) - min(qualities)) if qualities else 0.5
        
        return (frequency_score + consistency_score) / 2.0

class LearningImpactPredictor:
    """Prediz impacto de oportunidades de aprendizado."""
    
    async def predict_impact(self, gap: Dict) -> Dict:
        """
        Prediz impacto de preencher um gap de conhecimento.
        
        Returns:
            Predição de impacto
        """
        pattern = gap.get('pattern', {})
        
        # Calcular boost de confiança esperado
        confidence_boost = pattern.get('confidence', 0.0) * 0.2  # Boost proporcional
        
        # Calcular melhoria esperada
        expected_improvement = pattern.get('avg_quality', 0.5) * 0.3
        
        # Prioridade baseada em frequência e impacto
        frequency = pattern.get('frequency', 0)
        priority = min(10, int(frequency / 2) + int(expected_improvement * 10))
        
        return {
            'confidence_boost': confidence_boost,
            'expected_improvement': expected_improvement,
            'priority': priority,
            'estimated_effort': 5  # Horas estimadas
        }

class LearningStrategySelector:
    """Seleciona estratégia de aprendizado apropriada."""
    
    async def select_strategy(
        self,
        gap: Dict,
        impact_prediction: Dict
    ) -> LearningStrategy:
        """
        Seleciona estratégia baseada no gap e impacto.
        
        Returns:
            Estratégia selecionada
        """
        priority = impact_prediction.get('priority', 0)
        expected_impact = impact_prediction.get('expected_improvement', 0.0)
        
        # Estratégia baseada em prioridade e impacto
        if priority >= 8 and expected_impact > 0.3:
            return LearningStrategy.FINE_TUNING
        elif priority >= 6:
            return LearningStrategy.KNOWLEDGE_EXPANSION
        elif priority >= 4:
            return LearningStrategy.PROMPT_ENGINEERING
        else:
            return LearningStrategy.ARCHITECTURE_ADAPTATION

class LearningExecutionPlanner:
    """Planeja execução de estratégias de aprendizado."""
    
    async def plan_execution(
        self,
        opportunity: LearningOpportunity
    ) -> Dict[str, Any]:
        """
        Cria plano de execução para oportunidade.
        
        Returns:
            Plano de execução
        """
        return {
            'strategy': opportunity.strategy.value,
            'steps': self._get_strategy_steps(opportunity.strategy),
            'estimated_duration': self._estimate_duration(opportunity),
            'resources_required': self._get_required_resources(opportunity.strategy)
        }
    
    def _get_strategy_steps(self, strategy: LearningStrategy) -> List[str]:
        """Retorna passos para estratégia."""
        steps_map = {
            LearningStrategy.FINE_TUNING: [
                "Coletar dados de treinamento",
                "Preparar dataset",
                "Executar fine-tuning",
                "Validar modelo",
                "Deploy modelo"
            ],
            LearningStrategy.PROMPT_ENGINEERING: [
                "Analisar prompts existentes",
                "Projetar novos prompts",
                "Testar prompts",
                "Implementar melhorias"
            ],
            LearningStrategy.KNOWLEDGE_EXPANSION: [
                "Identificar conhecimento faltante",
                "Coletar novas informações",
                "Integrar no knowledge graph",
                "Validar integração"
            ],
            LearningStrategy.ARCHITECTURE_ADAPTATION: [
                "Analisar arquitetura atual",
                "Identificar melhorias",
                "Planejar mudanças",
                "Implementar adaptações"
            ]
        }
        return steps_map.get(strategy, [])
    
    def _estimate_duration(self, opportunity: LearningOpportunity) -> int:
        """Estima duração em horas."""
        duration_map = {
            LearningStrategy.FINE_TUNING: 8,
            LearningStrategy.PROMPT_ENGINEERING: 2,
            LearningStrategy.KNOWLEDGE_EXPANSION: 4,
            LearningStrategy.ARCHITECTURE_ADAPTATION: 12
        }
        return duration_map.get(opportunity.strategy, 6)
    
    def _get_required_resources(self, strategy: LearningStrategy) -> List[str]:
        """Retorna recursos necessários."""
        return {
            LearningStrategy.FINE_TUNING: ["GPU", "Training Data", "Compute"],
            LearningStrategy.PROMPT_ENGINEERING: ["Analyst", "Test Cases"],
            LearningStrategy.KNOWLEDGE_EXPANSION: ["Knowledge Sources", "Graph DB"],
            LearningStrategy.ARCHITECTURE_ADAPTATION: ["Architect", "Development Time"]
        }.get(strategy, [])

class AdaptiveLearningOrchestrator:
    """
    Sistema de aprendizado adaptativo.
    Identifica oportunidades e aplica estratégias específicas.
    """
    
    def __init__(self):
        self.pattern_miner = BehavioralPatternMiner()
        self.impact_predictor = LearningImpactPredictor()
        self.strategy_selector = LearningStrategySelector()
        self.execution_planner = LearningExecutionPlanner()
        
        self.executed_learnings = []
        
        logger.info("Adaptive Learning Orchestrator inicializado")
    
    async def analyze_learning_opportunities(
        self,
        interactions: List[Dict],
        performance_metrics: Dict
    ) -> List[LearningOpportunity]:
        """
        Analisa interações para identificar oportunidades de aprendizado.
        
        Returns:
            Lista de oportunidades ordenadas por prioridade
        """
        opportunities = []
        
        try:
            # 1. Mineração de padrões comportamentais
            behavioral_patterns = await self.pattern_miner.extract_patterns(interactions)
            logger.debug(f"Padrões extraídos: {len(behavioral_patterns)}")
            
            # 2. Identificação de gaps de conhecimento
            knowledge_gaps = await self._identify_knowledge_gaps(
                behavioral_patterns,
                performance_metrics
            )
            logger.debug(f"Gaps identificados: {len(knowledge_gaps)}")
            
            # 3. Predição de impacto para cada oportunidade
            for gap in knowledge_gaps:
                impact_prediction = await self.impact_predictor.predict_impact(gap)
                strategy = await self.strategy_selector.select_strategy(
                    gap,
                    impact_prediction
                )
                
                opportunity = LearningOpportunity(
                    pattern=gap.get('pattern_description', gap.get('intent', 'unknown')),
                    confidence_boost=impact_prediction['confidence_boost'],
                    strategy=strategy,
                    priority=impact_prediction['priority'],
                    expected_impact=impact_prediction['expected_improvement'],
                    metadata={
                        'gap': gap,
                        'impact': impact_prediction
                    }
                )
                
                opportunities.append(opportunity)
                logger.info(
                    f"Oportunidade identificada: {opportunity.pattern} "
                    f"(prioridade: {opportunity.priority})"
                )
        
        except Exception as e:
            logger.error(f"Erro analisando oportunidades: {e}")
        
        # Ordenar por prioridade
        return sorted(opportunities, key=lambda x: x.priority, reverse=True)
    
    async def _identify_knowledge_gaps(
        self,
        behavioral_patterns: List[Dict],
        performance_metrics: Dict
    ) -> List[Dict]:
        """Identifica gaps de conhecimento."""
        gaps = []
        
        for pattern in behavioral_patterns:
            avg_quality = pattern.get('avg_quality', 0.5)
            frequency = pattern.get('frequency', 0)
            
            # Gap identificado se qualidade baixa ou frequência alta com qualidade mediana
            if avg_quality < 0.6 or (frequency > 5 and avg_quality < 0.7):
                gaps.append({
                    'pattern': pattern,
                    'pattern_description': pattern.get('intent', 'unknown'),
                    'quality_gap': 0.8 - avg_quality,  # Gap até qualidade desejada
                    'frequency': frequency
                })
        
        return gaps
    
    async def execute_learning_cycle(
        self,
        opportunities: List[LearningOpportunity]
    ) -> List[Dict]:
        """
        Executa ciclo de aprendizado baseado nas oportunidades.
        
        Args:
            opportunities: Lista de oportunidades ordenadas
        
        Returns:
            Resultados da execução
        """
        executed_learnings = []
        
        # Processar top 3 prioridades
        top_opportunities = opportunities[:3]
        
        for opportunity in top_opportunities:
            try:
                logger.info(f"Executando estratégia: {opportunity.strategy.value}")
                
                # Planejar execução
                execution_plan = await self.execution_planner.plan_execution(opportunity)
                
                # Executar estratégia
                learning_result = await self._execute_learning_strategy(
                    opportunity,
                    execution_plan
                )
                
                executed_learnings.append({
                    'opportunity': {
                        'pattern': opportunity.pattern,
                        'strategy': opportunity.strategy.value,
                        'priority': opportunity.priority
                    },
                    'result': learning_result,
                    'execution_plan': execution_plan,
                    'timestamp': datetime.now()
                })
                
                logger.info(f"Estratégia {opportunity.strategy.value} executada com sucesso")
                
                # Avaliação pós-aprendizado (assíncrono)
                asyncio.create_task(
                    self._evaluate_learning_effectiveness(learning_result)
                )
                
            except Exception as e:
                logger.error(f"Erro executando estratégia {opportunity.strategy.value}: {e}")
                executed_learnings.append({
                    'opportunity': {
                        'pattern': opportunity.pattern,
                        'strategy': opportunity.strategy.value
                    },
                    'result': {'success': False, 'error': str(e)},
                    'timestamp': datetime.now()
                })
        
        self.executed_learnings.extend(executed_learnings)
        return executed_learnings
    
    async def _execute_learning_strategy(
        self,
        opportunity: LearningOpportunity,
        execution_plan: Dict
    ) -> Dict:
        """
        Executa estratégia de aprendizado específica.
        
        Returns:
            Resultado da execução
        """
        strategy = opportunity.strategy
        
        if strategy == LearningStrategy.FINE_TUNING:
            return await self._execute_fine_tuning(opportunity)
        elif strategy == LearningStrategy.PROMPT_ENGINEERING:
            return await self._execute_prompt_engineering(opportunity)
        elif strategy == LearningStrategy.KNOWLEDGE_EXPANSION:
            return await self._execute_knowledge_expansion(opportunity)
        elif strategy == LearningStrategy.ARCHITECTURE_ADAPTATION:
            return await self._execute_architecture_adaptation(opportunity)
        
        return {'success': False, 'error': 'Estratégia não implementada'}
    
    async def _execute_fine_tuning(self, opportunity: LearningOpportunity) -> Dict:
        """Executa fine-tuning."""
        logger.info("Executando fine-tuning...")
        # TODO: Integrar com DistributedTrainingPipeline
        return {
            'success': True,
            'method': 'fine_tuning',
            'status': 'scheduled',
            'estimated_completion': '2 hours'
        }
    
    async def _execute_prompt_engineering(self, opportunity: LearningOpportunity) -> Dict:
        """Executa prompt engineering."""
        logger.info("Executando prompt engineering...")
        # Por enquanto simular
        return {
            'success': True,
            'method': 'prompt_engineering',
            'prompts_optimized': 5,
            'improvement_expected': opportunity.expected_impact
        }
    
    async def _execute_knowledge_expansion(self, opportunity: LearningOpportunity) -> Dict:
        """Executa expansão de conhecimento."""
        logger.info("Executando expansão de conhecimento...")
        # TODO: Integrar com Knowledge Graph
        return {
            'success': True,
            'method': 'knowledge_expansion',
            'knowledge_items_added': 10
        }
    
    async def _execute_architecture_adaptation(self, opportunity: LearningOpportunity) -> Dict:
        """Executa adaptação de arquitetura."""
        logger.info("Executando adaptação de arquitetura...")
        return {
            'success': True,
            'method': 'architecture_adaptation',
            'status': 'planned',
            'requires_approval': True
        }
    
    async def _evaluate_learning_effectiveness(self, learning_result: Dict):
        """Avalia efetividade do aprendizado (assíncrono)."""
        # Por enquanto apenas log
        logger.info(f"Avaliando efetividade: {learning_result.get('method', 'unknown')}")
        # TODO: Comparar métricas antes e depois

