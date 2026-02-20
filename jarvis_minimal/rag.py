import os
import json
import numpy as np
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SimpleRAG:
    """Simple Vector Search for long-term memory."""
    def __init__(self, storage_path: str = "data/vector_memory.json"):
        self.storage_path = storage_path
        self.entries: List[Dict] = []
        self.embeddings: List[np.ndarray] = []
        self.model = None
        self._load()

    def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except ImportError:
                logger.warning("sentence-transformers não instalado. RAG desativado.")
                return False
        return True

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entries = data.get("entries", [])
                    # convert back to numpy arrays
                    raw_embs = data.get("embeddings", [])
                    self.embeddings = [np.array(e) for e in raw_embs]
            except Exception as e:
                logger.error(f"Erro ao carregar RAG: {e}")

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                data = {
                    "entries": self.entries,
                    "embeddings": [e.tolist() for e in self.embeddings]
                }
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar RAG: {e}")

    def add_entry(self, text: str, metadata: Dict = None):
        if not self._load_model(): return
        
        emb = self.model.encode(text)
        self.entries.append({"text": text, "metadata": metadata or {}})
        self.embeddings.append(emb)
        self.save()

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not self._load_model() or not self.embeddings:
            return []
        
        query_emb = self.model.encode(query)
        # Cosine similarity
        similarities = []
        for emb in self.embeddings:
            norm_q = np.linalg.norm(query_emb)
            norm_e = np.linalg.norm(emb)
            if norm_q > 0 and norm_e > 0:
                sim = np.dot(query_emb, emb) / (norm_q * norm_e)
            else:
                sim = 0
            similarities.append(sim)
        
        # Get top K
        indices = np.argsort(similarities)[-top_k:][::-1]
        results = [self.entries[i]["text"] for i in indices if similarities[i] > 0.3]
        return results

# Global instance
rag = SimpleRAG()
