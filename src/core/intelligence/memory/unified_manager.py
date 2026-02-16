"""
JARVIS 5.0 - Unified Memory Architecture
Consolidates Interaction, Lessons, Knowledge (RAG), and Vault.
"""

<<<<<<< Updated upstream
import os
import logging
import hashlib
=======
import asyncio
import hashlib
import logging
import os
import shutil
import sqlite3
import threading
>>>>>>> Stashed changes
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
<<<<<<< Updated upstream
from pathlib import Path
=======
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
>>>>>>> Stashed changes

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
    # Suppress ChromaDB telemetry
    import os
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    os.environ["POSTHOG_DISABLED"] = "1"
    os.environ["CHROMA_TELEMETRY"] = "False"
    os.environ["CHROMA_SERVER_NO_TELEMETRY"] = "True"
except ImportError:
    CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class UnifiedMemoryManager:
    """Unified memory manager for JARVIS 5.0"""
    
    _instance = None
<<<<<<< Updated upstream
    
    def __new__(cls):
=======

    def __new__(cls, *args, **kwargs):
>>>>>>> Stashed changes
        if cls._instance is None:
            cls._instance = super(UnifiedMemoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
<<<<<<< Updated upstream
    
    def __init__(self):
        if self._initialized: return
        from src.utils.config import config
=======

    def __init__(self, storage_path: str | Path | None = None):
        if self._initialized:
            return
        from src.utils.config import config

        self.project_root = config.PROJECT_ROOT
>>>>>>> Stashed changes
        # Use unified vector store location
        if storage_path is None:
            self.db_path = self.project_root / "data" / "memory" / "vector_store"
        else:
            self.db_path = Path(storage_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.interactions = None
        self.lessons = None
        self.knowledge = None
        
        self.short_term = deque(maxlen=15)
        self.prompt_cache = {}
        self.max_cache = 50
        self.cache_timestamps = {}  # Track access times for LRU
        
        self.model = None
        self._models_loading = False
        self._lock = threading.Lock()
<<<<<<< Updated upstream
        
=======
        self._schema_recovered = False

>>>>>>> Stashed changes
        self._initialize_db()
        self._initialized = True
        
        # [EVENT-DRIVEN]
        self.event_bus = None

    def connect_event_bus(self, event_bus):
        """Connects to AsyncEventBus for background memory operations."""
        print("DEBUG: connect_event_bus called with corrected EventType usage")
        from src.core.infrastructure.async_event_bus import EventType
        self.event_bus = event_bus
        if self.event_bus:
            import asyncio
            # Subscribe to interaction events for background storage
            print(f"DEBUG: Subscribing to {EventType.AI_RESPONSE}")
            self.event_bus.subscribe(EventType.AI_RESPONSE, self._handle_interaction_event)
            logger.info("✅ UnifiedMemoryManager connected to Event Bus (background saving enabled).")

    async def _handle_interaction_event(self, event_data: Dict[str, Any]):
        """Handles ai.response.generated event asynchronously."""
        try:
            prompt = event_data.get("prompt")
            response = event_data.get("response")
            metadata = event_data.get("metadata", {})
            
            if prompt and response:
                # Offload heavy embedding/DB operations to thread pool
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, 
                    lambda: self.store_interaction(prompt, response, metadata)
                )
                logger.debug(f"💾 Memory saved in background: {prompt[:30]}...")
        except Exception as e:
            logger.error(f"Failed to handle memory event: {e}")

    def _initialize_db(self):
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB offline. Memory running in volatile mode.")
            return
<<<<<<< Updated upstream
            
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            self.interactions = self.client.get_or_create_collection("jarvis_memory", metadata={"hnsw:space": "cosine"})
            self.lessons = self.client.get_or_create_collection("jarvis_lessons", metadata={"hnsw:space": "cosine"})
            self.knowledge = self.client.get_or_create_collection("jarvis_knowledge", metadata={"hnsw:space": "cosine"})
=======

        if self._needs_schema_reset():
            logger.warning(
                "Detected incompatible ChromaDB schema before initialization. "
                "Creating backup and resetting vector store."
            )
            if not self._backup_and_reset_vector_store():
                if not self._switch_to_fallback_vector_store():
                    logger.error(
                        "Memory initialization aborted: unable to reset schema."
                    )
                    return
            self._schema_recovered = True

        try:
            self._create_chroma_collections()
>>>>>>> Stashed changes
            logger.info("✅ Unified Memory collections initialized.")
        except Exception as e:
            if self._is_schema_mismatch_error(e) and not self._schema_recovered:
                logger.warning(
                    "Detected incompatible ChromaDB schema. "
                    "Creating backup and resetting vector store."
                )
                self._stop_chroma_client()
                if (
                    self._backup_and_reset_vector_store()
                    or self._switch_to_fallback_vector_store()
                ):
                    self._schema_recovered = True
                    try:
                        self._create_chroma_collections()
                        logger.info(
                            "✅ Unified Memory collections initialized after schema reset."
                        )
                        return
                    except Exception as retry_error:
                        logger.error(
                            f"Memory reinitialization after reset failed: {retry_error}"
                        )
            logger.error(f"Memory initialization failed: {e}")

    def _create_chroma_collections(self):
        self.client = chromadb.PersistentClient(
            path=str(self.db_path), settings=Settings(anonymized_telemetry=False)
        )
        self.interactions = self.client.get_or_create_collection(
            "jarvis_memory", metadata={"hnsw:space": "cosine"}
        )
        self.lessons = self.client.get_or_create_collection(
            "jarvis_lessons", metadata={"hnsw:space": "cosine"}
        )
        self.knowledge = self.client.get_or_create_collection(
            "jarvis_knowledge", metadata={"hnsw:space": "cosine"}
        )

    def _is_schema_mismatch_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return "no such column: collections.topic" in message or (
            "no such column" in message and "collections." in message
        )

    def _needs_schema_reset(self) -> bool:
        db_file = self.db_path / "chroma.sqlite3"
        if not db_file.exists():
            return False

        try:
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='collections'"
                )
                if not cursor.fetchone():
                    return False

                cursor.execute("PRAGMA table_info(collections)")
                columns = {row[1] for row in cursor.fetchall()}
                # Current runtime expects collections.topic; reset if missing.
                return bool(columns) and "topic" not in columns
        except Exception:
            # If introspection fails, fallback to runtime initialization path.
            return False

    def _stop_chroma_client(self):
        if not self.client:
            return

        try:
            if hasattr(self.client, "_system"):
                self.client._system.stop()
        except Exception:
            pass
        finally:
            self.client = None

    def _backup_and_reset_vector_store(self) -> bool:
        backup_dir = self.project_root / "data" / "backups" / "chroma_schema"
        backup_dir.mkdir(parents=True, exist_ok=True)

        db_file = self.db_path / "chroma.sqlite3"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for attempt in range(1, 4):
            try:
                if db_file.exists():
                    backup_file = backup_dir / f"chroma_{timestamp}.sqlite3"
                    shutil.copy2(db_file, backup_file)
                    logger.warning(f"ChromaDB backup created at {backup_file}")

                for child in self.db_path.iterdir():
                    if child.is_file():
                        child.unlink(missing_ok=True)
                    else:
                        shutil.rmtree(child, ignore_errors=True)

                # Optional sanity check to ensure a clean slate.
                if db_file.exists():
                    with sqlite3.connect(db_file) as conn:
                        conn.execute("PRAGMA integrity_check;")

                return True
            except Exception as backup_error:
                if attempt < 3 and self._is_file_lock_error(backup_error):
                    time.sleep(0.5 * attempt)
                    continue
                logger.error(f"Failed to backup/reset vector store: {backup_error}")
                return False

        return False

    def _is_file_lock_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return "[winerror 32]" in message or "being used by another process" in message

    def _switch_to_fallback_vector_store(self) -> bool:
        try:
            fallback_root = (
                self.project_root / "data" / "memory" / "vector_store_fallback"
            )
            fallback_path = fallback_root / datetime.now().strftime(
                "runtime_%Y%m%d_%H%M%S"
            )
            fallback_path.mkdir(parents=True, exist_ok=True)
            self.db_path = fallback_path
            logger.warning(f"Using fallback vector store path: {self.db_path}")
            return True
        except Exception as fallback_error:
            logger.error(f"Failed to allocate fallback vector store: {fallback_error}")
            return False

    def _ensure_model(self):
        if self.model or self._models_loading: return self.model
        self._models_loading = True
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ Embedding model loaded.")
        except Exception as e:
            logger.warning(f"Embedding model failed to load: {e}")
        finally:
            self._models_loading = False
        return self.model

    def _embed(self, text: str):
        model = self._ensure_model()
        if model: return model.encode(text).tolist()
        return None

    def store_interaction(self, prompt: str, response: str, metadata: Dict = None):
        """Stores a conversational interaction."""
        ts = datetime.now().isoformat()
        mem_id = hashlib.md5(f"{prompt}{ts}".encode()).hexdigest()
        text = f"User: {prompt}\nJarvis: {response}"
        
        # Cache Update with LRU tracking
        key = prompt.strip().lower()
        self.prompt_cache[key] = response
        self.cache_timestamps[key] = time.time()
        
        # Enforce LRU Limit with cleanup
        self._cleanup_cache_if_needed()

        self.short_term.append({"user": prompt, "jarvis": response, "ts": ts})
        
        if self.interactions:
            try:
                emb = self._embed(text)
                with self._lock:
                    self.interactions.upsert(
                        ids=[mem_id], documents=[text], 
                        embeddings=[emb] if emb else None,
                        metadatas=[metadata or {"ts": ts}]
                    )
                    # Periodic ChromaDB cleanup
                    self._cleanup_chromadb_if_needed()
            except Exception as e: logger.debug(f"Persistence error: {e}")

    def store_lesson(self, trigger: str, action: str):
        """Stores a direct teaching rule."""
        if not self.lessons: return
        try:
            lid = f"lesson_{int(time.time())}"
            emb = self._embed(trigger)
            with self._lock:
                self.lessons.add(
                    ids=[lid], documents=[f"If '{trigger}' -> '{action}'"],
                    embeddings=[emb] if emb else None,
                    metadatas=[{"trigger": trigger, "action": action, "ts": datetime.now().isoformat()}]
                )
            logger.info(f"Learned: {trigger} -> {action}")
        except Exception as e: logger.error(f"Lesson storage failed: {e}")

    def get_context(self, query: str, n=3) -> str:
        """Retrieves combined context from interactions and knowledge."""
        if not self.interactions: return ""
        try:
            emb = self._embed(query)
            # Query Interactions
            res = self.interactions.query(query_embeddings=[emb] if emb else None, query_texts=[query] if not emb else None, n_results=n)
            
            # Query Knowledge
            kn_res = self.knowledge.query(query_embeddings=[emb] if emb else None, query_texts=[query] if not emb else None, n_results=2)
            
            parts = []
            if res['documents'][0]: parts.append("[HISTORY]\n" + "\n---\n".join(res['documents'][0]))
            if kn_res['documents'][0]: parts.append("[KNOWLEDGE]\n" + "\n---\n".join(kn_res['documents'][0]))
            
            return "\n".join(parts) if parts else ""
        except Exception: return ""
    def is_empty(self) -> bool:
        """Checks if the interaction collection is empty."""
        if not self.interactions: return True
        return self.interactions.count() == 0

    def store_bulk_interactions(self, interactions: List[Dict[str, str]]):
        """Stores multiple interactions efficiently."""
        for item in interactions:
            self.store_interaction(item.get("prompt", ""), item.get("response", ""))

    def get_immediate_context(self) -> str:
        """Returns short-term RAM context."""
        if not self.short_term: return ""
        history = [f"User: {m['user']}\nJarvis: {m['jarvis']}" for m in self.short_term]
        return "[SHORT_TERM_RAM]\n" + "\n---\n".join(history)

    def _cleanup_cache_if_needed(self):
        """Clean up prompt cache using LRU eviction when over limit"""
        if len(self.prompt_cache) <= self.max_cache:
            return
            
        # Sort by access time (oldest first)
        sorted_items = sorted(self.cache_timestamps.items(), key=lambda x: x[1])
        
        # Remove oldest entries until we're under the limit
        items_to_remove = len(self.prompt_cache) - self.max_cache + 5  # Remove extra 5 for buffer
        
        for key, _ in sorted_items[:items_to_remove]:
            if key in self.prompt_cache:
                del self.prompt_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
        
        logger.debug(f"🧹 Cache cleaned: removed {items_to_remove} old entries")

    def _cleanup_chromadb_if_needed(self):
        """Periodic cleanup of ChromaDB collections to prevent unbounded growth"""
        if not self.interactions:
            return
            
        try:
            # Check interaction count periodically (every 100 operations)
            if not hasattr(self, '_cleanup_counter'):
                self._cleanup_counter = 0
            self._cleanup_counter += 1
            
            if self._cleanup_counter % 100 != 0:
                return
                
            # Get current counts
            interaction_count = self.interactions.count()
            max_interactions = 5000  # Limit to 5K interactions
            
            if interaction_count > max_interactions:
                # Remove oldest entries (keep most recent 80%)
                keep_count = int(max_interactions * 0.8)
                remove_count = interaction_count - keep_count
                
                # Get all IDs with timestamps
                results = self.interactions.get(include=['metadatas'])
                if results['metadatas']:
                    # Sort by timestamp (oldest first)
                    entries_with_ts = []
                    for i, metadata in enumerate(results['metadatas']):
                        ts_str = metadata.get('ts', '2000-01-01T00:00:00')
                        try:
                            ts = datetime.fromisoformat(ts_str)
<<<<<<< Updated upstream
                            entries_with_ts.append((results['ids'][i], ts))
                        except:
                            entries_with_ts.append((results['ids'][i], datetime.min))
                    
=======
                            entries_with_ts.append((results["ids"][i], ts))
                        except Exception:
                            entries_with_ts.append((results["ids"][i], datetime.min))

>>>>>>> Stashed changes
                    # Sort by timestamp
                    entries_with_ts.sort(key=lambda x: x[1])
                    
                    # Remove oldest entries
                    ids_to_remove = [entry[0] for entry in entries_with_ts[:remove_count]]
                    
                    with self._lock:
                        self.interactions.delete(ids=ids_to_remove)
                    
                    logger.info(f"🧹 ChromaDB cleaned: removed {remove_count} old interactions")
                    
        except Exception as e:
            logger.debug(f"ChromaDB cleanup failed: {e}")

    def force_cache_cleanup(self):
        """Force immediate cache cleanup"""
        self._cleanup_cache_if_needed()
        
    def force_chromadb_cleanup(self):
        """Force immediate ChromaDB cleanup"""
        self._cleanup_chromadb_if_needed()
