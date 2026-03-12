import os
import glob
from loguru import logger
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

class CodeMiner:
    """
    O 'Minerador de Código' do Jarvis.
    Indexa o repositório local para permitir consultas semânticas profundas.
    """
    
    def __init__(self, storage_dir: str = "backend/data/index"):
        self.storage_dir = storage_dir
        self.index = None
        os.makedirs(self.storage_dir, exist_ok=True)

    def index_codebase(self, root_dir: str):
        """Varre o projeto e gera o índice vetorial."""
        logger.info(f"[CodeMiner] Indexando repositório em {root_dir}...")
        try:
            # Filtra apenas arquivos relevantes para economizar tokens/espaço
            required_exts = [".py", ".ts", ".tsx", ".md", ".bat", ".ps1"]
            
            documents = SimpleDirectoryReader(
                input_dir=root_dir,
                recursive=True,
                required_exts=required_exts,
                exclude_hidden=True,
                exclude=[".git", "node_modules", "venv", ".next", "dist"]
            ).load_data()
            
            self.index = VectorStoreIndex.from_documents(documents)
            self.index.storage_context.persist(persist_dir=self.storage_dir)
            logger.success(f"[CodeMiner] Indexação concluída: {len(documents)} documentos processados.")
        except Exception as e:
            logger.error(f"[CodeMiner] Falha na indexação: {e}")

    def load_index(self):
        """Carrega o índice persistido."""
        if os.path.exists(os.path.join(self.storage_dir, "vector_store.json")):
            try:
                storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
                self.index = load_index_from_storage(storage_context)
                return True
            except Exception as e:
                logger.error(f"[CodeMiner] Falha ao carregar índice: {e}")
        return False

    def query(self, question: str):
        """Realiza uma busca semântica no código."""
        if not self.index:
            if not self.load_index():
                return "Índice de código não encontrado. Por favor, execute a indexação primeiro."
        
        query_engine = self.index.as_query_engine()
        response = query_engine.query(question)
        return str(response)

# Singleton
code_miner = CodeMiner()
