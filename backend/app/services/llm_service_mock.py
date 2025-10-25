"""Mock LLM Service - Funciona sem Ollama"""
from typing import List, Dict, Any, AsyncIterator, Optional
import asyncio

class LLMService:
    def __init__(self):
        self.initialized = False
        self.default_model = "demo-mode"
        self.available_models = ["demo-mode"]
    
    async def initialize(self):
        await asyncio.sleep(0.1)
        self.initialized = True
    
    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        await asyncio.sleep(0.3)
        return f"🤖 [MODO DEMO] Recebi sua mensagem: '{prompt[:100]}...'\n\n⚠️ Para usar IA real, instale o Ollama!\n\n🔗 Download: https://ollama.ai/download"
    
    async def generate_stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        mensagem = f"🤖 Olá! Recebi: '{prompt[:60]}...' Para IA real instale Ollama em https://ollama.ai"
        for palavra in mensagem.split():
            yield palavra + " "
            await asyncio.sleep(0.05)
    
    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        ultima = messages[-1]['content'] if messages else "..."
        await asyncio.sleep(0.3)
        return f"🤖 Entendi sua mensagem: '{ultima[:80]}...'\n\n⚠️ Estou em MODO DEMO (respostas simuladas)\n\n✅ Para IA real: https://ollama.ai/download"
    
    async def chat_stream(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        ultima = messages[-1]['content'] if messages else "..."
        resposta = f"🤖 Sua pergunta: '{ultima[:50]}...' | MODO DEMO - Instale Ollama para IA real!"
        for palavra in resposta.split():
            yield palavra + " "
            await asyncio.sleep(0.08)
    
    async def get_embeddings(self, text: str, model: str = "demo") -> List[float]:
        return [0.1, 0.2, 0.3]
    
    async def list_models(self) -> List[Dict[str, Any]]:
        return [{"name": "demo-mode", "size": 0, "modified_at": "2025-01-01"}]
    
    async def delete_model(self, model_name: str):
        pass
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        return {"name": model_name, "size": 0, "details": "Demo mode"}
    
    async def pull_model(self, model_name: str):
        await asyncio.sleep(0.1)

_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

