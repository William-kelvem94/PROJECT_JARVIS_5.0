"""
Brain - Gemini Client
Cliente real para Google Gemini
"""

import logging
from typing import Optional, List, Dict
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class GeminiClient:
    """Cliente Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.genai = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                logger.info("✅ Gemini Client inicializado")
            except ImportError:
                logger.error("❌ google-generativeai não instalado: pip install google-generativeai")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Gemini: {e}")
        else:
            logger.warning("⚠️ GEMINI_API_KEY não configurada")
    
    def chat(self, prompt: str, model: str = "gemini-1.5-flash") -> Optional[str]:
        """Chat simples"""
        if not self.genai:
            return None
        
        try:
            model_instance = self.genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Erro Gemini: {e}")
            return None
    
    def chat_with_history(self, messages: List[Dict], model: str = "gemini-1.5-flash") -> Optional[str]:
        """Chat com histórico"""
        if not self.genai:
            return None
        
        try:
            model_instance = self.genai.GenerativeModel(model)
            chat = model_instance.start_chat(history=[])
            
            # Converter mensagens para formato Gemini
            for msg in messages[:-1]:  # Histórico
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
            
            # Última mensagem
            last_msg = messages[-1]["content"]
            response = chat.send_message(last_msg)
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Erro Gemini chat: {e}")
            return None
    
    def vision(self, prompt: str, image_path: str, model: str = "gemini-1.5-pro") -> Optional[str]:
        """Análise de imagem"""
        if not self.genai:
            return None
        
        try:
            from PIL import Image
            
            model_instance = self.genai.GenerativeModel(model)
            image = Image.open(image_path)
            
            response = model_instance.generate_content([prompt, image])
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Erro Gemini Vision: {e}")
            return None
    
    def stream_chat(self, prompt: str, model: str = "gemini-1.5-flash"):
        """Chat com streaming"""
        if not self.genai:
            return
        
        try:
            model_instance = self.genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"❌ Erro Gemini stream: {e}")


# Instância global
gemini_client = None

def get_gemini_client(api_key: Optional[str] = None) -> GeminiClient:
    """Retorna instância do cliente"""
    global gemini_client
    
    if not gemini_client:
        gemini_client = GeminiClient(api_key)
    
    return gemini_client
