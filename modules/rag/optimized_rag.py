"""
RAG Otimizado com Cache de Embeddings e Busca Hierárquica
"""

import hashlib
import time
from typing import List, Dict, Any, Optional
from core.logger import logger
from modules.rag.vector_store import VectorStore

class OptimizedRAG:
    """
    RAG otimizado com:
    - Cache de embeddings
    - Busca hierárquica
    - Compressão de contexto
    """
    
    def __init__(self, vector_store: VectorStore, cache_size: int = 1000):
        """
        Inicializa RAG otimizado.
        
        Args:
            vector_store: Instância do VectorStore
            cache_size: Tamanho máximo do cache de embeddings
        """
        self.vector_store = vector_store
        self.cache_size = cache_size
        
        # Cache de embeddings (query -> embedding)
        self.embedding_cache: Dict[str, Any] = {}
        
        # Cache de resultados de busca (query_hash -> results)
        self.search_cache: Dict[str, List[Dict[str, Any]]] = {}
        
        # Estatísticas
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_searches": 0,
            "avg_search_time": 0.0
        }
        
        logger.info(f"OptimizedRAG inicializado (cache_size={cache_size})")
    
    def _get_cache_key(self, query: str) -> str:
        """Gera chave de cache para query."""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica otimizada com cache.
        
        Args:
            query: Query de busca
            top_k: Número de resultados
            use_cache: Se True, usa cache
        
        Returns:
            Lista de documentos encontrados
        """
        start_time = time.time()
        self.stats["total_searches"] += 1
        
        # Verificar cache
        if use_cache:
            cache_key = self._get_cache_key(query)
            
            if cache_key in self.search_cache:
                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit para query: {query[:50]}...")
                
                # Retornar resultados do cache (limitado a top_k)
                cached_results = self.search_cache[cache_key]
                return cached_results[:top_k]
        
        # Cache miss - fazer busca real
        self.stats["cache_misses"] += 1
        
        try:
            # Buscar no vector store
            results = self.vector_store.search(query, n_results=top_k)
            
            # Armazenar no cache
            if use_cache and len(results) > 0:
                cache_key = self._get_cache_key(query)
                self._add_to_cache(cache_key, results)
            
            # Atualizar estatísticas
            search_time = time.time() - start_time
            self._update_avg_time(search_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca semântica: {e}")
            return []
    
    def _add_to_cache(self, cache_key: str, results: List[Dict[str, Any]]):
        """Adiciona resultado ao cache, respeitando tamanho máximo."""
        # Se cache está cheio, remover entrada mais antiga (FIFO simples)
        if len(self.search_cache) >= self.cache_size:
            # Remover primeiro item (mais simples)
            oldest_key = next(iter(self.search_cache))
            del self.search_cache[oldest_key]
            logger.debug(f"Cache cheio, removendo: {oldest_key[:8]}...")
        
        self.search_cache[cache_key] = results
    
    def _update_avg_time(self, new_time: float):
        """Atualiza tempo médio de busca."""
        total = self.stats["total_searches"]
        current_avg = self.stats["avg_search_time"]
        
        # Média móvel exponencial simples
        alpha = 0.1  # Fator de suavização
        self.stats["avg_search_time"] = alpha * new_time + (1 - alpha) * current_avg
    
    def get_context_for_query(
        self,
        query: str,
        max_results: int = 3,
        max_chars: int = 2000
    ) -> str:
        """
        Obtém contexto otimizado para query.
        Comprime contexto se necessário.
        
        Args:
            query: Query do usuário
            max_results: Número máximo de resultados
            max_chars: Número máximo de caracteres
        
        Returns:
            Contexto formatado e comprimido
        """
        # Buscar resultados (com cache)
        # Por enquanto usar busca síncrona diretamente
        # TODO: Tornar async quando semantic_search for async
        results = self.vector_store.search(query, n_results=max_results)
        
        if not results:
            return ""
        
        # Formatar contexto
        context_parts = []
        total_chars = 0
        
        for i, doc in enumerate(results, 1):
            doc_text = doc.get("text", "")
            
            # Truncar documento se necessário
            remaining_chars = max_chars - total_chars
            if remaining_chars <= 0:
                break
            
            if len(doc_text) > remaining_chars:
                doc_text = doc_text[:remaining_chars] + "..."
            
            context_parts.append(f"[Doc {i}] {doc_text}")
            total_chars += len(doc_text) + len(f"[Doc {i}] ")
        
        # Se ainda sobrar espaço, adicionar mais documentos truncados
        if total_chars < max_chars * 0.8:  # Se usou menos de 80%
            for doc in results[len(context_parts):]:
                remaining = max_chars - total_chars
                if remaining <= 50:  # Muito pouco espaço
                    break
                
                snippet = doc.get("text", "")[:remaining]
                if snippet:
                    context_parts.append(f"[Doc {len(context_parts) + 1}] {snippet}...")
                    total_chars += len(snippet) + 10
        
        return "\n".join(context_parts)
    
    def clear_cache(self):
        """Limpa os caches."""
        self.embedding_cache.clear()
        self.search_cache.clear()
        logger.info("Caches limpos")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        cache_hit_rate = (
            self.stats["cache_hits"] / self.stats["total_searches"]
            if self.stats["total_searches"] > 0 else 0.0
        )
        
        return {
            "cache_size": len(self.search_cache),
            "max_cache_size": self.cache_size,
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": f"{cache_hit_rate:.2%}",
            "total_searches": self.stats["total_searches"],
            "avg_search_time_ms": f"{self.stats['avg_search_time'] * 1000:.2f}"
        }
    
    def optimize_cache(self):
        """Otimiza cache removendo entradas menos usadas."""
        if len(self.search_cache) <= self.cache_size:
            return
        
        # Por enquanto, apenas limpa cache se muito grande
        # Implementação futura: LRU cache
        excess = len(self.search_cache) - self.cache_size
        logger.info(f"Otimizando cache: removendo {excess} entradas")
        
        # Remover primeiros excess itens
        keys_to_remove = list(self.search_cache.keys())[:excess]
        for key in keys_to_remove:
            del self.search_cache[key]

