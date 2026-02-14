"""
JARVIS 5.0 - Memory Manager
===========================
Gerencia memÃ³ria persistente usando ChromaDB e embeddings.
Suporta Gold Memories para DestilaÃ§Ã£o Neural (QI Adjacente).
"""

import os
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import time
import threading
from collections import deque

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except (ImportError, OSError):
    CHROMA_AVAILABLE = False

# Lazy loading: imports pesados serÃ£o feitos sob demanda
EMBEDDINGS_AVAILABLE = None  # SerÃ¡ verificado na primeira tentativa
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
        self.prompt_cache = {}  # ðŸ†• Phase 2: Prompt caching (LRU-like)
        self.max_cache_size = 50
        self.short_term_memory = deque(maxlen=10) # Memória RAM imediata (Inspirada no PVA)
        self._models_loaded = False  # Flag para lazy loading
        self._graph_lock = threading.Lock()  # ðŸ”’ ProteÃ§Ã£o para I/O concorrente do Grafo JSON
        self._chroma_lock = threading.Lock() # ðŸ”’ ProteÃ§Ã£o para o ChromaDB
        # In test mode we avoid heavy initialization (threads, DB operations, model imports)
        try:
            test_mode = bool(os.environ.get('JARVIS_TEST_MODE', False))
        except Exception:
            test_mode = False

        if not test_mode:
            self._initialize_db()
            self._start_maintenance_thread()
        else:
            logger.info("MemoryManager initialized in JARVIS_TEST_MODE: skipping DB and background threads")
        self._initialized = True

    def _start_maintenance_thread(self):
        """Inicia thread de manutenÃ§Ã£o periÃ³dica (TTL)"""
        def maintenance_loop():
            while True:
                try:
                    # Limpar memÃ³rias com mais de 30 dias (Phase 2 TTL)
                    self.purge_old_memories(days=30)
                except Exception as e:
                    # Ignorar erros de schema silenciosamente na thread de manutenÃ§Ã£o
                    if "Expected operand value" not in str(e):
                        logger.error(f"Erro na limpeza de memÃ³ria: {e}")
                
                # Dormir por 24 horas (fora do try para evitar loop infinito em caso de sucesso rÃ¡pido)
                time.sleep(24 * 3600)
        
        thread = threading.Thread(target=maintenance_loop, daemon=True)
        thread.start()
        logger.info("ðŸ§¹ Thread de manutenÃ§Ã£o de memÃ³ria iniciada (TTL: 30 dias)")

    def _initialize_db(self):
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB nÃ£o disponÃ­vel. MemÃ³ria em modo fallback (RAM).")
            return
        
        db_path = os.path.join(os.getcwd(), "data", "memory")
        os.makedirs(db_path, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Tentar criar/acessar coleÃ§Ã£o com auto-healing
            try:
                self.collection = self.client.get_or_create_collection(
                    name="jarvis_memory",
                    metadata={"description": "JARVIS conversation memory (Singularity 11.2)"}
                )
                # Testar se funciona
                count = self.collection.count()
                logger.info(f"âœ… ChromaDB inicializado: {count} memÃ³rias")
            except Exception as e:
                error_msg = str(e).lower()
                is_schema_error = any(kw in error_msg for kw in ['column', 'table', 'schema', 'sqlite'])
                
                if is_schema_error:
                    logger.warning(f"ðŸ”§ Schema corrompido detectado: {e}")
                    logger.info("ðŸ”„ Resetando ChromaDB...")
                    
                    # Reset completo do banco
                    try:
                        import shutil
                        backup_path = os.path.join(os.getcwd(), "data", f"memory_backup_{int(datetime.now().timestamp())}")
                        if os.path.exists(db_path):
                            shutil.move(db_path, backup_path)
                            logger.info(f"ðŸ“¦ Backup criado: {backup_path}")
                        
                        os.makedirs(db_path, exist_ok=True)
                        self.client = chromadb.PersistentClient(path=db_path)
                    except:
                        pass
                
                # Criar nova coleÃ§Ã£o
                try:
                    self.client.delete_collection("jarvis_memory")
                except:
                    pass
                    
                self.collection = self.client.create_collection(
                    name="jarvis_memory",
                    metadata={"description": "JARVIS conversation memory (Singularity 11.2 - Reset)"}
                )
                logger.info("âœ… ChromaDB coleÃ§Ã£o recriada com sucesso")
            
            # Modelos serÃ£o carregados sob demanda (lazy loading)
                
        except Exception as e:
            logger.error(f"Erro ao inicializar memÃ³ria: {e}")
            self.collection = None

    def _generate_id(self, command: str, timestamp: str) -> str:
        return hashlib.md5(f"{command}{timestamp}".encode()).hexdigest()

    def _ensure_models_loaded(self) -> bool:
        """Lazy loading: Carrega modelos de embedding apenas quando necessÃ¡rio"""
        global EMBEDDINGS_AVAILABLE, CROSSENCODER_AVAILABLE, SentenceTransformer, CrossEncoder
        
        if self._models_loaded:
            return True
        
        if EMBEDDINGS_AVAILABLE is None:
            try:
                logger.info("â³ Carregando modelos de embedding (primeira vez)...")
                from sentence_transformers import SentenceTransformer as ST, CrossEncoder as CE
                SentenceTransformer = ST
                CrossEncoder = CE
                EMBEDDINGS_AVAILABLE = True
                CROSSENCODER_AVAILABLE = True
            except (ImportError, OSError) as e:
                logger.warning(f"Modelos de embedding nÃ£o disponÃ­veis: {e}")
                EMBEDDINGS_AVAILABLE = False
                CROSSENCODER_AVAILABLE = False
                return False
        
        if not EMBEDDINGS_AVAILABLE:
            return False
        
        try:
            if self.embedding_model is None:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("âœ… Embedding model carregado")
            
            if self.reranker is None and CROSSENCODER_AVAILABLE:
                self.reranker = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
                logger.info("âœ… Reranker carregado")
            
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
        """Salva uma interaÃ§Ã£o. Se is_gold=True, marca como conhecimento destilado."""
        timestamp = datetime.now().isoformat()
        mem_id = self._generate_id(command, timestamp)
        combined_text = f"USER: {command}\nJARVIS: {response}"
        
        meta = metadata or {}
        meta["timestamp"] = timestamp
        meta["is_gold"] = "true" if is_gold else "false"
        
        # ðŸ†• Phase 2: Atualizar Cache de Prompts
        self.prompt_cache[command.strip().lower()] = response
        if len(self.prompt_cache) > self.max_cache_size:
            # Remover o primeiro item inserido (estratÃ©gia simples para exemplo)
            first_key = next(iter(self.prompt_cache))
            del self.prompt_cache[first_key]
        
        if self.collection:
            try:
                try:
                    embedding = self._create_embedding(combined_text)
                except Exception as e:
                    logger.warning(f"Embedding generation failed, saving without embedding: {e}")
                    embedding = None

                # ðŸ†• Usar upsert ao invÃ©s de add para evitar warnings de IDs duplicados
                with self._chroma_lock:
                    self.collection.upsert(
                        ids=[mem_id],
                        documents=[combined_text],
                        metadatas=[meta],
                        embeddings=[embedding] if embedding else None
                    )

                if is_gold:
                    logger.info(f"âœ¨ MemÃ³ria de OURO destilada: {mem_id[:8]}")
            except Exception as e:
                logger.error(f"Erro ao salvar memÃ³ria persistente: {e}")
        else:
            self.memory_cache[mem_id] = {"text": combined_text, "meta": meta}
            
        # PUSH TO RAM (Short-term)
        self.short_term_memory.append({
            "user": command,
            "jarvis": response,
            "timestamp": timestamp
        })
        
        return True

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

    def get_immediate_context(self) -> str:
        """Retorna as últimas interações da RAM (Short-term context)"""
        if not self.short_term_memory: return ""
        
        ctx = "\n---\nCONTEXTO IMEDIATO (RAM):\n"
        for mem in self.short_term_memory:
            ctx += f"USER: {mem['user']}\nJARVIS: {mem['jarvis']}\n"
        ctx += "---\n"
        return ctx

    def get_cached_response(self, query: str) -> Optional[str]:
        """ðŸ†• Retorna resposta do cache se houver match exato"""
        return self.prompt_cache.get(query.strip().lower())

    def purge_old_memories(self, days: int = 30):
        """ðŸ†• Phase 2: Limpa memÃ³rias antigas (TTL)"""
        if not self.collection: return
        
        try:
            import time
            from datetime import timedelta
            
            # Formato ISO string para compatibilidade com o que foi salvo
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # ChromaDB purge com tratamento de erros de schema (Robust Cleanup)
            try:
                # Tentativa 1: Query direta (rÃ¡pida)
                with self._chroma_lock:
                    self.collection.delete(
                        where={"timestamp": {"$lt": cutoff_date}}
                    )
                logger.info(f"Memoria limpa: Registros anteriores a {cutoff_date} removidos (Fast Path).")
            except Exception as e:
                # Fallback: Se o esquema estiver corrompido (type mismatch warning), fazemos via Python
                if "Expected operand value" in str(e) or "operator" in str(e):
                    logger.debug("ChromaDB Schema mismatch detected. Using manual cleanup fallback.")
                    
                    # Pegar todos os metadados
                    all_data = self.collection.get(include=['metadatas'])
                    ids_to_delete = []
                    
                    if all_data and 'metadatas' in all_data and all_data['metadatas']:
                        for idx, meta in enumerate(all_data['metadatas']):
                            if meta and 'timestamp' in meta:
                                ts = meta['timestamp']
                                # ComparaÃ§Ã£o de strings ISO funciona (YYYY-MM-DD...)
                                if ts < cutoff_date:
                                    ids_to_delete.append(all_data['ids'][idx])
                    
                    if ids_to_delete:
                        # Deletar em chunchs de 100 para nÃ£o travar
                        batch_size = 100
                        for i in range(0, len(ids_to_delete), batch_size):
                            batch = ids_to_delete[i:i + batch_size]
                            with self._chroma_lock:
                                self.collection.delete(ids=batch)
                            
                        logger.info(f"Limpeza Manual Concluida: {len(ids_to_delete)} memorias antigas removidas.")
                    else:
                        logger.debug("Nenhuma memoria antiga encontrada para limpeza manual.")
                else:
                    raise e

        except Exception as e:
            logger.error(f"Erro genÃ©rico ao limpar memÃ³ria: {e}")

    def save_to_vault(self, content: str, metadata: Dict[str, Any] = None):
        """
        ðŸ†• Fase 4: Cofre (Deep Storage)
        Salva conteÃºdo bruto no ChromaDB para recuperaÃ§Ã£o semÃ¢ntica futura.
        """
        if not self.collection:
            logger.warning("ChromaDB indisponÃ­vel. Salvando apenas em log.")
            return

        try:
            doc_id = hashlib.md5(content.encode()).hexdigest()
            current_time = datetime.now().isoformat()
            
            meta = metadata or {}
            meta['timestamp'] = current_time
            meta['type'] = 'vault_entry'
            
            with self._chroma_lock:
                self.collection.add(
                    documents=[content],
                    metadatas=[meta],
                    ids=[doc_id]
                )
            logger.info(f"ðŸ”’ ConteÃºdo salvo no Cofre (Vault): {doc_id[:8]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar no Cofre: {e}")

    def extract_semantic_graph(self, text_content: str):
        """
        ðŸ†• Fase 4: Grafo (Fast Recall)
        Extrai conceitos chave e salva em JSON leve para carga rÃ¡pida na RAM.
        """
        try:
            import ollama
            
            # Prompt para extraÃ§Ã£o estruturada
            prompt = (
                f"Extraia os conceitos principais deste texto em formato JSON simples prescrevendo relaÃ§Ãµes.\n"
                f"Texto: {text_content[:2000]}...\n\n"
                f"SaÃ­da esperada apenas JSON: {{\"Conceito\": \"DefiniÃ§Ã£o\", \"RelacionadoA\": \"OutroConceito\"}}"
            )
            
            # Usar modelo leve (Tier Fast)
            response = ollama.chat(model='qwen2.5:3b', messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            json_str = response['message']['content']
            # Limpar markdown ```json ... ```
            if "```" in json_str:
                json_str = json_str.split("```")[1].replace("json", "").strip()
                
            graph_data = json.loads(json_str)
            
            # Salvar em arquivo local (Grafo)
            graph_path = os.path.join(os.getcwd(), "data", "memory", "concepts_graph.json")
            
            # ðŸ”’ Thread-Safe I/O
            with self._graph_lock:
                existing_graph = {}
                if os.path.exists(graph_path):
                    try:
                        with open(graph_path, 'r', encoding='utf-8') as f:
                            existing_graph = json.load(f)
                    except Exception as e:
                        logger.warning(f"Erro ao ler grafo existente (resetting): {e}")

                # Merge
                existing_graph.update(graph_data)
                
                # âœ‚ï¸ Pruning Inteligente (Limite de 500 conceitos para nÃ£o explodir RAM)
                MAX_GRAPH_SIZE = 500
                if len(existing_graph) > MAX_GRAPH_SIZE:
                    excess = len(existing_graph) - MAX_GRAPH_SIZE
                    # Remover os primeiros 'excess' itens (FIFO em Python 3.7+)
                    # NÃ£o Ã© perfeito (remove antigos), mas mantÃ©m o tamanho controlado
                    keys_to_remove = list(existing_graph.keys())[:excess]
                    for k in keys_to_remove:
                        del existing_graph[k]
                    logger.info(f"âœ‚ï¸ Grafo podado: {excess} conceitos antigos removidos.")
                
                # Write atomicamente (writes to temp then rename) para evitar leitura parcial
                # Mas no Windows rename atomico tem caveats, vamos usar lock simples + write direto por enquanto
                # protegido pelo lock
                with open(graph_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_graph, f, indent=2, ensure_ascii=False)
                
            logger.info(f"ðŸ•¸ï¸ Grafo SemÃ¢ntico atualizado com {len(graph_data)} novos conceitos.")
            
        except Exception as e:
            logger.error(f"Falha na extraÃ§Ã£o do Grafo SemÃ¢ntico: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas básicas do gerenciador de memória."""
        stats: Dict[str, Any] = {
            'chroma_available': CHROMA_AVAILABLE,
            'memory_cache_size': len(self.memory_cache),
            'prompt_cache_size': len(self.prompt_cache),
            'short_term_memory_len': len(self.short_term_memory),
            'models_loaded': self._models_loaded
        }

        try:
            if self.collection:
                try:
                    stats['collection_count'] = int(self.collection.count())
                except Exception:
                    stats['collection_count'] = None
            else:
                stats['collection_count'] = 0
        except Exception:
            stats['collection_count'] = None

        return stats

# InstÃ¢ncia global
memory_manager = MemoryManager()
