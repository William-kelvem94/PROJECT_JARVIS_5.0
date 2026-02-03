"""
Memória Neural Semântica (Cérebro do Jarvis)
Utiliza Vector DB para busca semântica de interações passadas.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.utils.config import config

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False

logger = logging.getLogger(__name__)

class NeuralMemory:
    """Classe que gerencia a memória de longo prazo do Jarvis usando vetores"""

    def __init__(self):
        if not NEURAL_AVAILABLE:
            logger.warning("Bibliotecas neurais (sentence-transformers/chromadb) não instaladas. Memória desativada.")
            return

        self.db_path = Path(config.get_setting('app.data_dir', 'data')) / 'neural_memory'
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar modelo de embeddigs (pequeno e rápido para rodar local)
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Inicializar banco de vetores
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection = self.client.get_or_create_collection(
            name="jarvis_interactions",
            metadata={"hnsw:space": "cosine"}
        )

    def store_interaction(self, prompt: str, response: str, metadata: Optional[Dict] = None):
        """Armazena uma interação na memória neural"""
        if not NEURAL_AVAILABLE: return

        try:
            interaction_id = f"int_{int(datetime.now().timestamp())}"
            embedding = self.model.encode(prompt).tolist()
            
            self.collection.add(
                ids=[interaction_id],
                embeddings=[embedding],
                documents=[f"User: {prompt}\nJarvis: {response}"],
                metadatas=[metadata or {"timestamp": datetime.now().isoformat()}]
            )
            logger.info(f"Interação neural armazenada: {interaction_id}")
        except Exception as e:
            logger.error(f"Erro ao armazenar interação neural: {e}")

    def query_context(self, current_prompt: str, n_results: int = 3) -> str:
        """Busca na memória neural por contextos parecidos"""
        if not NEURAL_AVAILABLE: return ""

        try:
            query_embedding = self.model.encode(current_prompt).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                context = "\n---\n".join(results['documents'][0])
                return f"\nLembranças de interações passadas:\n{context}\n"
            return ""
        except Exception as e:
            logger.error(f"Erro ao consultar memória neural: {e}")
            return ""

# Instância global
neural_memory = NeuralMemory()
