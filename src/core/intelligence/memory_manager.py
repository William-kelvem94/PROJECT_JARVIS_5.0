"""
JARVIS 5.0 - Memory Manager
===========================
Gerencia memória persistente usando ChromaDB e embeddings.
Suporta Gold Memories para Destilação Neural (QI Adjacente).
"""

import os
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except (ImportError, OSError):
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    EMBEDDINGS_AVAILABLE = True
    CROSSENCODER_AVAILABLE = True
except (ImportError, OSError):
    EMBEDDINGS_AVAILABLE = False
    CROSSENCODER_AVAILABLE = False

logger = logging.getLogger(__name__)

class MemoryManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized: return
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.reranker = None
        self.reranking_enabled = True
        self.memory_cache = {} # Fallback RAM
        self._initialize_db()
        self._initialized = True

    def _initialize_db(self):
        if not CHROMA_AVAILABLE: return
        
        db_path = os.path.join(os.getcwd(), "data", "memory")
        os.makedirs(db_path, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Tentar criar/acessar coleção
            try:
                self.collection = self.client.get_or_create_collection(
                    name="jarvis_memory",
                    metadata={"description": "JARVIS conversation memory (Singularity 11.2)"}
                )
                # Testar se funciona
                _ = self.collection.count()
                logger.info(f"✅ ChromaDB inicializado: {self.collection.count()} memórias")
            except Exception as e:
                # Se falhar, tentar deletar apenas a coleção
                logger.warning(f"⚠️ Erro ao acessar coleção: {e}")
                try:
                    self.client.delete_collection("jarvis_memory")
                except:
                    pass
                
                # Criar nova coleção
                self.collection = self.client.create_collection(
                    name="jarvis_memory",
                    metadata={"description": "JARVIS conversation memory (Singularity 11.2)"}
                )
                logger.info("✅ ChromaDB coleção recriada")
            
            # Carregar modelos apenas se coleção foi criada com sucesso
            if self.collection and EMBEDDINGS_AVAILABLE:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                self.reranker = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
                logger.info("✅ Modelos neurais de memória carregados (Embeddings + Reranker)")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar memória: {e}")
            self.collection = None

    def _generate_id(self, command: str, timestamp: str) -> str:
        return hashlib.md5(f"{command}{timestamp}".encode()).hexdigest()

    def _create_embedding(self, text: str) -> Optional[List[float]]:
        if self.embedding_model:
            return self.embedding_model.encode(text).tolist()
        return None

    def remember(self, command: str, response: str, metadata: Dict = None, is_gold: bool = False):
        """Salva uma interação. Se is_gold=True, marca como conhecimento destilado."""
        timestamp = datetime.now().isoformat()
        mem_id = self._generate_id(command, timestamp)
        combined_text = f"USER: {command}\nJARVIS: {response}"
        
        meta = metadata or {}
        meta["timestamp"] = timestamp
        meta["is_gold"] = "true" if is_gold else "false"
        
        if self.collection:
            try:
                embedding = self._create_embedding(combined_text)
                self.collection.add(
                    ids=[mem_id],
                    documents=[combined_text],
                    metadatas=[meta],
                    embeddings=[embedding] if embedding else None
                )
                if is_gold: logger.info(f"✨ Memória de OURO destilada: {mem_id[:8]}")
            except Exception as e:
                logger.error(f"Erro ao salvar memória persistente: {e}")
        else:
            self.memory_cache[mem_id] = {"text": combined_text, "meta": meta}

    def get_context(self, query: str, max_memories: int = 3) -> str:
        """Busca contexto priorizando Gold Memories"""
        if not self.collection: return ""
        try:
            embedding = self._create_embedding(query)
            results = self.collection.query(
                query_embeddings=[embedding] if embedding else None,
                query_texts=[query] if not embedding else None,
                n_results=max_memories * 2,
                include=["documents", "metadatas"]
            )
            
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            gold_docs = []
            standard_docs = []
            for d, m in zip(docs, metas):
                if m.get("is_gold") == "true":
                    gold_docs.append(f"[CONHECIMENTO_MESTRE] {d}")
                else:
                    standard_docs.append(d)
            
            final_docs = (gold_docs + standard_docs)[:max_memories]
            if not final_docs: return ""
            
            context = "\n---\nSABEDORIA ACUMULADA (BASE DE TREINO):\n"
            context += "\n---\n".join(final_docs)
            context += "\n---\n"
            return context
        except Exception:
            return ""

# Instância global
memory_manager = MemoryManager()
