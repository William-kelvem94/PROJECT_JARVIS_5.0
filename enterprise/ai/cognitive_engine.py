"""
Cognitive Engine - Motor Cognitivo Principal
Processamento avançado com roteamento inteligente e aprendizado contínuo
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from core.logger import logger
from enterprise.ai.model_orchestrator import ModelOrchestrator
from enterprise.ai.knowledge_graph import EnterpriseKnowledgeGraph
from enterprise.ai.continuous_learning import ContinuousLearningLoop
from enterprise.ai.context_manager import AdvancedContextManager

@dataclass
class CognitiveQuery:
    """Query cognitiva com metadados."""
    id: str
    text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class CognitiveResponse:
    """Resposta cognitiva com métricas."""
    query_id: str
    response: str
    confidence: float
    model_used: str
    context_used: Dict[str, Any]
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class IntentAnalysis:
    """Análise de intenção e contexto."""
    primary_intent: str
    intents: Dict[str, float]  # Intent -> confidence
    entities: List[Dict[str, Any]]
    domain: str
    complexity: float  # 0.0 a 1.0
    requires_knowledge: bool
    metadata: Dict[str, Any]

class CognitiveEngine:
    """
    Motor cognitivo avançado com processamento inteligente.
    Integra modelos especializados, conhecimento e aprendizado contínuo.
    """
    
    def __init__(
        self,
        model_orchestrator: Optional[ModelOrchestrator] = None,
        knowledge_graph: Optional[EnterpriseKnowledgeGraph] = None,
        learning_loop: Optional[ContinuousLearningLoop] = None,
        context_manager: Optional[AdvancedContextManager] = None
    ):
        """
        Inicializa Cognitive Engine.
        
        Args:
            model_orchestrator: Orquestrador de modelos
            knowledge_graph: Grafo de conhecimento
            learning_loop: Loop de aprendizado
            context_manager: Gerenciador de contexto
        """
        self.model_orchestrator = model_orchestrator or ModelOrchestrator()
        self.knowledge_graph = knowledge_graph or EnterpriseKnowledgeGraph()
        self.learning_loop = learning_loop or ContinuousLearningLoop()
        self.context_manager = context_manager or AdvancedContextManager()
        
        logger.info("Cognitive Engine inicializado")
    
    async def process_query(self, query: CognitiveQuery) -> CognitiveResponse:
        """
        Processa query com pipeline cognitivo completo.
        
        Args:
            query: Query cognitiva
        
        Returns:
            Resposta cognitiva
        """
        logger.info(f"Processando query cognitiva: {query.id}")
        
        try:
            # 1. Análise de intenção e contexto
            intent_analysis = await self._analyze_intent_and_context(query)
            logger.debug(f"Intenção detectada: {intent_analysis.primary_intent}")
            
            # 2. Roteamento para modelo especializado
            specialized_model = await self._select_optimal_model(intent_analysis)
            logger.debug(f"Modelo selecionado: {specialized_model.get('name', 'unknown')}")
            
            # 3. Recuperação de conhecimento contextual
            context = await self._retrieve_relevant_knowledge(query, intent_analysis)
            logger.debug(f"Contexto recuperado: {len(context.get('knowledge', []))} itens")
            
            # 4. Construção de contexto rico
            rich_context = await self.context_manager.build_context(
                query.text,
                {
                    "user_id": query.user_id,
                    "session_id": query.session_id,
                    "intent_analysis": intent_analysis,
                    "external_context": query.context or {}
                }
            )
            
            # 5. Geração de resposta com ensemble
            response = await self._generate_enhanced_response(
                query,
                specialized_model,
                context,
                rich_context
            )
            
            # 6. Aprendizado contínuo (assíncrono)
            asyncio.create_task(
                self.learning_loop.record_interaction(
                    query, response, intent_analysis
                )
            )
            
            logger.info(f"Query {query.id} processada com sucesso")
            return response
            
        except Exception as e:
            logger.error(f"Erro processando query {query.id}: {e}")
            # Resposta de fallback
            return CognitiveResponse(
                query_id=query.id,
                response="Desculpe, ocorreu um erro ao processar sua solicitação.",
                confidence=0.0,
                model_used="fallback",
                context_used={},
                quality_metrics={"error": 1.0},
                metadata={"error": str(e)}
            )
    
    async def _analyze_intent_and_context(self, query: CognitiveQuery) -> IntentAnalysis:
        """
        Analisa intenção e contexto da query.
        
        Returns:
            Análise de intenção
        """
        # Usar modelo de intenção especializado ou geral
        intent_model = await self.model_orchestrator.get_intent_model()
        
        # Análise básica (pode ser melhorada com NLP avançado)
        text_lower = query.text.lower()
        
        # Detecção simples de intenção
        intents = {}
        
        # Categorias básicas
        if any(word in text_lower for word in ["abrir", "abre", "execute", "iniciar"]):
            intents["action"] = 0.8
        if any(word in text_lower for word in ["pergunta", "o que", "como", "explique"]):
            intents["question"] = 0.9
        if any(word in text_lower for word in ["ler", "mostrar", "buscar", "encontrar"]):
            intents["retrieve"] = 0.7
        if any(word in text_lower for word in ["criar", "fazer", "gerar", "produzir"]):
            intents["create"] = 0.8
        
        # Intent primário
        primary_intent = max(intents.items(), key=lambda x: x[1])[0] if intents else "general"
        
        # Análise de complexidade (simplificada)
        complexity = min(1.0, len(query.text.split()) / 50.0)
        
        # Extração simples de entidades (pode usar NER avançado)
        entities = []
        words = query.text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                entities.append({
                    "text": word,
                    "type": "ENTITY",
                    "position": i
                })
        
        return IntentAnalysis(
            primary_intent=primary_intent,
            intents=intents,
            entities=entities,
            domain="general",
            complexity=complexity,
            requires_knowledge=len(entities) > 0 or "?" in query.text,
            metadata={}
        )
    
    async def _select_optimal_model(self, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """
        Seleciona modelo ótimo baseado na análise de intenção.
        
        Returns:
            Especificação do modelo
        """
        return await self.model_orchestrator.select_optimal_model(intent_analysis)
    
    async def _retrieve_relevant_knowledge(
        self,
        query: CognitiveQuery,
        intent_analysis: IntentAnalysis
    ) -> Dict[str, Any]:
        """
        Recupera conhecimento relevante do grafo de conhecimento.
        
        Returns:
            Contexto de conhecimento
        """
        if not intent_analysis.requires_knowledge:
            return {"knowledge": []}
        
        try:
            # Buscar no knowledge graph
            knowledge_context = await self.knowledge_graph.query_knowledge(
                query.text,
                depth=2
            )
            
            return {
                "knowledge": knowledge_context.get("entities", []),
                "relationships": knowledge_context.get("relationships", []),
                "confidence": knowledge_context.get("confidence", 0.0)
            }
        except Exception as e:
            logger.error(f"Erro recuperando conhecimento: {e}")
            return {"knowledge": [], "error": str(e)}
    
    async def _generate_enhanced_response(
        self,
        query: CognitiveQuery,
        model_spec: Dict[str, Any],
        context: Dict[str, Any],
        rich_context: Dict[str, Any]
    ) -> CognitiveResponse:
        """
        Gera resposta aprimorada usando ensemble de modelos.
        
        Returns:
            Resposta cognitiva
        """
        # Construir prompt com contexto
        prompt = self._build_enhanced_prompt(query, context, rich_context)
        
        # Obter modelos para ensemble (pode usar múltiplos)
        models = [model_spec]  # Por enquanto, modelo único
        
        # Gerar resposta usando orquestrador
        response_data = await self.model_orchestrator.ensemble_models(
            prompt,
            models
        )
        
        # Calcular métricas de qualidade
        quality_metrics = {
            "relevance": response_data.get("confidence", 0.5),
            "completeness": min(1.0, len(response_data.get("response", "")) / 200),
            "coherence": 0.7  # Simplificado, pode usar modelo de análise
        }
        
        return CognitiveResponse(
            query_id=query.id,
            response=response_data.get("response", ""),
            confidence=response_data.get("confidence", 0.0),
            model_used=model_spec.get("name", "unknown"),
            context_used={
                "knowledge_items": len(context.get("knowledge", [])),
                "context_length": len(str(rich_context))
            },
            quality_metrics=quality_metrics,
            metadata=response_data.get("metadata", {})
        )
    
    def _build_enhanced_prompt(
        self,
        query: CognitiveQuery,
        context: Dict[str, Any],
        rich_context: Dict[str, Any]
    ) -> str:
        """Constrói prompt aprimorado com contexto."""
        prompt_parts = []
        
        # Contexto de conhecimento
        if context.get("knowledge"):
            prompt_parts.append("Contexto relevante:")
            for item in context["knowledge"][:3]:  # Limitar a 3 itens
                prompt_parts.append(f"- {item.get('description', str(item))}")
        
        # Contexto rico
        if rich_context.get("summary"):
            prompt_parts.append(f"\nContexto da conversa: {rich_context['summary']}")
        
        # Query original
        prompt_parts.append(f"\nPergunta do usuário: {query.text}")
        prompt_parts.append("\nResposta:")
        
        return "\n".join(prompt_parts)

import asyncio

