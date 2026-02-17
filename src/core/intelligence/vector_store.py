#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Unified Vector Store Manager
=========================================
Gerenciador centralizado para acesso ao ChromaDB unificado.
Substitui múltiplas instâncias espalhadas pelo projeto.

Usage:
    from src.core.intelligence.vector_store import get_vector_store

    # Obter instância única
    vs = get_vector_store()

    # Usar as coleções padronizadas
    interactions = vs.get_collection("interactions")
    knowledge = vs.get_collection("knowledge")
    learning = vs.get_collection("learning")
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any
import threading
from src.core.config.system_manifest import system_manifest

logger = logging.getLogger(__name__)

# Check ChromaDB availability
try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    Settings = None
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available. Vector store will run in fallback mode.")


class UnifiedVectorStore:
    """Unified Vector Store for JARVIS 5.0"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Suppress ChromaDB telemetry
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["POSTHOG_DISABLED"] = "1"
        os.environ["CHROMA_TELEMETRY"] = "False"
        os.environ["CHROMA_SERVER_NO_TELEMETRY"] = "True"

        # Unified vector store path
        try:
            from src.core.config.system_manifest import system_manifest
            self.db_path = Path(system_manifest.paths["vector_store"])
        except (ImportError, KeyError, AttributeError):
            # Fallback path discover
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
            self.db_path = project_root / "data" / "memory" / "vector_store"
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = None
        self.collections: Dict[str, Any] = {}
        self._available = False

        self._initialize_client()
        self._initialized = True

    def _initialize_client(self):
        """Initialize ChromaDB client with error handling"""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB unavailable - running in memory-only mode")
            return

        try:
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False, allow_reset=True, is_persistent=True
                ),
            )
            self._available = True
            logger.info(f"✅ Unified Vector Store initialized: {self.db_path}")

            # Pre-create standard collections
            self._create_standard_collections()

        except Exception as e:
            msg = str(e)
            # Detect Chroma instance conflict and try graceful fallback
            if "An instance of Chroma already exists" in msg:
                logger.warning(
                    "Chroma instance conflict detected for path '%s' — attempting fallback client",
                    self.db_path,
                )
                try:
                    # fallback to in-memory client to keep system operable
                    self.client = chromadb.Client()
                    self._available = True
                    logger.info(
                        "✅ Vector Store initialized using in-memory Chroma fallback"
                    )
                    self._create_standard_collections()
                    return
                except Exception as e2:
                    logger.error(
                        "Fallback to in-memory Chroma client failed: %s", e2
                    )

            logger.error(f"❌ Vector Store initialization failed: {e}")
            self._available = False
            self.client = None

    def _create_standard_collections(self):
        """Create standard collections for JARVIS"""
        standard_collections = [
            "interactions",  # User conversations and context
            "knowledge",  # Learned knowledge and facts
            "learning",  # Learning experiences and feedback
            "experiences",  # Past experiences and patterns
            "context",  # Contextual information
        ]

        for collection_name in standard_collections:
            try:
                collection = self.client.get_or_create_collection(
                    name=collection_name, metadata={"hnsw:space": "cosine"}
                )
                self.collections[collection_name] = collection
                logger.debug(f"✅ Collection '{collection_name}' ready")
            except Exception as e:
                logger.error(f"❌ Failed to create collection '{collection_name}': {e}")

    def is_available(self) -> bool:
        """Check if vector store is available"""
        return self._available and self.client is not None

    def get_collection(self, name: str):
        """Get or create a collection"""
        if not self.is_available():
            logger.warning(
                f"Vector store unavailable - cannot access collection '{name}'"
            )
            return None

        if name in self.collections:
            return self.collections[name]

        try:
            collection = self.client.get_or_create_collection(
                name=name, metadata={"hnsw:space": "cosine"}
            )
            self.collections[name] = collection
            return collection
        except Exception as e:
            logger.error(f"Failed to get collection '{name}': {e}")
            return None

    def get_client(self):
        """Get ChromaDB client directly (for advanced usage)"""
        return self.client if self.is_available() else None

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on vector store"""
        if not self.is_available():
            return {"status": "unavailable", "error": "ChromaDB client not initialized"}

        try:
            # Test basic operations
            collections_count = len(self.client.list_collections())

            return {
                "status": "healthy",
                "db_path": str(self.db_path),
                "collections_count": collections_count,
                "standard_collections": list(self.collections.keys()),
                "chromadb_available": CHROMADB_AVAILABLE,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                # ChromaDB handles cleanup automatically
                pass
            logger.info("✅ Vector store cleanup completed")
        except Exception as e:
            logger.error(f"Vector store cleanup error: {e}")


# Global instance
_vector_store = None


def get_vector_store() -> UnifiedVectorStore:
    """Get the global unified vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = UnifiedVectorStore()
    return _vector_store


# Convenience functions for backward compatibility
def get_chromadb_client():
    """Get ChromaDB client (backward compatibility)"""
    vs = get_vector_store()
    return vs.get_client()


def get_memory_collection():
    """Get main memory collection (backward compatibility)"""
    vs = get_vector_store()
    return vs.get_collection("interactions")


def get_knowledge_collection():
    """Get knowledge collection (backward compatibility)"""
    vs = get_vector_store()
    return vs.get_collection("knowledge")


if __name__ == "__main__":
    # Test the vector store
    print("🧪 Testing Unified Vector Store")
    print("=" * 50)

    vs = get_vector_store()
    health = vs.health_check()

    print(f"Status: {health['status']}")
    if health["status"] == "healthy":
        print(f"Path: {health['db_path']}")
        print(f"Collections: {health['collections_count']}")
        print(f"Standard collections: {health['standard_collections']}")
    else:
        print(f"Error: {health.get('error', 'Unknown')}")
