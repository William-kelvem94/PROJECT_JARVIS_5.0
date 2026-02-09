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
import threading
import time

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except (ImportError, OSError):
    CHROMA_AVAILABLE = False

# Lazy loading: imports pesados serão feitos sob demanda
EMBEDDINGS_AVAILABLE = None  # Será verificado na primeira tentativa
CROSSENCODER_AVAILABLE = None
SentenceTransformer = None
CrossEncoder = None

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
        self.memory_cache = {}  # Fallback RAM
        self.prompt_cache = {}  # 🆕 Phase 2: Prompt caching (LRU-like)
        self.max_cache_size = 50
        self._models_loaded = False  # Flag para lazy loading
        self._initialize_db()
        self._start_maintenance_thread()
        self._initialized = True

    def _start_maintenance_thread(self):
        """Inicia thread de manutenção periódica (TTL)"""
        def maintenance_loop():
            while True:
                try:
                    # Limpar memórias com mais de 30 dias (Phase 2 TTL)
                    self.purge_old_memories(days=30)
                    # Dormir por 24 horas
                    time.sleep(24 * 3600)
                except Exception as e:
                    logger.error(f"Erro na thread de manutenção de memória: {e}")
                    time.sleep(3600) # Tentar de novo em 1h
        
        thread = threading.Thread(target=maintenance_loop, daemon=True)
        thread.start()
        logger.info("🧹 Thread de manutenção de memória iniciada (TTL: 30 dias)")

    def _initialize_db(self):
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB não disponível. Memória em modo fallback (RAM).")
            return
        
        db_path = os.path.join(os.getcwd(), "data", "memory")
        os.makedirs(db_path, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Tentar criar/acessar coleção com auto-healing
            try:
                self.collection = self.client.get_or_create_collection(
                    name="jarvis_memory",
                    metadata={"description": "JARVIS conversation memory (Singularity 11.2)"}
                )
                # Testar se funciona
                count = self.collection.count()
                logger.info(f"✅ ChromaDB inicializado: {count} memórias")
            except Exception as e:
                error_msg = str(e).lower()
                is_schema_error = any(kw in error_msg for kw in ['column', 'table', 'schema', 'sqlite'])
                
                if is_schema_error:
                    logger.warning(f"🔧 Schema corrompido detectado: {e}")
                    logger.info("🔄 Resetando ChromaDB...")
                    
                    # Reset completo do banco
                    try:
                        import shutil
                        backup_path = os.path.join(os.getcwd(), "data", f"memory_backup_{int(datetime.now().timestamp())}")
                        if os.path.exists(db_path):
                            shutil.move(db_path, backup_path)
                            logger.info(f"📦 Backup criado: {backup_path}")
                        
                        os.makedirs(db_path, exist_ok=True)
                        self.client = chromadb.PersistentClient(path=db_path)
                    except:
                        pass
                
                # Criar nova coleção
                try:
                    self.client.delete_collection("jarvis_memory")
                except:
                    pass
                    
                self.collection = self.client.create_collection(
                    name="jarvis_memory",
                    metadata={"description": "JARVIS conversation memory (Singularity 11.2 - Reset)"}
                )
                logger.info("✅ ChromaDB coleção recriada com sucesso")
            
            # Modelos serão carregados sob demanda (lazy loading)
                
        except Exception as e:
            logger.error(f"Erro ao inicializar memória: {e}")
            self.collection = None

    def _generate_id(self, command: str, timestamp: str) -> str:
        return hashlib.md5(f"{command}{timestamp}".encode()).hexdigest()

    def _ensure_models_loaded(self) -> bool:
        """Lazy loading: Carrega modelos de embedding apenas quando necessário"""
        global EMBEDDINGS_AVAILABLE, CROSSENCODER_AVAILABLE, SentenceTransformer, CrossEncoder
        
        if self._models_loaded:
            return True
        
        if EMBEDDINGS_AVAILABLE is None:
            try:
                logger.info("⏳ Carregando modelos de embedding (primeira vez)...")
                from sentence_transformers import SentenceTransformer as ST, CrossEncoder as CE
                SentenceTransformer = ST
                CrossEncoder = CE
                EMBEDDINGS_AVAILABLE = True
                CROSSENCODER_AVAILABLE = True
            except (ImportError, OSError) as e:
                logger.warning(f"Modelos de embedding não disponíveis: {e}")
                EMBEDDINGS_AVAILABLE = False
                CROSSENCODER_AVAILABLE = False
                return False
        
        if not EMBEDDINGS_AVAILABLE:
            return False
        
        try:
            if self.embedding_model is None:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("✅ Embedding model carregado")
            
            if self.reranker is None and CROSSENCODER_AVAILABLE:
                self.reranker = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
                logger.info("✅ Reranker carregado")
            
            self._models_loaded = True
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            return False
    
    def _create_embedding(self, text: str) -> Optional[List[float]]:
        if not self._ensure_models_loaded():
            return None
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
        
        # 🆕 Phase 2: Atualizar Cache de Prompts
        self.prompt_cache[command.strip().lower()] = response
        if len(self.prompt_cache) > self.max_cache_size:
            # Remover o primeiro item inserido (estratégia simples para exemplo)
            first_key = next(iter(self.prompt_cache))
            del self.prompt_cache[first_key]
        
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

    def get_cached_response(self, query: str) -> Optional[str]:
        """🆕 Retorna resposta do cache se houver match exato"""
        return self.prompt_cache.get(query.strip().lower())

    def purge_old_memories(self, days: int = 30):
        """🆕 Phase 2: Limpa memórias antigas (TTL)"""
        if not self.collection: return
        
        try:
            import time
            from datetime import timedelta
            
            # Formato ISO string para compatibilidade com o que foi salvo
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # ChromaDB purge com tratamento de erro de schema
            try:
                self.collection.delete(
                    where={"timestamp": {"$lt": cutoff_date}}
                )
                logger.info(f"🧹 Memória limpa: Registros anteriores a {cutoff_date} removidos.")
            except Exception as e:
                # Se der erro de tipo (operando int vs string), ignoramos por enquanto
                # para não crashar a thread de manutenção
                if "Expected operand value" in str(e):
                    logger.warning(f"⚠️ Erro de schema ao limpar memória (ignorado): {e}")
                else:
                    raise e

        except Exception as e:
            logger.error(f"Erro genérico ao limpar memória: {e}")

# Instância global
memory_manager = MemoryManager()
