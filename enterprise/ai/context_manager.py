"""
Advanced Context Manager - Gerenciamento Avançado de Contexto
Gerencia memória de curto e longo prazo
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from core.logger import logger

class ShortTermMemory:
    """Memória de curto prazo (conversa atual)."""
    
    def __init__(self, max_items: int = 20):
        self.max_items = max_items
        self.conversation: List[Dict[str, Any]] = []
    
    def add_interaction(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Adiciona interação à memória."""
        self.conversation.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        })
        
        # Limitar tamanho
        if len(self.conversation) > self.max_items:
            self.conversation = self.conversation[-self.max_items:]
    
    async def get_recent_context(self, last_n: int = 5) -> List[Dict[str, Any]]:
        """Obtém contexto recente."""
        return self.conversation[-last_n:]
    
    def clear(self):
        """Limpa memória de curto prazo."""
        self.conversation = []

class LongTermMemory:
    """Memória de longo prazo (histórico persistente)."""
    
    def __init__(self):
        # Por enquanto em memória, pode usar banco de dados
        self.memories: List[Dict[str, Any]] = []
    
    async def recall_relevant_memories(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recupera memórias relevantes.
        
        Args:
            query: Query para buscar memórias
            limit: Número máximo de memórias
        
        Returns:
            Lista de memórias relevantes
        """
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Score de relevância simples
        scored_memories = []
        for memory in self.memories:
            memory_text = memory.get("content", "").lower()
            score = sum(1 for word in query_words if word in memory_text)
            
            if score > 0:
                scored_memories.append((memory, score))
        
        # Ordenar por score
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Retornar top N
        return [m[0] for m in scored_memories[:limit]]
    
    def store_memory(self, content: str, metadata: Optional[Dict] = None):
        """Armazena memória de longo prazo."""
        self.memories.append({
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        })

class RelevanceScorer:
    """Calcula relevância de contexto."""
    
    def score_relevance(
        self,
        context_item: Dict[str, Any],
        query: str
    ) -> float:
        """
        Calcula score de relevância.
        
        Returns:
            Score de 0.0 a 1.0
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        context_text = str(context_item.get("content", "")).lower()
        context_words = set(context_text.split())
        
        # Intersecção de palavras
        intersection = query_words & context_words
        
        if not query_words:
            return 0.0
        
        # Score baseado em palavras em comum
        score = len(intersection) / len(query_words)
        
        return min(1.0, score)

class ContextAssembler:
    """Monta contexto rico a partir de múltiplas fontes."""
    
    def __init__(self):
        self.relevance_scorer = RelevanceScorer()
    
    async def assemble_context(
        self,
        short_term: List[Dict[str, Any]],
        long_term: List[Dict[str, Any]],
        domain_knowledge: Dict[str, Any],
        user_preferences: Dict[str, Any],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Monta contexto rico combinando múltiplas fontes.
        
        Returns:
            Contexto rico
        """
        # Resumo de memória de curto prazo
        short_term_summary = self._summarize_interactions(short_term)
        
        # Resumo de memória de longo prazo
        long_term_summary = self._summarize_memories(long_term)
        
        # Conhecimento do domínio
        domain_summary = ""
        if domain_knowledge.get("entities"):
            domain_summary = f"Entidades relevantes: {len(domain_knowledge['entities'])}"
        
        # Construir contexto combinado
        context = {
            "short_term": {
                "summary": short_term_summary,
                "items": len(short_term)
            },
            "long_term": {
                "summary": long_term_summary,
                "items": len(long_term)
            },
            "domain_knowledge": {
                "entities": domain_knowledge.get("entities", [])[:5],  # Limitar
                "summary": domain_summary
            },
            "user_preferences": user_preferences,
            "summary": f"{short_term_summary} {long_term_summary}",
            "timestamp": datetime.now()
        }
        
        return context
    
    def _summarize_interactions(self, interactions: List[Dict[str, Any]]) -> str:
        """Resume interações."""
        if not interactions:
            return ""
        
        # Última interação do usuário
        user_messages = [i for i in interactions if i.get("role") == "user"]
        if user_messages:
            last_user = user_messages[-1].get("content", "")[:100]
            return f"Contexto recente: {last_user}..."
        
        return ""
    
    def _summarize_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Resume memórias."""
        if not memories:
            return ""
        
        # Combinar conteúdos relevantes
        contents = [m.get("content", "")[:50] for m in memories[:3]]
        return f"Memórias relacionadas: {'; '.join(contents)}..."

class AdvancedContextManager:
    """
    Gerenciador avançado de contexto.
    Integra memória de curto e longo prazo.
    """
    
    def __init__(self):
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.context_assembler = ContextAssembler()
        
        logger.info("Advanced Context Manager inicializado")
    
    async def build_context(
        self,
        query: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói contexto rico para a IA.
        
        Args:
            query: Query atual
            user_context: Contexto do usuário
        
        Returns:
            Contexto rico
        """
        # 1. Memória de curto prazo
        short_term = await self.short_term_memory.get_recent_context()
        
        # 2. Memória de longo prazo
        long_term = await self.long_term_memory.recall_relevant_memories(query)
        
        # 3. Conhecimento do domínio (vindo do knowledge graph externo)
        domain_knowledge = user_context.get("intent_analysis", {}).get("entities", [])
        
        # 4. Preferências do usuário
        user_preferences = await self._get_user_preferences(user_context)
        
        # 5. Montar contexto
        rich_context = await self.context_assembler.assemble_context(
            short_term,
            long_term,
            {"entities": domain_knowledge},
            user_preferences,
            query
        )
        
        return rich_context
    
    async def _get_user_preferences(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém preferências do usuário."""
        # Por enquanto retornar vazio
        # TODO: Integrar com sistema de preferências
        return user_context.get("user_preferences", {})
    
    def record_interaction(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Registra interação na memória de curto prazo."""
        self.short_term_memory.add_interaction(role, content, metadata)
    
    def store_important_memory(self, content: str, metadata: Optional[Dict] = None):
        """Armazena memória importante de longo prazo."""
        self.long_term_memory.store_memory(content, metadata)

