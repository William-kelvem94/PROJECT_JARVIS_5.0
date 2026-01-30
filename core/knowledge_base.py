"""
Knowledge Base - Sistema de Conhecimento Persistente
Armazena conhecimento aprendido das interações em banco vetorial
Integra com VectorStore para busca semântica
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from core.logger import logger
from modules.rag.vector_store import VectorStore
from modules.memory.persistent_memory import PersistentMemory

class KnowledgeBase:
    """
    Sistema de conhecimento persistente que:
    - Extrai conhecimento das interações
    - Armazena em banco vetorial
    - Permite busca semântica
    - Aprende continuamente
    """
    
    def __init__(self, vector_store: VectorStore = None, memory: PersistentMemory = None):
        """
        Inicializa Knowledge Base.
        
        Args:
            vector_store: Instância do VectorStore (cria nova se None)
            memory: Instância de PersistentMemory (cria nova se None)
        """
        if vector_store is None:
            self.vector_store = VectorStore()
        else:
            self.vector_store = vector_store
        
        if memory is None:
            self.memory = PersistentMemory()
        else:
            self.memory = memory
        
        logger.info("KnowledgeBase inicializado")
    
    def extract_and_store_knowledge(
        self,
        user_query: str,
        assistant_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extrai conhecimento de uma interação e armazena.
        
        Args:
            user_query: Query do usuário
            assistant_response: Resposta do assistente
            context: Contexto adicional
        
        Returns:
            Resultado da operação
        """
        try:
            # Extrair conhecimento útil da interação
            knowledge_items = self._extract_knowledge_items(user_query, assistant_response, context)
            
            stored_count = 0
            for item in knowledge_items:
                # Armazenar cada item no banco vetorial
                result = self.vector_store.add_document(
                    text=item["text"],
                    metadata={
                        "type": item["type"],
                        "source": item.get("source", "user_interaction"),
                        "query": user_query[:200],  # Primeiros 200 chars
                        "timestamp": datetime.now().isoformat(),
                        **item.get("metadata", {})
                    },
                    doc_id=item.get("id")
                )
                
                if result.get("success"):
                    stored_count += 1
            
            logger.info(f" {stored_count} itens de conhecimento armazenados")
            
            # Salvar estatísticas
            stats = self.get_stats()
            self.memory.save_context("knowledge_base_stats", stats)
            
            return {
                "success": True,
                "stored_count": stored_count,
                "total_items": len(knowledge_items)
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair e armazenar conhecimento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_knowledge_items(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extrai itens de conhecimento de uma interação.
        
        Returns:
            Lista de itens de conhecimento extraídos
        """
        items = []
        
        # 1. Resposta completa como conhecimento geral
        if len(response) > 50:  # Apenas respostas significativas
            items.append({
                "id": f"knowledge_{datetime.now().timestamp()}",
                "type": "response",
                "text": f"Pergunta: {query}\nResposta: {response}",
                "source": "user_interaction"
            })
        
        # 2. Extrair fatos mencionados na resposta
        facts = self._extract_facts(response)
        for i, fact in enumerate(facts):
            items.append({
                "id": f"fact_{datetime.now().timestamp()}_{i}",
                "type": "fact",
                "text": fact,
                "source": "extracted_from_response"
            })
        
        # 3. Extrair conceitos/chaves mencionados
        concepts = self._extract_concepts(query, response)
        for i, concept in enumerate(concepts):
            items.append({
                "id": f"concept_{datetime.now().timestamp()}_{i}",
                "type": "concept",
                "text": concept,
                "source": "extracted_from_interaction"
            })
        
        return items
    
    def _extract_facts(self, text: str) -> List[str]:
        """
        Extrai fatos do texto.
        Método simples - pode ser melhorado com NLP.
        """
        facts = []
        
        # Buscar padrões de fatos (simples)
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            # Considerar fatos: frases afirmativas > 20 chars
            if len(sentence) > 20 and not sentence.startswith(('?', '!', 'Como', 'Por que')):
                facts.append(sentence)
        
        # Limitar a 3 fatos mais relevantes
        return facts[:3]
    
    def _extract_concepts(self, query: str, response: str) -> List[str]:
        """
        Extrai conceitos mencionados.
        """
        concepts = []
        
        # Palavras-chave importantes (simples)
        important_words = []
        for word in query.split():
            if len(word) > 4:  # Palavras > 4 chars
                important_words.append(word.lower())
        
        # Adicionar como conceitos se mencionados na resposta
        response_lower = response.lower()
        for word in important_words:
            if word in response_lower:
                concepts.append(f"{word}: mencionado em contexto de '{query[:50]}'")
        
        return concepts[:5]  # Limitar a 5 conceitos
    
    def search_knowledge(
        self,
        query: str,
        n_results: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Busca conhecimento relevante.
        
        Args:
            query: Query de busca
            n_results: Número de resultados
            min_score: Score mínimo
        
        Returns:
            Lista de itens de conhecimento encontrados
        """
        try:
            return self.vector_store.search(query, n_results=n_results, min_score=min_score)
        except Exception as e:
            logger.error(f"Erro ao buscar conhecimento: {e}")
            return []
    
    def get_context_for_query(
        self,
        query: str,
        max_results: int = 3,
        max_chars: int = 2000
    ) -> str:
        """
        Obtém contexto relevante formatado para usar no prompt do LLM.
        
        Args:
            query: Query do usuário
            max_results: Número máximo de resultados
            max_chars: Número máximo de caracteres
        
        Returns:
            Contexto formatado
        """
        try:
            results = self.search_knowledge(query, n_results=max_results)
            
            if not results:
                return ""
            
            context_parts = []
            total_chars = 0
            
            for i, doc in enumerate(results, 1):
                doc_text = doc.get("text", "")
                
                # Truncar se necessário
                remaining = max_chars - total_chars
                if remaining <= 0:
                    break
                
                if len(doc_text) > remaining:
                    doc_text = doc_text[:remaining] + "..."
                
                context_parts.append(f"[Conhecimento {i}]\n{doc_text}\n")
                total_chars += len(doc_text) + len(f"[Conhecimento {i}]\n\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto: {e}")
            return ""
    
    def auto_learn_from_interactions(self, limit: int = 100):
        """
        Aprende automaticamente do histórico de interações.
        
        Args:
            limit: Número máximo de interações para processar
        """
        try:
            # Buscar histórico de conversas
            history = self.memory.get_conversation_history(limit=limit * 2)
            
            # Agrupar por pares user-assistant
            pairs = []
            current_user = None
            
            for msg in history:
                if msg["role"] == "user":
                    current_user = msg["content"]
                elif msg["role"] == "assistant" and current_user:
                    pairs.append({
                        "query": current_user,
                        "response": msg["content"],
                        "timestamp": msg.get("timestamp")
                    })
                    current_user = None
            
            # Processar pares
            learned_count = 0
            for pair in pairs[:limit]:
                result = self.extract_and_store_knowledge(
                    user_query=pair["query"],
                    assistant_response=pair["response"]
                )
                
                if result.get("success"):
                    learned_count += result.get("stored_count", 0)
            
            logger.info(f" Aprendizado automático: {learned_count} itens extraídos de {len(pairs)} interações")
            
            return {
                "success": True,
                "processed_pairs": len(pairs),
                "learned_items": learned_count
            }
            
        except Exception as e:
            logger.error(f"Erro no aprendizado automático: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do Knowledge Base."""
        try:
            vector_stats = self.vector_store.get_stats()
            memory_stats = self.memory.get_stats() if self.memory else {}
            
            return {
                "vector_store": vector_stats,
                "memory": memory_stats,
                "total_documents": vector_stats.get("document_count", 0),
                "knowledge_items": vector_stats.get("document_count", 0)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                "error": str(e)
            }
    
    def clear_knowledge(self):
        """Limpa todo o conhecimento armazenado."""
        try:
            # Limpar vector store (criar nova coleção)
            self.vector_store = VectorStore()
            logger.info(" Base de conhecimento limpa")
            return {"success": True}
        except Exception as e:
            logger.error(f"Erro ao limpar conhecimento: {e}")
            return {"success": False, "error": str(e)}

