"""
Continuous Learning Loop - Aprendizado Contínuo
Registra interações e melhora o sistema continuamente
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from core.logger import logger
from enterprise.ai.cognitive_engine import CognitiveQuery, CognitiveResponse, IntentAnalysis

class FeedbackAnalyzer:
    """Analisa feedback implícito e explícito."""
    
    def __init__(self):
        self.feedback_history = []
    
    async def analyze_feedback(
        self,
        query: CognitiveQuery,
        response: CognitiveResponse,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa feedback da interação.
        
        Returns:
            Análise de feedback
        """
        # Feedback implícito (baseado em métricas)
        implicit_feedback = {
            "confidence": response.confidence,
            "response_length": len(response.response),
            "quality_score": sum(response.quality_metrics.values()) / len(response.quality_metrics),
            "context_usage": len(response.context_used.get("knowledge_items", [])) > 0
        }
        
        # Feedback explícito (se disponível)
        explicit_feedback = metadata.get("user_feedback", {})
        
        # Análise combinada
        overall_satisfaction = (
            implicit_feedback["quality_score"] * 0.7 +
            explicit_feedback.get("rating", 0.5) * 0.3
        )
        
        return {
            "implicit": implicit_feedback,
            "explicit": explicit_feedback,
            "overall_satisfaction": overall_satisfaction,
            "should_improve": overall_satisfaction < 0.6,
            "timestamp": datetime.now()
        }

class KnowledgeExtractor:
    """Extrai novo conhecimento de interações."""
    
    def __init__(self):
        self.extracted_knowledge = []
    
    async def extract_from_interaction(
        self,
        query: CognitiveQuery,
        response: CognitiveResponse,
        feedback: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extrai novo conhecimento da interação.
        
        Returns:
            Conhecimento extraído ou None
        """
        # Extrair entidades mencionadas
        entities = []
        for entity in query.context.get("entities", []) if query.context else []:
            entities.append({
                "text": entity.get("text"),
                "type": entity.get("type", "ENTITY"),
                "source": "user_query"
            })
        
        # Extrair relações implícitas
        relationships = []
        if query.context and response.context_used.get("knowledge_items"):
            # Relacionar query com conhecimento usado
            relationships.append({
                "type": "MENTIONS",
                "source": query.text[:50],
                "target": response.context_used.get("knowledge_items", [])[0] if response.context_used.get("knowledge_items") else None
            })
        
        # Se há conhecimento novo significativo
        if entities or relationships:
            return {
                "entities": entities,
                "relationships": relationships,
                "source_interaction": query.id,
                "timestamp": datetime.now()
            }
        
        return None

class ContinuousLearningLoop:
    """
    Loop de aprendizado contínuo.
    Registra interações e melhora o sistema.
    """
    
    def __init__(self):
        self.feedback_analyzer = FeedbackAnalyzer()
        self.knowledge_extractor = KnowledgeExtractor()
        self.interaction_history = []
        self.performance_history = []
        
        logger.info("Continuous Learning Loop inicializado")
    
    async def record_interaction(
        self,
        query: CognitiveQuery,
        response: CognitiveResponse,
        intent_analysis: IntentAnalysis
    ):
        """
        Registra interação para aprendizado.
        
        Args:
            query: Query original
            response: Resposta gerada
            intent_analysis: Análise de intenção
        """
        try:
            # 1. Coleta de feedback
            metadata = {
                "intent": intent_analysis.primary_intent,
                "model_used": response.model_used,
                "quality_metrics": response.quality_metrics
            }
            
            feedback = await self.feedback_analyzer.analyze_feedback(
                query, response, metadata
            )
            
            # 2. Extração de novo conhecimento
            new_knowledge = await self.knowledge_extractor.extract_from_interaction(
                query, response, feedback
            )
            
            # 3. Armazenar interação
            interaction_record = {
                "query_id": query.id,
                "timestamp": datetime.now(),
                "query": query.text,
                "response": response.response,
                "intent": intent_analysis.primary_intent,
                "feedback": feedback,
                "knowledge_extracted": new_knowledge is not None,
                "quality_metrics": response.quality_metrics
            }
            
            self.interaction_history.append(interaction_record)
            
            # Manter histórico limitado
            if len(self.interaction_history) > 1000:
                self.interaction_history = self.interaction_history[-1000:]
            
            # 4. Retornar conhecimento para integração
            if new_knowledge:
                logger.info(f"Novo conhecimento extraído da interação {query.id}")
                return new_knowledge
            
            return None
            
        except Exception as e:
            logger.error(f"Erro registrando interação: {e}")
            return None
    
    def should_retrain(
        self,
        feedback: Dict[str, Any],
        quality_metrics: Dict[str, float]
    ) -> bool:
        """
        Decide se deve retreinar baseado em feedback.
        
        Returns:
            True se deve retreinar
        """
        # Critérios para retreino
        satisfaction = feedback.get("overall_satisfaction", 0.5)
        avg_quality = sum(quality_metrics.values()) / len(quality_metrics)
        
        # Retreinar se qualidade baixa
        if satisfaction < 0.5 or avg_quality < 0.5:
            # Verificar se há padrão consistente
            recent_interactions = self.interaction_history[-10:]
            low_quality_count = sum(
                1 for i in recent_interactions
                if i.get("feedback", {}).get("overall_satisfaction", 0.5) < 0.5
            )
            
            # Retreinar se 30% ou mais das interações recentes têm baixa qualidade
            return low_quality_count >= 3
        
        return False
    
    async def schedule_incremental_training(self, feedback: Dict[str, Any]):
        """
        Agenda treinamento incremental.
        
        Args:
            feedback: Feedback que motivou o retreino
        """
        logger.info("Agendando treinamento incremental")
        
        # Por enquanto apenas log
        # TODO: Integrar com DistributedTrainingPipeline
        training_data = {
            "interactions": self.interaction_history[-100:],  # Últimas 100 interações
            "feedback": feedback,
            "timestamp": datetime.now()
        }
        
        logger.info(f"Dados de treinamento preparados: {len(training_data['interactions'])} interações")
        
        # TODO: Enviar para pipeline de treinamento
        # await self.training_pipeline.incremental_training(training_data)
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizado."""
        if not self.interaction_history:
            return {
                "total_interactions": 0,
                "avg_satisfaction": 0.0,
                "knowledge_extracted": 0
            }
        
        avg_satisfaction = sum(
            i.get("feedback", {}).get("overall_satisfaction", 0.0)
            for i in self.interaction_history
        ) / len(self.interaction_history)
        
        knowledge_count = sum(
            1 for i in self.interaction_history
            if i.get("knowledge_extracted", False)
        )
        
        return {
            "total_interactions": len(self.interaction_history),
            "avg_satisfaction": avg_satisfaction,
            "knowledge_extracted": knowledge_count,
            "recent_performance": [
                i.get("quality_metrics", {})
                for i in self.interaction_history[-10:]
            ]
        }

