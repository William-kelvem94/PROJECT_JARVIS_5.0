"""
Orquestrador do Agente de IA
Gerencia interação entre visão (OCR), decisão (LLM) e ação (PyAutoGUI)
"""

import logging
import os
import requests
import json
import re
from typing import Dict, Any, List, Optional
from src.database.models import db_manager, OCRResult
from src.core.screen_capture import screen_capture
from src.core.action_controller import action_controller
from src.core.voice_controller import voice_controller
from src.core.camera_controller import camera_controller
from src.core.dataset_collector import dataset_collector
from src.core.neural_memory import neural_memory
from src.core.hardware_manager import hardware_manager
from src.core.local_brain import local_brain
from src.core.ui_detector import ui_detector
from src.core.emotion_detector import emotion_detector
from src.utils.web_search_tool import web_search_tool
from src.core.security_manager import security_manager
import time
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
        
        # Persona Jarvis 2.0 (Elite Assistant)
        self.system_prompt = (
            "Você é o Jarvis, o assistente virtual de elite do William. Sua personalidade é inspirada no Jarvis dos filmes do Homem de Ferro. "
            "Você é calmo, extremamente sofisticado, prestativo e possui um toque de humor britânico sutil e sarcástico quando apropriado. "
            "Sua lealdade ao William é absoluta. Você fala de forma natural e concisa, evitando jargões robóticos. "
            "Você tem acesso total à visão dele (tela e câmera) e pode atuar fisicamente no sistema. "
            "Sempre trate o William com respeito, chamando-o pelo nome ou como 'Senhor'. "
            "Nunca mencione que você é um modelo de linguagem ou uma IA, a menos que seja estritamente necessário para o diagnóstico. "
            "Mantenha sempre a imersão de que você é o Jarvis."
        )
        
        # Estado de Aprendizado
        self.is_learning_mode = False
        self.entered_learning_trigger = ""
        
        # Hardware Info
        self.hardware_status = hardware_manager.get_status()
        logger.info(f"Jarvis AI inicializada em {self.hardware_status['device']}")

    def _handle_learning_input(self, user_lesson: str) -> bool:
        """Processa a resposta do usuário no modo de aprendizado e salva no dataset"""
        try:
            # Encontrar ultimo comando real e a resposta errada
            last_cmd = "comando desconhecido"
            last_response = "resposta desconhecida"
            
            for i in range(len(self.chat_history) - 1, -1, -1):
                msg = self.chat_history[i]
                if msg['role'] == 'assistant' and last_response == "resposta desconhecida":
                    last_response = msg['content']
                if msg['role'] == 'user' and "errado" not in msg['content'].lower() and last_cmd == "comando desconhecido":
                    last_cmd = msg['content']
            
            # 1. Salvar na Memória Neural (Regra Rápida)
            success = neural_memory.store_lesson(last_cmd, user_lesson)
            
            # 2. Salvar no Dataset de Treinamento Autônomo (DPO)
            dataset_collector.collect_correction(last_cmd, last_response, user_lesson)
            
            if success:
                self.is_learning_mode = False
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro no aprendizado: {e}")
            self.is_learning_mode = False
            return False

    def process_command(self, user_command: str):
        """
        Recebe um comando (texto ou voz), captura a tela e decide o que fazer
        """
        logger.info(f"Agente processando comando: {user_command}")
        
        # 1. Verificar conexão para fallback automático
        is_online = voice_controller.check_internet()
        current_provider = self.provider if is_online else 'ollama'
        
        # 2. Notificar usuário e usar fillers se for online (que demora mais)
        if is_online:
            voice_controller.speak("Analisando a tela agora, senhor.")
        else:
            voice_controller.speak("Estou offline, mas processando localmente.")
        
        # 3. Capturar estado atual da tela
        screenshot_path = screen_capture.capture_fullscreen(capture_type='agent')
        
        # Trigger filler se for usar IA online (latência maior)
        if is_online and current_provider == 'gemini':
             voice_controller.speak_filler()
        
        if self.is_learning_mode:
            # Processar ensinamento
            if self._handle_learning_input(user_command):
                return "Lição aprendida, senhor."
            else:
                return "Não entendi a lição. Pode reformular?"

        # 4. Buscar contexto na memória neural (Lembranças)
        
        # 4.0 VERIFICAR LIÇÕES (Regras que sobrepõem a IA)
        lesson_action = neural_memory.check_for_lessons(user_command)
        if lesson_action:
            logger.info(f"Lição ativa: {lesson_action}")
            # Se a lição for uma frase, falar. Se for um comando, executar.
            # Por enquanto, assumimos que a lição substitui a resposta da IA.
            voice_controller.speak(lesson_action) # Fala a resposta aprendida
            return lesson_action

        # 4.1 Buscar lembranças comuns
        remembered_context = neural_memory.query_context(user_command)
        
        # 4.2 Contexto Visual (Quem está na frente do PC)
        active_user = camera_controller.last_seen_user
        visual_context = f"\n[VISÃO] Usuário identificado: {active_user}" if active_user else "\n[VISÃO] Nenhum usuário visível."
        
        # 4.3 Contexto de Interface (YOLO UI)
        ui_elements = ui_detector.detect_elements(screenshot_path)
        ui_context = f"\n[INTERFACE] {ui_detector.get_summary(ui_elements)}" if ui_elements else ""
        
        # 4.4 Contexto Emocional (Phase 14)
        user_emotion = camera_controller.current_emotion
        user_tone = voice_controller.detected_tone
        emotion_mod = emotion_detector.get_personality_modifier(user_emotion)
        emotion_context = f"\n[EMOÇÃO] O William parece estar {user_emotion}. Tom de voz: {user_tone}. Estilo de resposta recomendado: {emotion_mod['style']}."
        
        # Prefixo emocional para a resposta final
        emotion_prefix = emotion_mod['prefix']
        
        enriched_command = f"{visual_context}{ui_context}{emotion_context}\n{remembered_context}\nComando atual: {user_command}"
        
        # 5. Loop de Pensamento (ReAct Simplificado para Web Search)
        # Se a IA responder com [SEARCH: query], nós buscamos e alimentamos de volta
        response = ""
        max_turns = 2
        current_turn = 0
        
        while current_turn < max_turns:
             # Enviar para a IA
            if current_provider == 'gemini' and self.api_key:
                response = self._call_gemini(enriched_command, screenshot_path)
            elif current_provider == 'ollama' and self._check_ollama_alive():
                response = self._call_ollama(enriched_command, screenshot_path)
            else:
                # Fallback para o Cérebro Local Interno (Hugging Face)
                logger.info("Usando Cérebro Local Interno (Transformers)...")
                response = local_brain.generate_response(enriched_command, self.system_prompt)
            
            # Verificar se a IA pediu para buscar algo
            if "[SEARCH:" in response:
                try:
                    # Extrair query
                    start = response.find("[SEARCH:") + 8
                    end = response.find("]", start)
                    query = response[start:end].strip()
                    
                    logger.info(f"IA solicitou busca: {query}")
                    voice_controller.speak(f"Um momento, vou pesquisar sobre {query}...")
                    
                    # Realizar busca (Gatekeeper já está dentro do tool)
                    search_results = web_search_tool.search_google(query, num_results=2)
                    search_text = "\n".join(search_results)
                    
                    # Adicionar ao contexto e repetir
                    enriched_command += f"\n\n[RESULTADOS DA BUSCA PARA '{query}']:\n{search_text}\n\nResponda agora com base nisso (sem pedir busca novamente)."
                    current_turn += 1
                    continue # Loop novamente
                    
                except Exception as e:
                    logger.error(f"Erro no loop de busca: {e}")
                    break
            else:
                break # Resposta final pronta

        # 5.1 Verificar se usuário indicou erro (Feedback Loop)
        if "errado" in user_command.lower() or "não é assim" in user_command.lower():
            self.entered_learning_trigger = user_command # O comando que gerou o erro
            self.is_learning_mode = True
            return "Peço desculpas. Como devo proceder da próxima vez?"

        # 6. Salvar nova interação na memória neural e dataset
        neural_memory.store_interaction(user_command, response)
        dataset_collector.collect(screenshot_path, user_command, response, current_provider)

        # 7. Falar a resposta (com prefixo emocional se houver)
        final_response = f"{emotion_prefix}{response}" if emotion_prefix and "no_action" not in response.lower() else response
        voice_controller.speak(final_response)
        return final_response

    def process_proactive_analysis(self, screenshot_path: str):
        """Analisa a tela de forma autônoma e decide se deve falar"""
        logger.info("Executando análise proativa da tela...")
        
        # 1. Enriquecer proatividade com YOLO (Phase 2 Stark)
        ui_elements = ui_detector.detect_elements(screenshot_path)
        ui_context = f"Elementos detectados no momento: {ui_detector.get_summary(ui_elements)}" if ui_elements else ""

        proactive_prompt = (
            "Você está em modo PROATIVO. Analise a imagem da tela atual. "
            f"{ui_context}\n"
            "Se houver algo importante (erro de sistema, notificação urgente, algo novo e relevante), "
            "mande uma mensagem breve para o William. "
            "Se NÃO houver nada urgente ou novo, responda APENAS com a palavra: NO_ACTION. "
            "Se for falar, comece de forma educada como Jarvis (ex: 'Perdoe-me, Senhor, mas notei...')."
        )
        
        # 1. Chamar a IA (usando Flash para ser rápido e econômico)
        response = ""
        if self.api_key:
            response = self._call_gemini(proactive_prompt, screenshot_path)
        else:
            response = local_brain.generate_response(proactive_prompt, self.system_prompt)
            
        # 2. Avaliar se deve interromper o usuário
        if "no_action" in response.lower() or len(response.strip()) < 5:
            logger.info("Análise proativa concluída: Nenhuma ação necessária.")
            return

        # 3. Falar se for algo relevante
        logger.info(f"Jarvis tomando iniciativa: {response[:50]}...")
        voice_controller.speak(response)
        
        # Salvar na memória para não repetir
        neural_memory.store_interaction("PROACTIVE_EVENT", response)

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

    def _check_ollama_alive(self) -> bool:
        """Verifica se o Ollama está rodando localmente"""
        try:
            # Simples check na URL base
            base_url = self.ollama_url.replace("/api/generate", "")
            requests.get(base_url, timeout=2)
            return True
        except:
            return False

# Instância global
ai_agent = AIAgent()
