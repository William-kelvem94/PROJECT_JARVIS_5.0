"""
Backward-compatible adapter module for legacy imports.

Replaces the old `src.core.intelligence.memory_manager` and
`src.core.intelligence.memory.unified_manager` modules.
Canonical implementation is `backend.app.unified_memory.UnifiedMemory`.
"""

from typing import Any, Dict, List

try:
    import chromadb
except Exception:
    chromadb = None


class UnifiedMemoryManager:
    """Simple ChromaDB wrapper (legacy)."""
    def __init__(self):
        self.prompt_cache: Dict[str, Any] = {}
        self.short_term: List[Any] = []
        try:
            if chromadb is None:
                raise RuntimeError("chromadb is unavailable")
            self.client = chromadb.Client()
            self.interactions = self.client.create_collection(
                name="interactions", get_or_create=True
            )
        except Exception:
            self.interactions = None

    def store_interaction(
        self, command: str, response: str, metadata: Dict[str, Any]
    ):
        if self.interactions:
            self.interactions.add(
                documents=[f"User: {command}\nJARVIS: {response}"],
                metadatas=[metadata],
                ids=[str(hash(command + response))],
            )

    def get_context(self, query: str, n: int = 3) -> str:
        if not self.interactions:
            return ""
        results = self.interactions.query(query_texts=[query], n_results=n)
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs)


class MemoryManagerAdapter:
    """Backward-compatible adapter wrapping UnifiedMemoryManager."""
    def __init__(self):
        self._manager = UnifiedMemoryManager()

    @property
    def collection(self):
        return self._manager.interactions

    def get_stats(self) -> Dict[str, Any]:
        total_memories = self.collection.count() if self.collection else 0
        return {
            "total_memories": total_memories,
            "cache_size": len(self._manager.prompt_cache),
            "short_term_size": len(self._manager.short_term),
            "chromadb_available": self.collection is not None,
        }

    def remember(
        self, command: str, response: str, metadata: Dict[str, Any] = None
    ) -> bool:
        self._manager.store_interaction(command, response, metadata or {})
        return True

    def recall(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.collection:
            return []

        result = self.collection.query(query_texts=[query], n_results=top_k)
        docs = result.get("documents", [[]])[0]
        distances = result.get("distances", [[]])[0]

        memories = []
        for idx, doc in enumerate(docs):
            lines = str(doc).splitlines()
            command = lines[0].replace("User: ", "") if lines else ""
            similarity = 0.0
            if idx < len(distances) and distances[idx] is not None:
                similarity = max(0.0, 1.0 - float(distances[idx]))
            memories.append({"command": command, "text": doc, "similarity": similarity})

        return memories

    def get_context(self, query: str, max_memories: int = 3) -> str:
        return self._manager.get_context(query, n=max_memories)


memory_manager = MemoryManagerAdapter()

__all__ = ["UnifiedMemoryManager", "MemoryManagerAdapter", "memory_manager"]
