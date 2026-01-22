"""
Semantic Memory - Sistema de busca semântica usando embeddings
Permite buscar memórias por significado, não apenas por palavras-chave
"""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from core.logger import logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers não disponível. Instale com: pip install sentence-transformers")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb não disponível. Instale com: pip install chromadb")


class SemanticMemory:
    """
    Sistema de memória com busca semântica usando embeddings.
    Permite recuperar memórias relevantes baseado no significado, não apenas palavras exatas.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        persist_directory: str = "./data/semantic_memory"
    ):
        """
        Inicializa sistema de memória semântica.
        
        Args:
            model_name: Nome do modelo de embeddings (default: all-MiniLM-L6-v2)
            persist_directory: Diretório para persistir dados
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not CHROMADB_AVAILABLE:
            raise ImportError(
                "Dependências necessárias não instaladas. "
                "Execute: pip install sentence-transformers chromadb"
            )
        
        self.model_name = model_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Inicializar modelo de embeddings
        logger.info(f"Carregando modelo de embeddings: {model_name}")
        self.embedder = SentenceTransformer(model_name)
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Coleções
        self.conversations = self.client.get_or_create_collection("conversations")
        self.knowledge = self.client.get_or_create_collection("knowledge")
        self.episodes = self.client.get_or_create_collection("episodes")
        
        logger.info("SemanticMemory inicializado com sucesso")
    
    def store_conversation(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Armazena conversa com embedding para busca semântica.
        
        Args:
            role: "user" ou "assistant"
            content: Conteúdo da mensagem
            metadata: Metadados adicionais
        
        Returns:
            ID da memória armazenada
        """
        # Gerar embedding
        embedding = self.embedder.encode(content).tolist()
        
        # ID único
        memory_id = f"conv_{int(time.time() * 1000)}"
        
        # Metadados
        full_metadata = {
            "role": role,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        # Armazenar
        self.conversations.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[full_metadata],
            ids=[memory_id]
        )
        
        logger.debug(f"Conversa armazenada: {memory_id}")
        return memory_id
    
    def search_conversations(
        self,
        query: str,
        n_results: int = 5,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca conversas semanticamente relacionadas.
        
        Args:
            query: Consulta em linguagem natural
            n_results: Número de resultados
            role_filter: Filtrar por role ("user" ou "assistant")
        
        Returns:
            Lista de conversas relevantes
        """
        # Gerar embedding da query
        query_embedding = self.embedder.encode(query).tolist()
        
        # Filtro opcional
        where_filter = {"role": role_filter} if role_filter else None
        
        # Buscar
        results = self.conversations.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        # Formatar resultados
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        logger.debug(f"Busca de conversas retornou {len(formatted_results)} resultados")
        return formatted_results
    
    def store_knowledge(
        self,
        content: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Armazena conhecimento/fato para recuperação futura.
        
        Args:
            content: Conteúdo do conhecimento
            category: Categoria (ex: "preference", "fact", "skill")
            metadata: Metadados adicionais
        
        Returns:
            ID do conhecimento armazenado
        """
        # Gerar embedding
        embedding = self.embedder.encode(content).tolist()
        
        # ID único
        knowledge_id = f"know_{int(time.time() * 1000)}"
        
        # Metadados
        full_metadata = {
            "category": category,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        # Armazenar
        self.knowledge.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[full_metadata],
            ids=[knowledge_id]
        )
        
        logger.debug(f"Conhecimento armazenado: {knowledge_id}")
        return knowledge_id
    
    def search_knowledge(
        self,
        query: str,
        n_results: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca conhecimento relevante.
        
        Args:
            query: Consulta
            n_results: Número de resultados
            category_filter: Filtrar por categoria
        
        Returns:
            Lista de conhecimentos relevantes
        """
        query_embedding = self.embedder.encode(query).tolist()
        
        where_filter = {"category": category_filter} if category_filter else None
        
        results = self.knowledge.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def store_episode(
        self,
        event: str,
        context: Dict[str, Any],
        importance: float = 0.5
    ) -> str:
        """
        Armazena episódio/evento específico.
        
        Args:
            event: Descrição do evento
            context: Contexto do evento
            importance: Importância do evento (0.0 a 1.0)
        
        Returns:
            ID do episódio
        """
        # Gerar embedding
        embedding = self.embedder.encode(event).tolist()
        
        # ID único
        episode_id = f"ep_{int(time.time() * 1000)}"
        
        # Metadados
        metadata = {
            "importance": importance,
            "timestamp": datetime.utcnow().isoformat(),
            "context": json.dumps(context)
        }
        
        # Armazenar
        self.episodes.add(
            embeddings=[embedding],
            documents=[event],
            metadatas=[metadata],
            ids=[episode_id]
        )
        
        logger.debug(f"Episódio armazenado: {episode_id}")
        return episode_id
    
    def recall_episodes(
        self,
        query: str,
        n_results: int = 5,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Recupera episódios relacionados.
        
        Args:
            query: Consulta
            n_results: Número de resultados
            min_importance: Importância mínima
        
        Returns:
            Lista de episódios relevantes
        """
        query_embedding = self.embedder.encode(query).tolist()
        
        # Buscar todos e filtrar por importância (ChromaDB tem limitações em filtros numéricos)
        results = self.episodes.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2  # Buscar mais para filtrar
        )
        
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                importance = metadata.get('importance', 0.0)
                
                if importance >= min_importance:
                    # Parse context de volta
                    context_str = metadata.get('context', '{}')
                    try:
                        context = json.loads(context_str)
                    except:
                        context = {}
                    
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "event": doc,
                        "context": context,
                        "importance": importance,
                        "timestamp": metadata.get('timestamp'),
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
                
                if len(formatted_results) >= n_results:
                    break
        
        return formatted_results
    
    def get_relevant_context(
        self,
        query: str,
        include_conversations: bool = True,
        include_knowledge: bool = True,
        include_episodes: bool = True,
        max_results_per_type: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recupera contexto relevante de todas as fontes.
        
        Args:
            query: Consulta
            include_conversations: Incluir conversas
            include_knowledge: Incluir conhecimento
            include_episodes: Incluir episódios
            max_results_per_type: Máximo de resultados por tipo
        
        Returns:
            Dicionário com contexto relevante de cada tipo
        """
        context = {}
        
        if include_conversations:
            context['conversations'] = self.search_conversations(query, max_results_per_type)
        
        if include_knowledge:
            context['knowledge'] = self.search_knowledge(query, max_results_per_type)
        
        if include_episodes:
            context['episodes'] = self.recall_episodes(query, max_results_per_type)
        
        logger.debug(f"Contexto relevante recuperado para: {query}")
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de memória."""
        return {
            "conversations_count": self.conversations.count(),
            "knowledge_count": self.knowledge.count(),
            "episodes_count": self.episodes.count(),
            "model": self.model_name,
            "persist_directory": str(self.persist_directory)
        }
    
    def clear_all(self):
        """Limpa toda a memória (use com cuidado!)."""
        logger.warning("Limpando toda a memória semântica...")
        self.client.delete_collection("conversations")
        self.client.delete_collection("knowledge")
        self.client.delete_collection("episodes")
        
        # Recriar coleções
        self.conversations = self.client.get_or_create_collection("conversations")
        self.knowledge = self.client.get_or_create_collection("knowledge")
        self.episodes = self.client.get_or_create_collection("episodes")
        
        logger.info("Memória semântica limpa")
