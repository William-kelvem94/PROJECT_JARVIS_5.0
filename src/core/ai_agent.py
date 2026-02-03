"""
Orquestrador do Agente de IA
Gerencia interação entre visão (OCR), decisão (LLM) e ação (PyAutoGUI)
"""

import logging
import os
import requests
import json
from typing import Dict, Any, List, Optional
from src.core.screen_capture import screen_capture
from src.core.action_controller import action_controller
from src.core.voice_controller import voice_controller
from src.core.dataset_collector import dataset_collector
from src.core.neural_memory import neural_memory
from src.utils.config import config

logger = logging.getLogger(__name__)

class AIAgent:
    """Classe principal do Agente Inteligente"""

    def __init__(self, provider: str = 'gemini'):
        self.provider = provider
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Histórico de conversação
        self.chat_history = []
        
        # Persona Jarvis
        self.system_prompt = (
            "Você é o Jarvis, um assistente virtual ultra-inteligente e prestativo, similar ao do Homem de Ferro. "
            "Sua voz é sofisticada, calma e levemente sarcástica quando apropriado, mas sempre leal. "
            "Você tem acesso à tela do usuário e pode realizar ações no sistema (mouse e teclado). "
            "Responda de forma concisa e natural. Se o usuário pedir para fazer algo na tela, "
            "analise a imagem e descreva o que você vai fazer antes de executar (ou apenas descreva se a execução automática estiver desativada). "
            "Trate o usuário de forma respeitosa, mas mantenha a personalidade do Jarvis."
        )

    def process_command(self, user_command: str):
        """
        Recebe um comando (texto ou voz), captura a tela e decide o que fazer
        """
        logger.info(f"Agente processando comando: {user_command}")
        
        # 1. Verificar conexão para fallback automático
        is_online = voice_controller.check_internet()
        current_provider = self.provider if is_online else 'ollama'
        
        # 2. Notificar usuário via voz
        msg = "Entendido. Analisando a tela." if is_online else "Estou offline, senhor. Usando processamento local."
        voice_controller.speak(msg)
        
        # 3. Capturar estado atual da tela
        screenshot_path = screen_capture.capture_fullscreen(capture_type='agent')
        
        # 4. Buscar contexto na memória neural (Lembranças)
        remembered_context = neural_memory.query_context(user_command)
        enriched_command = f"{remembered_context}\nComando atual: {user_command}" if remembered_context else user_command

        # 5. Enviar para a IA
        response = ""
        if current_provider == 'gemini' and self.api_key:
            response = self._call_gemini(enriched_command, screenshot_path)
        else:
            response = self._call_ollama(enriched_command, screenshot_path)

        # 6. Salvar nova interação na memória neural e dataset
        neural_memory.store_interaction(user_command, response)
        dataset_collector.collect(screenshot_path, user_command, response, current_provider)

        # 7. Falar a resposta
        voice_controller.speak(response)
        return response

    def _call_gemini(self, prompt: str, image_path: str):
        """Integração real com Gemini Pro Vision (Free Tier)"""
        if not self.api_key:
            return "Erro: Variável GOOGLE_API_KEY não configurada no sistema."

        try:
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            # Adicionar ao histórico
            self.chat_history.append({"role": "user", "content": prompt})
            
            # Construir mensagens com histórico (simplificado para Gemini Flash)
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in self.chat_history[-5:]])
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"{self.system_prompt}\n\nHistórico recente:\n{history_text}\n\nComando atual: {prompt}"},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            response_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Adicionar resposta ao histórico
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            return response_text

        except Exception as e:
            logger.error(f"Erro ao chamar Gemini: {e}")
            return f"Senhor, tive um problema técnico ao consultar meus servidores: {str(e)}"

    def _call_ollama(self, prompt: str, image_path: str):
        """Integração real com Ollama Local (Llava)"""
        try:
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Tenta usar o modelo Llava para visão local
            payload = {
                "model": "llava",
                "prompt": f"{self.system_prompt}\n\nComando: {prompt}",
                "images": [image_data],
                "stream": False
            }

            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('response', "Senhor, não obtive resposta do processador local.")

        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {e}")
            return f"Infelizmente estou com dificuldades no processamento offline: {str(e)}. Verifique se o Ollama com o modelo LLava está rodando."

# Instância global
ai_agent = AIAgent()
