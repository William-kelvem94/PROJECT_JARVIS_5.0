# ============================================================================
# JARVIS SINGULARITY - Memory Manager (Phase 3: Auto-Learning)
# ============================================================================
# Sistema de memória persistente com RAG (Retrieval-Augmented Generation)
# Usa ChromaDB para armazenar e recuperar interações
# ============================================================================

import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# IMPORTS CONDICIONAIS
# -------------------------------------------------------------------------
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("⚠️ ChromaDB não disponível - memória persistente desabilitada")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("⚠️ sentence-transformers não disponível - usando embeddings básicos")

# ============ P1: RAG RERANKING ============
try:
    from sentence_transformers import CrossEncoder
    CROSSENCODER_AVAILABLE = True
except ImportError:
    CROSSENCODER_AVAILABLE = False
    logger.warning("⚠️ CrossEncoder não disponível - reranking desabilitado")


# ============================================================================
# MEMORY MANAGER
# ============================================================================
class MemoryManager:
    """
    Gerencia memória persistente do JARVIS com RAG.
    
    CAPACIDADES:
    - Armazena interações (comando + resposta)
    - Busca memórias similares (semantic search)
    - Aprende com conversas passadas
    - Embeddings com SentenceTransformers
    """
    
    def __init__(self, persist_dir: str = "data/memory"):
        """
        Inicializa o Memory Manager.
        
        Args:
            persist_dir: Diretório para persistir ChromaDB
        """
        logger.info("🧠 Inicializando Memory Manager...")
        
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.memory_cache = {}  # In-memory fallback
        self._initialized = False  # Flag para lazy init
        
        # ============ P1: RAG RERANKING ============
        self.reranker = None  # CrossEncoder for reranking
        self.reranking_enabled = True
        
        # ⚡ LAZY INITIALIZATION
        # ChromaDB será inicializado apenas no primeiro uso
        # Isso previne crash durante boot
        logger.info("⚡ ChromaDB em modo LAZY (carrega no primeiro uso)")
        logger.info("✅ Memory Manager online (lazy mode)")
    
    def _ensure_initialized(self):
        """Lazy initialization - carrega ChromaDB apenas quando necessário"""
        if self._initialized:
            return
        
        logger.info("📦 Inicializando ChromaDB (lazy load)...")
        
        if not CHROMADB_AVAILABLE:
            logger.warning("⚠️ ChromaDB não disponível")
            self._initialized = True
            return
        
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self.collection = self.client.get_or_create_collection(
                name="jarvis_memory",
                metadata={"description": "JARVIS conversation memory"}
            )
            
            logger.info(f"✅ ChromaDB inicializado - {self.collection.count()} memórias")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
            logger.warning("⚠️ Usando fallback RAM")
            self.client = None
            self.collection = None
        
        # Carregar embeddings se ChromaDB funcionar
        if EMBEDDINGS_AVAILABLE and self.collection and not self.embedding_model:
            try:
                logger.info("📦 Carregando embeddings...")
                self.embedding_model = SentenceTransformer(
                    'paraphrase-multilingual-MiniLM-L12-v2'
                )
                logger.info("✅ Embeddings carregados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar embeddings: {e}")
        
        # ============ P1: RAG RERANKING ============
        if CROSSENCODER_AVAILABLE and not self.reranker:
            try:
                logger.info("📦 Carregando Reranker (CrossEncoder)...")
                # Modelo ultra-leve mas preciso para re-ranqueamento
                self.reranker = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
                logger.info("✅ Reranker carregado (Military Grade Recall)")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar Reranker: {e}")
                self.reranking_enabled = False
        
        self._initialized = True
    
    def _generate_id(self, command: str, timestamp: str) -> str:
        """Gera ID único para memória"""
        content = f"{command}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """Cria embedding para texto"""
        if self.embedding_model:
            try:
                return self.embedding_model.encode(text).tolist()
            except Exception as e:
                logger.error(f"❌ Erro ao criar embedding: {e}")
        return None
    
    def remember(
        self,
        command: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Salva uma interação na memória.
        
        Args:
            command: Comando do usuário
            response: Resposta do JARVIS
            metadata: Metadados adicionais
        
        Returns:
            True se salvou com sucesso
        """
        # Lazy init
        self._ensure_initialized()
        
        if not self.collection:
            # Fallback: salvar em memória RAM
            interaction_id = hashlib.md5(f"{command}{response}".encode()).hexdigest()
            self.memory_cache[interaction_id] = {
                "command": command,
                "response": response,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            logger.debug(f"💾 Salvo em cache RAM: {len(self.memory_cache)} memórias")
            return True
        
        try:
            timestamp = datetime.now().isoformat()
            memory_id = self._generate_id(command, timestamp)
            
            # Combinar comando e resposta para embedding
            combined_text = f"Comando: {command}\nResposta: {response}"
            
            # Criar embedding
            embedding = self._create_embedding(combined_text)
            
            # Preparar metadados
            mem_metadata = {
                "command": command[:500],  # Limitar tamanho
                "response": response[:500],
                "timestamp": timestamp,
                **(metadata or {})
            }
            
            # Adicionar à collection
            if embedding:
                self.collection.add(
                    ids=[memory_id],
                    embeddings=[embedding],
                    documents=[combined_text],
                    metadatas=[mem_metadata]
                )
            else:
                # Fallback sem embedding customizado
                self.collection.add(
                    ids=[memory_id],
                    documents=[combined_text],
                    metadatas=[mem_metadata]
                )
            
            logger.info(f"💾 Memória salva: {memory_id[:8]}...")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao salvar memória: {e}")
            return False
    
    def recall(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Busca memórias similares com reranking.
        
        Args:
            query: Consulta (comando atual)
            top_k: Número de memórias a retornar
            min_similarity: Similaridade mínima (0-1)
        
        Returns:
            Lista de memórias relevantes
        """
        # Lazy init
        self._ensure_initialized()
        
        if not self.collection:
            return []
        
        try:
            # ============ P1: RAG RERANKING ============
            # Fetch more candidates for reranking (top_k * 3)
            fetch_k = top_k * 3 if self.reranking_enabled and self.reranker else top_k
            
            # Criar embedding da query
            query_embedding = self._create_embedding(query)
            
            # Buscar memórias similares
            if query_embedding:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=fetch_k
                )
            else:
                # Fallback: busca por texto
                results = self.collection.query(
                    query_texts=[query],
                    n_results=fetch_k
                )
            
            # Processar resultados
            memories = []
            if results and results['metadatas']:
                for i, metadata in enumerate(results['metadatas'][0]):
                    # Verificar similaridade (se disponível)
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    similarity = 1 - distance  # Converter distância para similaridade
                    
                    if similarity >= min_similarity:
                        memories.append({
                            'command': metadata.get('command', ''),
                            'response': metadata.get('response', ''),
                            'timestamp': metadata.get('timestamp', ''),
                            'similarity': similarity
                        })
            
            # ============ P1: RAG RERANKING ============
            # Rerank using CrossEncoder for better relevance
            if self.reranking_enabled and self.reranker and len(memories) > top_k:
                logger.debug(f"🔄 Reranking {len(memories)} results...")
                
                # Create query-document pairs
                pairs = [[query, f"{mem['command']} {mem['response']}"] for mem in memories]
                
                # Get reranking scores
                scores = self.reranker.predict(pairs)
                
                # Sort by rerank score
                for i, mem in enumerate(memories):
                    mem['rerank_score'] = float(scores[i])
                
                memories = sorted(memories, key=lambda x: x['rerank_score'], reverse=True)[:top_k]
                logger.info(f"✅ Reranked to top {len(memories)} results")
            
            logger.info(f"🔍 Encontradas {len(memories)} memórias relevantes")
            return memories
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar memórias: {e}")
            return []
    
    def get_context(self, query: str, max_memories: int = 3) -> str:
        """
        Obtém contexto de memórias para incluir no prompt.
        
        Args:
            query: Consulta atual
            max_memories: Máximo de memórias a incluir
        
        Returns:
            String formatada com contexto
        """
        memories = self.recall(query, top_k=max_memories)
        
        if not memories:
            return ""
        
        context_parts = ["CONTEXTO DE MEMÓRIAS PASSADAS:"]
        
        for i, mem in enumerate(memories, 1):
            context_parts.append(
                f"\n{i}. [Similaridade: {mem['similarity']:.2f}]"
                f"\n   Comando: {mem['command']}"
                f"\n   Resposta: {mem['response']}"
            )
        
        return "\n".join(context_parts)
    
    def clear_old_memories(self, days: int = 30) -> int:
        """
        Remove memórias antigas.
        
        Args:
            days: Remover memórias mais antigas que X dias
        
        Returns:
            Número de memórias removidas
        """
        if not self.collection:
            return 0
        
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Obter todas as memórias
            all_memories = self.collection.get()
            
            # Filtrar memórias antigas
            old_ids = []
            for i, metadata in enumerate(all_memories['metadatas']):
                timestamp_str = metadata.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp < cutoff_date:
                        old_ids.append(all_memories['ids'][i])
            
            # Remover
            if old_ids:
                self.collection.delete(ids=old_ids)
                logger.info(f"🗑️ Removidas {len(old_ids)} memórias antigas")
            
            return len(old_ids)
        
        except Exception as e:
            logger.error(f"❌ Erro ao limpar memórias: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas da memória"""
        if not self.collection:
            return {"available": False}
        
        try:
            count = self.collection.count()
            
            return {
                "available": True,
                "total_memories": count,
                "persist_dir": str(self.persist_dir),
                "embedding_model": bool(self.embedding_model)
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats: {e}")
            return {"available": False, "error": str(e)}


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
memory_manager = MemoryManager()
