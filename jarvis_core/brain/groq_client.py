"""
Brain - Groq Client
Cliente real para Groq API
"""

import logging
from typing import Optional, List, Dict
import os

logger = logging.getLogger(__name__)

class GroqClient:
    """Cliente Groq API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info("✅ Groq Client inicializado")
            except ImportError:
                logger.error("❌ groq package não instalado: pip install groq")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Groq: {e}")
        else:
            logger.warning("⚠️ GROQ_API_KEY não configurada")
    
    def chat(self, messages: List[Dict], model: str = "llama3-70b-8192", 
             temperature: float = 0.7, max_tokens: int = 1024) -> Optional[str]:
        """Chat completion"""
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Erro Groq: {e}")
            return None
    
    def stream_chat(self, messages: List[Dict], model: str = "llama3-70b-8192"):
        """Chat com streaming"""
        if not self.client:
            return
        
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Erro Groq stream: {e}")


# Instância global
groq_client = None

def get_groq_client(api_key: Optional[str] = None) -> GroqClient:
    """Retorna instância do cliente"""
    global groq_client
    
    if not groq_client:
        groq_client = GroqClient(api_key)
    
    return groq_client
