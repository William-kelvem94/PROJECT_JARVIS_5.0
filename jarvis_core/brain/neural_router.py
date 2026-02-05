"""
Brain - Neural Router
Decide qual LLM usar baseado no contexto
"""

import logging
from typing import Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Tipos de modelos disponíveis"""
    GROQ_FAST = "groq_fast"  # Llama 3 70B - Conversa
    GEMINI_FLASH = "gemini_flash"  # Gemini Flash - Balanceado
    GEMINI_PRO = "gemini_pro"  # Gemini Pro - Profundo
    GEMINI_VISION = "gemini_vision"  # Gemini Vision - Imagens
    LOCAL_QWEN = "local_qwen"  # Qwen local - Privacidade

class NeuralRouter:
    """Router inteligente entre modelos"""
    
    def __init__(self, groq_key: Optional[str] = None, gemini_key: Optional[str] = None):
        self.groq_key = groq_key
        self.gemini_key = gemini_key
        
        # Clients (lazy loading)
        self._groq_client = None
        self._gemini_client = None
        
        # Métricas
        self.metrics = {
            "groq_calls": 0,
            "gemini_calls": 0,
            "local_calls": 0,
            "total_latency": 0
        }
    
    def decide_model(self, prompt: str, context: Optional[Dict] = None) -> ModelType:
        """Decide qual modelo usar"""
        context = context or {}
        
        # 1. Verificar se tem imagem
        if context.get("has_image"):
            logger.info("🖼️ Imagem detectada → Gemini Vision")
            return ModelType.GEMINI_VISION
        
        # 2. Verificar privacidade
        if context.get("privacy_level") == "high":
            logger.info("🔒 Privacidade alta → Qwen local")
            return ModelType.LOCAL_QWEN
        
        # 3. Análise de complexidade
        complexity = self._estimate_complexity(prompt)
        
        if complexity < 0.3:
            # Conversa simples
            logger.info("💬 Conversa simples → Groq (rápido)")
            return ModelType.GROQ_FAST
        elif complexity < 0.7:
            # Balanceado
            logger.info("⚖️ Complexidade média → Gemini Flash")
            return ModelType.GEMINI_FLASH
        else:
            # Profundo
            logger.info("🧠 Alta complexidade → Gemini Pro")
            return ModelType.GEMINI_PRO
    
    def _estimate_complexity(self, prompt: str) -> float:
        """Estima complexidade do prompt (0-1)"""
        complexity = 0.0
        
        # Tamanho
        if len(prompt) > 500:
            complexity += 0.2
        
        # Palavras-chave complexas
        complex_keywords = [
            "analise", "compare", "explique", "detalhe",
            "código", "implementa", "debug", "otimiza",
            "pesquise", "resuma", "traduza"
        ]
        
        for keyword in complex_keywords:
            if keyword in prompt.lower():
                complexity += 0.15
        
        # Perguntas múltiplas
        if prompt.count("?") > 1:
            complexity += 0.2
        
        return min(complexity, 1.0)
    
    async def process(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Processa prompt com modelo apropriado"""
        model_type = self.decide_model(prompt, context)
        
        try:
            if model_type == ModelType.GROQ_FAST:
                return await self._call_groq(prompt)
            elif model_type in [ModelType.GEMINI_FLASH, ModelType.GEMINI_PRO]:
                return await self._call_gemini(prompt, model_type)
            elif model_type == ModelType.GEMINI_VISION:
                image_path = context.get("image_path")
                return await self._call_gemini_vision(prompt, image_path)
            elif model_type == ModelType.LOCAL_QWEN:
                return await self._call_local(prompt)
            else:
                return "Modelo não implementado"
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            return f"Erro: {str(e)}"
    
    async def _call_groq(self, prompt: str) -> str:
        """Chama Groq API"""
        if not self.groq_key:
            return "Groq API key não configurada"
        
        try:
            from jarvis_core.brain.groq_client import get_groq_client
            
            client = get_groq_client(self.groq_key)
            
            if not client.client:
                return "Groq client não disponível"
            
            response = client.chat([{"role": "user", "content": prompt}])
            
            if response:
                self.metrics["groq_calls"] += 1
                return response
            else:
                return "Erro ao chamar Groq"
                
        except Exception as e:
            logger.error(f"❌ Erro Groq: {e}")
            return f"Erro Groq: {str(e)}"
    
    async def _call_gemini(self, prompt: str, model_type: ModelType) -> str:
        """Chama Gemini API"""
        if not self.gemini_key:
            return "Gemini API key não configurada"
        
        try:
            from jarvis_core.brain.gemini_client import get_gemini_client
            
            client = get_gemini_client(self.gemini_key)
            
            if not client.genai:
                return "Gemini client não disponível"
            
            model_name = "gemini-1.5-flash" if model_type == ModelType.GEMINI_FLASH else "gemini-1.5-pro"
            response = client.chat(prompt, model_name)
            
            if response:
                self.metrics["gemini_calls"] += 1
                return response
            else:
                return "Erro ao chamar Gemini"
                
        except Exception as e:
            logger.error(f"❌ Erro Gemini: {e}")
            return f"Erro Gemini: {str(e)}"
    
    async def _call_gemini_vision(self, prompt: str, image_path: str) -> str:
        """Chama Gemini Vision"""
        if not self.gemini_key:
            return "Gemini API key não configurada"
        
        try:
            from jarvis_core.brain.gemini_client import get_gemini_client
            
            client = get_gemini_client(self.gemini_key)
            
            if not client.genai:
                return "Gemini client não disponível"
            
            response = client.vision(prompt, image_path)
            
            if response:
                self.metrics["gemini_calls"] += 1
                return response
            else:
                return "Erro ao chamar Gemini Vision"
                
        except Exception as e:
            logger.error(f"❌ Erro Gemini Vision: {e}")
            return f"Erro Gemini Vision: {str(e)}"
    
    async def _call_local(self, prompt: str) -> str:
        """Chama modelo local (Qwen via Ollama)"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "qwen2.5:0.5b",
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.metrics["local_calls"] += 1
                        return data.get("response", "")
                    else:
                        return "Ollama não está rodando"
        except Exception as e:
            logger.error(f"❌ Erro local: {e}")
            return f"Erro local: {str(e)}"
    
    def get_metrics(self) -> Dict:
        """Retorna métricas de uso"""
        return self.metrics


# Instância global
neural_router = None


def get_router(groq_key: Optional[str] = None, gemini_key: Optional[str] = None) -> NeuralRouter:
    """Retorna instância do router"""
    global neural_router
    
    if not neural_router:
        neural_router = NeuralRouter(groq_key, gemini_key)
    
    return neural_router
