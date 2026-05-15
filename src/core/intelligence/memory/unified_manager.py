from typing import Any, Dict

try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None

class UnifiedMemoryManager:
    def __init__(self):
        self.prompt_cache = {}
        self.short_term = []
        try:
            if chromadb is None:
                raise RuntimeError("chromadb is unavailable")
            self.client = chromadb.Client()
            self.interactions = self.client.create_collection(name="interactions", get_or_create=True)
        except Exception:
            self.interactions = None

    def store_interaction(self, command: str, response: str, metadata: Dict[str, Any]):
        if self.interactions:
            self.interactions.add(
                documents=[f"User: {command}\nJARVIS: {response}"],
                metadatas=[metadata],
                ids=[str(hash(command + response))]
            )

    def get_context(self, query: str, n: int = 3) -> str:
        if not self.interactions:
            return ""
        results = self.interactions.query(query_texts=[query], n_results=n)
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs)
