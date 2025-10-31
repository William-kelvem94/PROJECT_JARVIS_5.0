"""
Cognitive Pipeline Orchestrator - Orquestrador do Pipeline Cognitivo
Gerencia todo o fluxo desde input até aprendizado
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
from core.logger import logger
from enterprise.ai.cognitive_engine import CognitiveEngine, CognitiveQuery, CognitiveResponse
from enterprise.ai.adaptive_learning_orchestrator import AdaptiveLearningOrchestrator
from enterprise.ai.multi_model_ensemble import MultiModelEnsembleEngine
from enterprise.ai.cognitive_performance_monitor import CognitivePerformanceMonitor
from enterprise.ai.knowledge_distillation import KnowledgeDistillationSystem

class CognitivePipelineOrchestrator:
    """
    Orquestrador do pipeline cognitivo completo.
    Gerencia todo o fluxo desde input até aprendizado.
    """
    
    def __init__(
        self,
        cognitive_engine: Optional[CognitiveEngine] = None,
        learning_orchestrator: Optional[AdaptiveLearningOrchestrator] = None,
        ensemble_engine: Optional[MultiModelEnsembleEngine] = None,
        performance_monitor: Optional[CognitivePerformanceMonitor] = None,
        knowledge_distiller: Optional[KnowledgeDistillationSystem] = None
    ):
        """
        Inicializa orquestrador.
        
        Args:
            cognitive_engine: Engine cognitivo
            learning_orchestrator: Orquestrador de aprendizado
            ensemble_engine: Engine de ensemble
            performance_monitor: Monitor de performance
            knowledge_distiller: Sistema de destilação
        """
        self.cognitive_engine = cognitive_engine or CognitiveEngine()
        self.learning_orchestrator = learning_orchestrator or AdaptiveLearningOrchestrator()
        self.ensemble_engine = ensemble_engine or MultiModelEnsembleEngine()
        self.performance_monitor = performance_monitor or CognitivePerformanceMonitor()
        self.knowledge_distiller = knowledge_distiller or KnowledgeDistillationSystem()
        
        # Stages do pipeline
        self.pipeline_stages = {
            'input_processing': self._process_input,
            'intent_analysis': self._analyze_intent,
            'context_retrieval': self._retrieve_context,
            'model_orchestration': self._orchestrate_models,
            'response_generation': self._generate_response,
            'learning_cycle': self._execute_learning_cycle
        }
        
        self.interaction_history = []
        
        logger.info("Cognitive Pipeline Orchestrator inicializado")
    
    async def execute_cognitive_pipeline(self, user_input: Dict) -> Dict[str, Any]:
        """
        Executa o pipeline cognitivo completo.
        
        Args:
            user_input: Input do usuário
        
        Returns:
            Resultado completo do pipeline
        """
        pipeline_context = {
            'user_input': user_input,
            'start_time': asyncio.get_event_loop().time(),
            'stage_metrics': {},
            'learning_opportunities': [],
            'pipeline_abort': False
        }
        
        try:
            logger.info("Iniciando pipeline cognitivo")
            
            # Executar estágios do pipeline
            for stage_name, stage_method in self.pipeline_stages.items():
                stage_start = asyncio.get_event_loop().time()
                
                try:
                    pipeline_context = await stage_method(pipeline_context)
                    
                    stage_duration = asyncio.get_event_loop().time() - stage_start
                    pipeline_context['stage_metrics'][stage_name] = stage_duration
                    
                    logger.debug(f"Stage {stage_name} concluído em {stage_duration:.2f}s")
                    
                    # Verificar se deve abortar
                    if pipeline_context.get('pipeline_abort', False):
                        logger.warning("Pipeline abortado")
                        break
                        
                except Exception as e:
                    logger.error(f"Erro no stage {stage_name}: {e}")
                    pipeline_context['stage_errors'] = pipeline_context.get('stage_errors', [])
                    pipeline_context['stage_errors'].append({
                        'stage': stage_name,
                        'error': str(e)
                    })
                    # Continuar pipeline apesar do erro
            
            # Métricas finais
            total_time = asyncio.get_event_loop().time() - pipeline_context['start_time']
            pipeline_context['total_processing_time'] = total_time
            pipeline_context['timestamp'] = datetime.now()
            
            # Monitorar performance
            await self.performance_monitor.track_cognitive_metrics(pipeline_context)
            
            # Armazenar interação
            self.interaction_history.append(pipeline_context)
            if len(self.interaction_history) > 1000:
                self.interaction_history = self.interaction_history[-1000:]
            
            logger.info(f"Pipeline concluído em {total_time:.2f}s")
            
            return pipeline_context
            
        except Exception as e:
            logger.error(f"Erro crítico no pipeline: {e}")
            pipeline_context['pipeline_error'] = str(e)
            return pipeline_context
    
    async def _process_input(self, context: Dict) -> Dict:
        """Processa input do usuário."""
        user_input = context.get('user_input', {})
        
        # Criar CognitiveQuery
        query = CognitiveQuery(
            id=f"query_{datetime.now().timestamp()}",
            text=user_input.get('text', user_input.get('message', '')),
            user_id=user_input.get('user_id'),
            session_id=user_input.get('session_id'),
            context=user_input.get('context')
        )
        
        context['query'] = query
        return context
    
    async def _analyze_intent(self, context: Dict) -> Dict:
        """Analisa intenção (já feito no cognitive_engine)."""
        # Pass-through, análise será feita no engine
        return context
    
    async def _retrieve_context(self, context: Dict) -> Dict:
        """Recupera contexto (já feito no cognitive_engine)."""
        # Pass-through, contexto será recuperado no engine
        return context
    
    async def _orchestrate_models(self, context: Dict) -> Dict:
        """Orquestra modelos (já feito no cognitive_engine)."""
        # Pass-through
        return context
    
    async def _generate_response(self, context: Dict) -> Dict:
        """Gera resposta usando cognitive engine."""
        query = context.get('query')
        
        if not query:
            context['pipeline_abort'] = True
            context['error'] = 'Query não encontrada'
            return context
        
        # Processar query
        response_start = asyncio.get_event_loop().time()
        
        response = await self.cognitive_engine.process_query(query)
        
        response_time = asyncio.get_event_loop().time() - response_start
        
        context['response'] = response
        context['response_time'] = response_time
        context['confidence'] = response.confidence
        
        # Adicionar métricas de qualidade
        context['quality_metrics'] = response.quality_metrics
        context['context_used'] = response.context_used
        
        return context
    
    async def _execute_learning_cycle(self, context: Dict) -> Dict:
        """Executa ciclo de aprendizado se necessário."""
        try:
            # Obter interações recentes
            recent_interactions = self.interaction_history[-100:] if len(self.interaction_history) >= 100 else self.interaction_history
            
            if not recent_interactions or len(recent_interactions) < 10:
                # Insuficiente para análise
                context['learning_opportunities'] = []
                return context
            
            # Preparar dados para análise
            interactions_data = []
            for inter in recent_interactions:
                interactions_data.append({
                    'intent': inter.get('response', {}).get('metadata', {}).get('intent', 'unknown'),
                    'query': inter.get('query', {}).text if hasattr(inter.get('query', {}), 'text') else '',
                    'quality_metrics': inter.get('quality_metrics', {}),
                    'timestamp': inter.get('timestamp', datetime.now())
                })
            
            # Obter métricas de performance
            performance_data = self.performance_monitor.get_performance_summary()
            
            # Analisar oportunidades de aprendizado
            opportunities = await self.learning_orchestrator.analyze_learning_opportunities(
                interactions_data,
                performance_data
            )
            
            context['learning_opportunities'] = [
                {
                    'pattern': opp.pattern,
                    'priority': opp.priority,
                    'strategy': opp.strategy.value,
                    'expected_impact': opp.expected_impact
                }
                for opp in opportunities
            ]
            
            # Executar se alta prioridade
            if opportunities and opportunities[0].priority > 7:
                logger.info(f"Executando ciclo de aprendizado: {len(opportunities[:2])} oportunidades")
                
                learning_results = await self.learning_orchestrator.execute_learning_cycle(
                    opportunities[:2]  # Top 2
                )
                
                context['learning_results'] = learning_results
                logger.info(f"Ciclo de aprendizado concluído: {len(learning_results)} estratégias executadas")
            
        except Exception as e:
            logger.error(f"Erro no ciclo de aprendizado: {e}")
            context['learning_error'] = str(e)
        
        return context
    
    async def _get_recent_interactions(self, limit: int = 100) -> List[Dict]:
        """Obtém interações recentes."""
        return self.interaction_history[-limit:]
    
    async def _get_performance_data(self) -> Dict:
        """Obtém dados de performance."""
        return self.performance_monitor.get_performance_summary()
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do pipeline."""
        if not self.interaction_history:
            return {
                'total_interactions': 0,
                'avg_processing_time': 0.0
            }
        
        processing_times = [
            inter.get('total_processing_time', 0)
            for inter in self.interaction_history
            if inter.get('total_processing_time')
        ]
        
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        return {
            'total_interactions': len(self.interaction_history),
            'avg_processing_time': avg_time,
            'recent_performance': self.performance_monitor.get_performance_summary()
        }

