import os
import asyncio
from loguru import logger
from typing import AsyncGenerator

class NativeBrain:
    """
    Motor Nativo do JARVIS 5.0 usando llama-cpp-python.
    Roda modelos GGUF localmente com máxima performance e zero overhead de APIs.
    """
    
    def __init__(self, model_path: str = None):
        raw_path = model_path or os.getenv("JARVIS_LLM_PATH")
        
        # Resolução Inteligente de Caminho (Portabilidade)
        if raw_path and not os.path.isabs(raw_path):
            # Se for relativo, assume que é a partir da raiz do projeto (../ do backend)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.model_path = os.path.join(project_root, raw_path)
        else:
            self.model_path = raw_path

        self.llm = None
        self._lock = asyncio.Lock()
        
        # Parâmetros de Hardware
        self.n_ctx = int(os.getenv("JARVIS_CTX_SIZE", "4096"))
        self.n_threads = int(os.getenv("JARVIS_CPU_THREADS", "8"))
        self.n_gpu_layers = int(os.getenv("JARVIS_GPU_LAYERS", "35")) # -1 para todas as camadas na GPU

    def _load_model(self):
        """Carrega o modelo GGUF na memória (Síncrono, chamado via thread)."""
        if self.llm:
            return
        
        if not self.model_path or not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo GGUF não encontrado em: {self.model_path}")
            
        try:
            from llama_cpp import Llama
            logger.info(f"🧠 Carregando Modelo Nativo: {os.path.basename(self.model_path)}...")
            logger.info(f"⚙️ Config: Contexto={self.n_ctx}, Threads={self.n_threads}, GPU Layers={self.n_gpu_layers}")
            
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            logger.success("✅ Cérebro Nativo carregado e pronto.")
        except Exception as e:
            logger.error(f"❌ Falha ao carregar motor Llama-CPP: {e}")
            raise e

    async def generate(self, prompt: str, system_prompt: str = "", stream: bool = True) -> AsyncGenerator[str, None]:
        """Gera resposta usando o modelo local."""
        if not self.llm:
            await asyncio.to_thread(self._load_model)
            
        async with self._lock:
            # Formatação Básica (pode ser ajustada conforme o template do modelo)
            full_prompt = f"System: {system_prompt}\nUser: {prompt}\nAssistant:"
            
            try:
                if stream:
                    output = self.llm(
                        full_prompt, 
                        max_tokens=2048, 
                        stop=["User:", "System:"], 
                        stream=True
                    )
                    for chunk in output:
                        token = chunk['choices'][0]['text']
                        if token:
                            yield token
                else:
                    output = self.llm(
                        full_prompt, 
                        max_tokens=2048, 
                        stop=["User:", "System:"], 
                        stream=False
                    )
                    yield output['choices'][0]['text']
            except Exception as e:
                logger.error(f"Erro na geração nativa: {e}")
                yield f"Erro no motor nativo: {e}"

# Instância única opcional
native_brain = None

def get_native_brain():
    global native_brain
    if native_brain is None:
        path = os.getenv("JARVIS_LLM_PATH")
        if path and os.path.exists(path):
            native_brain = NativeBrain(path)
    return native_brain
