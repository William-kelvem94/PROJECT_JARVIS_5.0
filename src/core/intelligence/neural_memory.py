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

# ============ P1: RAG UPGRADE (Jina Embeddings v3) ============
try:
    # Jina Embeddings v3 - Superior multilingual performance
    JINA_AVAILABLE = True
except:
    JINA_AVAILABLE = False

logger = logging.getLogger(__name__)

class NeuralMemory:
    """Classe que gerencia a memória de longo prazo do Jarvis usando vetores"""

    def __init__(self):
        global NEURAL_AVAILABLE
        if not NEURAL_AVAILABLE:
            logger.warning("Bibliotecas neurais (sentence-transformers/chromadb) não instaladas. Memória desativada.")
            return

        self.db_path = Path(config.get_setting('app.data_dir', 'data')) / 'neural_memory'
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # ============ P1: RAG UPGRADE (MiniLM for Fast Boot) ============
        # We use MiniLM as primary for instant boot on CPU
        # Jina v3 is kept as an optional high-precision upgrade
        try:
            logger.info("Loading MiniLM (Fast Boot, 384-dim)...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ MiniLM loaded (Instant Boot)")
        except Exception as e:
            logger.warning(f"MiniLM failed, attempting Jina v3: {e}")
            try:
                self.model = SentenceTransformer('jinaai/jina-embeddings-v3', trust_remote_code=True)
            except:
                logger.error("❌ All embedding models failed!")
                NEURAL_AVAILABLE = False
                return
        
        # Inicializar banco de vetores com Self-Healing
        try:
            from chromadb.config import Settings
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            self._init_collections()
        except Exception as e:
            logger.error(f"❌ Erro crítico no ChromaDB (pode ser corrupção de esquema): {e}")
            logger.info("🔄 Tentando auto-cura: Resetando banco de dados neural...")
            
            try:
                import shutil
                # Backup corrupt DB for safety
                backup_path = self.db_path.parent / f"neural_memory_corrupt_{int(datetime.now().timestamp())}"
                if self.db_path.exists():
                    shutil.move(str(self.db_path), str(backup_path))
                
                self.db_path.mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=str(self.db_path),
                    settings=Settings(anonymized_telemetry=False)
                )
                self._init_collections()
                logger.info("✅ Auto-cura concluída. Banco resetado.")
            except Exception as e2:
                logger.error(f"❌ Falha crítica na auto-cura: {e2}")
                NEURAL_AVAILABLE = False

    def _init_collections(self):
        """Inicializa as coleções do ChromaDB"""
        self.collection = self.client.get_or_create_collection(
            name="jarvis_interactions",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Coleção de CONHECIMENTO (RAG - Código, Documentos)
        self.knowledge_collection = self.client.get_or_create_collection(
            name="jarvis_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Coleção de LIÇÕES (Regras explícitas que o usuário ensinou)
        self.lessons_collection = self.client.get_or_create_collection(
            name="jarvis_lessons",
            metadata={"hnsw:space": "cosine"}
        )

    def is_empty(self) -> bool:
        """Verifica se a memória está vazia"""
        if not NEURAL_AVAILABLE: return True
        return self.collection.count() == 0 and self.lessons_collection.count() == 0

    def store_bulk_interactions(self, interactions: List[Dict[str, str]]):
        """Armazena múltiplas interações de uma vez"""
        if not NEURAL_AVAILABLE or not interactions: return
        
        try:
            ids = [f"seed_{i}_{int(datetime.now().timestamp())}" for i in range(len(interactions))]
            texts = [f"User: {int_data['prompt']}\nJarvis: {int_data['response']}" for int_data in interactions]
            embeddings = self.model.encode([int_data['prompt'] for int_data in interactions]).tolist()
            metadatas = [{"source": "seed", "timestamp": datetime.now().isoformat()} for _ in interactions]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"Semeadas {len(interactions)} interações na memória.")
        except Exception as e:
            logger.error(f"Erro no seeding em lote: {e}")

    def store_lesson(self, trigger: str, action: str):
        """Armazena uma regra explicita (Lição)"""
        if not NEURAL_AVAILABLE: return
        
        try:
            lesson_id = f"lesson_{int(datetime.now().timestamp())}"
            embedding = self.model.encode(trigger).tolist()
            
            self.lessons_collection.add(
                ids=[lesson_id],
                embeddings=[embedding],
                documents=[f"Quando usuário disser: '{trigger}' -> Ação: '{action}'"],
                metadatas=[{"trigger": trigger, "action": action, "timestamp": datetime.now().isoformat()}]
            )
            logger.info(f"Lição aprendida: {trigger} -> {action}")
            return True
        except Exception as e:
            logger.error(f"Erro ao aprender lição: {e}")
            return False

    def check_for_lessons(self, command: str, threshold: float = 0.85) -> Optional[str]:
        """
        Verifica se existe uma lição específica para este comando.
        Retorna a ação definida se encontrar correspondência alta.
        """
        if not NEURAL_AVAILABLE: return None
        
        try:
            query_embedding = self.model.encode(command).tolist()
            results = self.lessons_collection.query(
                query_embeddings=[query_embedding],
                n_results=1
            )
            
            if results['ids'] and results['distances'][0]:
                # Chroma retorna distância (0 = identico). Converter para similaridade se necessário ou usar threshold de distancia.
                # Default space is cosine distance. 0.0 is identical, 1.0 is opposite.
                # Se distance < 0.2 (muito parecido)
                distance = results['distances'][0][0]
                
                if distance < (1 - threshold): # Aproximação
                    action = results['metadatas'][0][0].get('action')
                    logger.info(f"Lição aplicada! Comando '{command}' acionou regra '{action}' (Dist: {distance:.4f})")
                    return action
            
            return None
        except Exception as e:
            logger.error(f"Erro ao verificar lições: {e}")
            return None

    def get_all_lessons(self) -> List[Dict]:
        """Retorna todas as lições aprendidas"""
        if not NEURAL_AVAILABLE: return []
        try:
            results = self.lessons_collection.get()
            lessons = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    lessons.append({
                        'id': results['ids'][i],
                        'trigger': results['metadatas'][i].get('trigger'),
                        'action': results['metadatas'][i].get('action'),
                        'timestamp': results['metadatas'][i].get('timestamp')
                    })
            return sorted(lessons, key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            logger.error(f"Erro ao buscar lições: {e}")
            return []

    def delete_lesson(self, lesson_id: str) -> bool:
        """Remove uma lição específica"""
        if not NEURAL_AVAILABLE: return False
        try:
            self.lessons_collection.delete(ids=[lesson_id])
            logger.info(f"Lição removida: {lesson_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover lição: {e}")
            return False

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
            
            # 1. Buscar nas interações passadas
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # 2. Buscar no conhecimento indexado (RAG)
            knowledge_results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            context_parts = []
            
            if results['documents'] and results['documents'][0]:
                context_parts.append("\n[INTERAÇÕES PASSADAS]\n" + "\n---\n".join(results['documents'][0]))
            
            if knowledge_results['documents'] and knowledge_results['documents'][0]:
                context_parts.append("\n[CONHECIMENTO INDEXADO (RAG)]\n" + "\n---\n".join(knowledge_results['documents'][0]))
                
            if context_parts:
                return "\nLembranças e Conhecimento Relevante:\n" + "\n".join(context_parts) + "\n"
            
            return ""
        except Exception as e:
            logger.error(f"Erro ao consultar memória neural: {e}")
            return ""

    def store_knowledge(self, source: str, content: str, metadata: Optional[Dict] = None):
        """Armazena um fragmento de conhecimento no RAG"""
        if not NEURAL_AVAILABLE: return
        
        try:
            item_id = f"kn_{hash(source + content) % 10**8}_{int(datetime.now().timestamp())}"
            embedding = self.model.encode(content).tolist()
            
            self.knowledge_collection.add(
                ids=[item_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {"source": source, "timestamp": datetime.now().isoformat()}]
            )
            logger.debug(f"Conhecimento indexado: {source}")
        except Exception as e:
            logger.error(f"Erro ao armazenar conhecimento: {e}")

# Instância global
neural_memory = NeuralMemory()
