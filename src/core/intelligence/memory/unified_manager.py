"""
JARVIS 5.0 - Unified Memory Architecture
Consolidates Interaction, Lessons, Knowledge (RAG), and Vault.
"""

import os
import logging
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
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
        if self._initialized: return
        from src.utils.config import config
        self.db_path = config.MEMORY_DIR
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.interactions = None
        self.lessons = None
        self.knowledge = None
        
        self.short_term = deque(maxlen=15)
        self.prompt_cache = {}
        self.max_cache = 50
        
        self.model = None
        self._models_loading = False
        self._lock = threading.Lock()
        
        self._initialize_db()
        self._initialized = True

    def _initialize_db(self):
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB offline. Memory running in volatile mode.")
            return
            
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            self.interactions = self.client.get_or_create_collection("jarvis_memory", metadata={"hnsw:space": "cosine"})
            self.lessons = self.client.get_or_create_collection("jarvis_lessons", metadata={"hnsw:space": "cosine"})
            self.knowledge = self.client.get_or_create_collection("jarvis_knowledge", metadata={"hnsw:space": "cosine"})
            logger.info("✅ Unified Memory collections initialized.")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")

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
        
        # Cache Update
        self.prompt_cache[prompt.strip().lower()] = response
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
