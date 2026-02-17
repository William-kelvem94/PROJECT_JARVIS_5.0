"""
JARVIS 5.0 - Unified Memory Architecture
Consolidates Interaction, Lessons, Knowledge (RAG), and Vault.
"""

import os
import logging
import hashlib
import time
import threading
from datetime import datetime
from typing import List, Dict, Any
from collections import deque

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

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedMemoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        from src.utils.config import config

        # Use unified vector store location
        self.db_path = config.PROJECT_ROOT / "data" / "memory" / "vector_store"
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = None
        self.interactions = None
        self.lessons = None
        self.knowledge = None
        # Backwards compatibility: some callers expect `collection` attribute
        self.collection = None

        self.short_term = deque(maxlen=15)
        self.prompt_cache = {}
        self.max_cache = 50
        self.cache_timestamps = {}  # Track access times for LRU

        self.model = None
        self._models_loading = False
        self._lock = threading.Lock()

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
            # Subscribe to interaction events for background storage
            print(f"DEBUG: Subscribing to {EventType.AI_RESPONSE}")
            self.event_bus.subscribe(
                EventType.AI_RESPONSE, self._handle_interaction_event
            )
            logger.info(
                "✅ UnifiedMemoryManager connected to Event Bus (background saving enabled)."
            )

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
                    None, lambda: self.store_interaction(prompt, response, metadata)
                )
                logger.debug(f"💾 Memory saved in background: {prompt[:30]}...")
        except Exception as e:
            logger.error(f"Failed to handle memory event: {e}")

    def _initialize_db(self):
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB offline. Memory running in volatile mode.")
            return

        try:
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
            # Back-compat: expose `collection` as the primary interactions collection
            self.collection = self.interactions
            logger.info("✅ Unified Memory collections initialized.")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")

    def _ensure_model(self):
        if self.model or self._models_loading:
            return self.model
        self._models_loading = True
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            logger.info("✅ Embedding model loaded.")
        except Exception as e:
            logger.warning(f"Embedding model failed to load: {e}")
        finally:
            self._models_loading = False
        return self.model

    def _embed(self, text: str):
        """Obtain embedding — prefer offloading to ProcessWorkerFactory to avoid blocking the main loop."""
        # Try offloading to a process worker first
        try:
            from src.core.infrastructure.process_worker_factory import (
                process_worker_factory,
                WorkerType,
                WorkerConfig,
            )

            # Ensure factory is running and AI worker type configured
            if not process_worker_factory._running:
                try:
                    process_worker_factory.configure_worker_type(
                        WorkerType.AI_PROCESSOR,
                        WorkerConfig(worker_type=WorkerType.AI_PROCESSOR, max_memory_mb=512, max_concurrent_tasks=1),
                    )
                except Exception:
                    pass
                try:
                    process_worker_factory.start()
                except Exception:
                    pass

            task_id = process_worker_factory.submit_task(
                WorkerType.AI_PROCESSOR, "text_embedding", text
            )
            result = process_worker_factory.get_task_result(task_id, timeout=20.0)
            if result and result.get("success") and result.get("result") is not None:
                return result.get("result")
        except Exception:
            # Fall back to in-process embedding
            pass

        # Fallback: local embedding (thread-based)
        model = self._ensure_model()
        if model:
            try:
                return model.encode(text).tolist()
            except Exception:
                return None
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
                        ids=[mem_id],
                        documents=[text],
                        embeddings=[emb] if emb else None,
                        metadatas=[metadata or {"ts": ts}],
                    )
                    # Periodic ChromaDB cleanup
                    self._cleanup_chromadb_if_needed()
            except Exception as e:
                logger.debug(f"Persistence error: {e}")

    def store_lesson(self, trigger: str, action: str):
        """Stores a direct teaching rule."""
        if not self.lessons:
            return
        try:
            lid = f"lesson_{int(time.time())}"
            emb = self._embed(trigger)
            with self._lock:
                self.lessons.add(
                    ids=[lid],
                    documents=[f"If '{trigger}' -> '{action}'"],
                    embeddings=[emb] if emb else None,
                    metadatas=[
                        {
                            "trigger": trigger,
                            "action": action,
                            "ts": datetime.now().isoformat(),
                        }
                    ],
                )
            logger.info(f"Learned: {trigger} -> {action}")
        except Exception as e:
            logger.error(f"Lesson storage failed: {e}")

    def get_context(self, query: str, n=3, max_memories: int = None) -> str:
        """Retrieves combined context from interactions and knowledge.

        Backwards-compatible: accepts `max_memories` (used by older callers/tests)
        which, when provided, overrides `n`.
        """
        # Maintain backward compatibility: allow callers to pass `max_memories`
        if max_memories is not None:
            n = max_memories

        if not self.interactions:
            return ""
        try:
            emb = self._embed(query)
            # Query Interactions
            res = self.interactions.query(
                query_embeddings=[emb] if emb else None,
                query_texts=[query] if not emb else None,
                n_results=n,
            )

            # Query Knowledge
            kn_res = self.knowledge.query(
                query_embeddings=[emb] if emb else None,
                query_texts=[query] if not emb else None,
                n_results=2,
            )

            parts = []
            if res["documents"][0]:
                parts.append("[HISTORY]\n" + "\n---\n".join(res["documents"][0]))
            if kn_res["documents"][0]:
                parts.append("[KNOWLEDGE]\n" + "\n---\n".join(kn_res["documents"][0]))

            return "\n".join(parts) if parts else ""
        except Exception:
            return ""

    def is_empty(self) -> bool:
        """Checks if the interaction collection is empty."""
        if not self.interactions:
            return True
        return self.interactions.count() == 0

    def store_bulk_interactions(self, interactions: List[Dict[str, str]]):
        """Stores multiple interactions efficiently."""
        for item in interactions:
            self.store_interaction(item.get("prompt", ""), item.get("response", ""))

    def get_immediate_context(self) -> str:
        """Returns short-term RAM context."""
        if not self.short_term:
            return ""
        history = [f"User: {m['user']}\nJarvis: {m['jarvis']}" for m in self.short_term]
        return "[SHORT_TERM_RAM]\n" + "\n---\n".join(history)

    def _cleanup_cache_if_needed(self):
        """Clean up prompt cache using LRU eviction when over limit"""
        if len(self.prompt_cache) <= self.max_cache:
            return

        # Sort by access time (oldest first)
        sorted_items = sorted(self.cache_timestamps.items(), key=lambda x: x[1])

        # Remove oldest entries until we're under the limit
        items_to_remove = (
            len(self.prompt_cache) - self.max_cache + 5
        )  # Remove extra 5 for buffer

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
            if not hasattr(self, "_cleanup_counter"):
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
                results = self.interactions.get(include=["metadatas"])
                if results["metadatas"]:
                    # Sort by timestamp (oldest first)
                    entries_with_ts = []
                    for i, metadata in enumerate(results["metadatas"]):
                        ts_str = metadata.get("ts", "2000-01-01T00:00:00")
                        try:
                            ts = datetime.fromisoformat(ts_str)
                            entries_with_ts.append((results["ids"][i], ts))
                        except:
                            entries_with_ts.append((results["ids"][i], datetime.min))

                    # Sort by timestamp
                    entries_with_ts.sort(key=lambda x: x[1])

                    # Remove oldest entries
                    ids_to_remove = [
                        entry[0] for entry in entries_with_ts[:remove_count]
                    ]

                    with self._lock:
                        self.interactions.delete(ids=ids_to_remove)

                    logger.info(
                        f"🧹 ChromaDB cleaned: removed {remove_count} old interactions"
                    )

        except Exception as e:
            logger.debug(f"ChromaDB cleanup failed: {e}")

    def force_cache_cleanup(self):
        """Force immediate cache cleanup"""
        self._cleanup_cache_if_needed()

    def force_chromadb_cleanup(self):
        """Force immediate ChromaDB cleanup"""
        self._cleanup_chromadb_if_needed()

    def get_stats(self) -> Dict[str, Any]:
        """Return lightweight statistics for monitoring and tests."""
        interactions_count = self.interactions.count() if self.interactions else 0
        lessons_count = self.lessons.count() if self.lessons else 0
        knowledge_count = self.knowledge.count() if self.knowledge else 0

        stats = {
            "db_path": str(self.db_path),
            "connected": bool(self.client),
            "short_term_len": len(self.short_term),
            "prompt_cache_size": len(self.prompt_cache),
            "collections": {
                "interactions": interactions_count,
                "lessons": lessons_count,
                "knowledge": knowledge_count,
            },
            "total_memories": interactions_count + lessons_count + knowledge_count,
        }
        return stats

    # Backwards-compatible convenience API expected by older callers/tests
    def remember(self, command: str, response: str) -> bool:
        """Save a single interaction (compat wrapper). Returns True on success."""
        try:
            self.store_interaction(command, response, metadata={"source": "remember"})
            return True
        except Exception:
            return False

    def recall(self, query: str, top_k: int = 3):
        """Return a list of similar stored interactions.

        If chromadb is available, use vector search; otherwise fall back to
        simple substring matching over short-term memory.
        """
        results = []
        try:
            if self.interactions:
                emb = self._embed(query)
                res = self.interactions.query(
                    query_embeddings=[emb] if emb else None,
                    query_texts=[query] if not emb else None,
                    n_results=top_k,
                )

                docs = res.get("documents", [[]])[0]
                ids = res.get("ids", [[]])[0]
                for i, doc in enumerate(docs):
                    results.append({"command": doc, "similarity": 1.0})
                return results

            # Fallback: search short-term memory
            for item in list(self.short_term)[-50:]:
                if query.lower() in item["user"].lower() or query.lower() in item["jarvis"].lower():
                    results.append({"command": item["user"], "similarity": 0.9})
                elif any(tok in item["user"].lower() for tok in query.lower().split()):
                    results.append({"command": item["user"], "similarity": 0.5})
                if len(results) >= top_k:
                    break
        except Exception:
            pass

        return results
