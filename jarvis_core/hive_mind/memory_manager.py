"""
Hive Mind - Memory Manager
Gerenciamento de memória híbrida (RAM + ChromaDB)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridMemory:
    """Gerenciador de memória híbrida"""
    
    def __init__(self):
        self.short_term = []  # Lista em RAM
        self.max_short_term = 50  # Máximo antes de resumir
        
        self.memory_file = Path("data/memory/short_term.json")
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ChromaDB (opcional, se instalado)
        self.chroma_client = None
        self.collection = None
        
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path="data/memory/chroma")
            self.collection = self.chroma_client.get_or_create_collection("jarvis_memory")
            logger.info("✅ ChromaDB inicializado")
        except ImportError:
            logger.warning("⚠️ ChromaDB não instalado. Usando apenas memória curta.")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar ChromaDB: {e}")
        
        # Carregar memória existente
        self._load_short_term()
    
    def store_short_term(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Armazena na memória de curto prazo"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.short_term.append(message)
        
        # Auto-summary se atingir limite
        if len(self.short_term) >= self.max_short_term:
            logger.info("📊 Limite de memória curta atingido. Resumindo...")
            self.auto_summary()
        
        # Salvar em disco
        self._save_short_term()
    
    def store_long_term(self, text: str, metadata: Optional[Dict] = None):
        """Armazena na memória de longo prazo (vetorial)"""
        if not self.collection:
            logger.warning("⚠️ ChromaDB não disponível")
            return
        
        try:
            doc_id = f"mem_{datetime.now().timestamp()}"
            
            self.collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            logger.debug(f"✅ Memória longa armazenada: {doc_id}")
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar memória longa: {e}")
    
    def search_memory(self, query: str, n_results: int = 5) -> List[Dict]:
        """Busca semântica na memória"""
        if not self.collection:
            logger.warning("⚠️ ChromaDB não disponível")
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            memories = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return memories
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def auto_summary(self):
        """Resume contexto e move para memória longa"""
        if len(self.short_term) < 10:
            return
        
        # Criar resumo textual
        summary_text = f"Resumo de {len(self.short_term)} interações:\n"
        
        for msg in self.short_term:
            summary_text += f"- {msg['role']}: {msg['content'][:100]}...\n"
        
        # Armazenar resumo na memória longa
        self.store_long_term(
            summary_text,
            metadata={
                "type": "summary",
                "messages_count": len(self.short_term),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Limpar memória curta (manter últimas 10)
        self.short_term = self.short_term[-10:]
        self._save_short_term()
        
        logger.info("✅ Memória resumida e arquivada")
    
    def get_context(self, max_messages: int = 20) -> List[Dict]:
        """Retorna contexto recente"""
        return self.short_term[-max_messages:]
    
    def clear_short_term(self):
        """Limpa memória curta"""
        self.short_term = []
        self._save_short_term()
    
    def _load_short_term(self):
        """Carrega memória curta do disco"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.short_term = json.load(f)
                logger.info(f"✅ Memória carregada: {len(self.short_term)} mensagens")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar memória: {e}")
    
    def _save_short_term(self):
        """Salva memória curta no disco"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.short_term, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar memória: {e}")


# Instância global
hybrid_memory = HybridMemory()
