"""
Sistema RAG - Banco de Dados Vetorial
Armazena e busca informações contextuais para melhorar respostas do LLM
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from core.logger import logger

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB não disponível. Instale com: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers não disponível. Instale com: pip install sentence-transformers")

class VectorStore:
    """
    Banco de dados vetorial para RAG.
    Armazena documentos e permite busca semântica.
    """
    
    def __init__(self, storage_path: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa o banco vetorial.
        
        Args:
            storage_path: Caminho para armazenar dados (padrão: ./data/vector_db)
            model_name: Nome do modelo de embedding
        """
        self.storage_path = Path(storage_path) if storage_path else Path("./data/vector_db")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = None
        self.client = None
        self.collection = None
        
        # Inicializar modelo de embeddings
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(model_name)
                logger.info(f"Modelo de embedding carregado: {model_name}")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo de embedding: {e}")
        else:
            logger.warning("Usando embeddings simples (sem sentence-transformers)")
        
        # Inicializar ChromaDB
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=str(self.storage_path / "chroma"))
                self.collection = self.client.get_or_create_collection(
                    name="jarvis_knowledge",
                    metadata={"description": "Base de conhecimento do JARVIS"}
                )
                logger.info("ChromaDB inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar ChromaDB: {e}")
        else:
            logger.warning("ChromaDB não disponível. Usando armazenamento simples.")
            self._simple_store = []
    
    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Adiciona um documento ao banco vetorial.
        
        Args:
            text: Texto do documento
            metadata: Metadados adicionais
            doc_id: ID opcional do documento
        
        Returns:
            Resultado da operação
        """
        try:
            metadata = metadata or {}
            doc_id = doc_id or f"doc_{len(self._simple_store) if not CHROMADB_AVAILABLE else 0}"
            
            if CHROMADB_AVAILABLE and self.collection:
                # Usar ChromaDB
                if self.embedding_model:
                    embedding = self.embedding_model.encode(text).tolist()
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[text],
                        metadatas=[metadata]
                    )
                else:
                    self.collection.add(
                        ids=[doc_id],
                        documents=[text],
                        metadatas=[metadata]
                    )
            else:
                # Armazenamento simples
                self._simple_store.append({
                    "id": doc_id,
                    "text": text,
                    "metadata": metadata
                })
            
            logger.info(f"Documento adicionado: {doc_id}")
            return {
                "success": True,
                "doc_id": doc_id,
                "result": "Documento adicionado com sucesso!"
            }
        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares à query.
        
        Args:
            query: Query de busca
            n_results: Número de resultados
            min_score: Score mínimo
        
        Returns:
            Lista de documentos encontrados
        """
        try:
            if CHROMADB_AVAILABLE and self.collection:
                if self.embedding_model:
                    # Busca com embeddings
                    query_embedding = self.embedding_model.encode(query).tolist()
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results
                    )
                    
                    documents = []
                    if results['ids'] and len(results['ids'][0]) > 0:
                        for i, doc_id in enumerate(results['ids'][0]):
                            documents.append({
                                "id": doc_id,
                                "text": results['documents'][0][i],
                                "metadata": results['metadatas'][0][i],
                                "distance": results.get('distances', [[]])[0][i] if results.get('distances') else 0
                            })
                    
                    return documents
                else:
                    # Busca semântica simples (busca por palavras-chave)
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=n_results
                    )
                    
                    documents = []
                    if results['ids'] and len(results['ids'][0]) > 0:
                        for i, doc_id in enumerate(results['ids'][0]):
                            documents.append({
                                "id": doc_id,
                                "text": results['documents'][0][i],
                                "metadata": results['metadatas'][0][i]
                            })
                    
                    return documents
            else:
                # Busca simples por palavras-chave
                query_lower = query.lower()
                query_words = query_lower.split()
                
                scored_docs = []
                for doc in self._simple_store:
                    text_lower = doc['text'].lower()
                    score = sum(1 for word in query_words if word in text_lower) / len(query_words) if query_words else 0
                    
                    if score >= min_score:
                        scored_docs.append({
                            **doc,
                            "score": score
                        })
                
                # Ordenar por score
                scored_docs.sort(key=lambda x: x['score'], reverse=True)
                return scored_docs[:n_results]
                
        except Exception as e:
            logger.error(f"Erro ao buscar: {e}")
            return []
    
    def get_context_for_query(self, query: str, max_results: int = 3) -> str:
        """
        Obtém contexto relevante para uma query.
        Retorna texto formatado para injetar no prompt do LLM.
        
        Args:
            query: Query do usuário
            max_results: Número máximo de resultados
        
        Returns:
            Contexto formatado
        """
        results = self.search(query, n_results=max_results)
        
        if not results:
            return ""
        
        context_parts = []
        for i, doc in enumerate(results, 1):
            context_parts.append(f"[Documento {i}]\n{doc['text']}\n")
        
        return "\n".join(context_parts)
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Remove um documento.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            Resultado da operação
        """
        try:
            if CHROMADB_AVAILABLE and self.collection:
                self.collection.delete(ids=[doc_id])
            else:
                self._simple_store = [d for d in self._simple_store if d['id'] != doc_id]
            
            logger.info(f"Documento removido: {doc_id}")
            return {
                "success": True,
                "result": f"Documento {doc_id} removido!"
            }
        except Exception as e:
            logger.error(f"Erro ao remover documento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco vetorial."""
        if CHROMADB_AVAILABLE and self.collection:
            count = self.collection.count()
        else:
            count = len(self._simple_store)
        
        return {
            "document_count": count,
            "storage_path": str(self.storage_path),
            "chromadb_available": CHROMADB_AVAILABLE,
            "embeddings_available": SENTENCE_TRANSFORMERS_AVAILABLE
        }

