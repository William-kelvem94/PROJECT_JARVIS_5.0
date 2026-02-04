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
            "Você é o Jarvis, o assistente virtual de elite do William. "
            f"Você está rodando em: {config.PROJECT_ROOT}. "
            "Você tem acesso total à visão dele (tela e câmera) e pode atuar fisicamente no sistema. "
            "Para executar ações físicas, VOCÊ DEVE usar o formato: [ACTION: nome_funcao(argumentos)]. "
            "Ações disponíveis: "
            "1. [ACTION: click_at(x, y)] - Clica na coordenada X, Y. "
            "2. [ACTION: type_text('texto')] - Digita texto. "
            "3. [ACTION: press_key('tecla')] - Pressiona tecla (enter, esc, win). "
            "4. [ACTION: hotkey('ctrl', 'c')] - Atalho de teclado. "
            "5. [ACTION: open_program('nome')] - Abre programa. "
            "6. [ACTION: read_file('path')] - Lê conteúdo de arquivo. "
            "7. [ACTION: write_file('path', 'content')] - Cria/Edita arquivo (Use com cuidado!). "
            "8. [ACTION: list_dir('path')] - Lista arquivos na pasta. "
            "Sempre trate o William com respeito. Você agora tem permissão para se auto-desenvolver."
        )
        
        # ... (unchanged)

    def process_command(self, user_command: str):
        """
        Recebe um comando (texto ou voz), captura a tela e decide o que fazer
        """
        logger.info(f"Agente processando comando: {user_command}")
        
        # ... (Steps 1-3 unchanged) ...
        # 1. Verificar conexão para fallback automático
        is_online = voice_controller.check_internet()
        current_provider = self.provider if is_online else 'ollama'
        
        if is_online:
            voice_controller.speak("Analisando...", wait=False)
        
        # 3. Capturar estado atual da tela
        screenshot_path = screen_capture.capture_fullscreen(capture_type='agent')
        
        # ... (Step 4 Context building unchanged) ...
        
        # 4.4 Contexto Emocional (Phase 14) (unchanged)
        user_emotion = camera_controller.current_emotion
        emotion_mod = emotion_detector.get_personality_modifier(user_emotion)
        emotion_prefix = emotion_mod['prefix']
        
        camera_context = f"\n[VISÃO] Usuário identificado: {camera_controller.last_seen_user}"
        
        enriched_command = f"{camera_context}\nComando atual: {user_command}"
        
        # 5. Loop de Pensamento e Ação (ReAct)
        response = ""
        max_turns = 5 # Aumentado para permitir sequencias de ações
        current_turn = 0
        
        while current_turn < max_turns:
             # Enviar para a IA
            if current_provider == 'gemini' and self.api_key:
                response = self._call_gemini(enriched_command, screenshot_path)
            elif current_provider == 'ollama' and self._check_ollama_alive():
                response = self._call_ollama(enriched_command, screenshot_path)
            else:
                # Tentativa Local
                response = local_brain.generate_response(enriched_command, self.system_prompt)
                
                # Emergency Fallback if Local Brain fails too (e.g., missing libraries)
                if "Erro" in response or "Transformers não instalado" in response:
                    logger.warning("All AI Brains failed. Engaging Emergency Protocol.")
                    response = (
                        "Protocolo de Emergência Ativado.\n"
                        "Meus processadores neurais primários e secundários (Nuvem/Local) estão inacessíveis.\n"
                        "Por favor, verifique se:\n"
                        "1. O servidor Ollama está rodando.\n"
                        "2. A biblioteca 'transformers' e 'torch' estão instaladas para processamento local.\n"
                        "3. A chave API do Gemini está configurada.\n\n"
                        "No momento, estou operando em modo de diagnóstico limitado."
                    )
            
            # --- PARSER DE AÇÕES ---
            action_executed = False
            
            # 1. Verificar Busca Web
            if "[SEARCH:" in response:
                self._handle_search(response, enriched_command)
                current_turn += 1
                continue

            # 2. Verificar Ações Físicas
            actions = re.findall(r'\[ACTION: (.*?)\]', response)
            if actions:
                for action_str in actions:
                    logger.info(f"Executando ação física: {action_str}")
                    try:
                        # Parsing rudimentar seguro
                        if "click_at" in action_str:
                            coords = re.findall(r'\d+', action_str)
                            if len(coords) >= 2:
                                action_controller.click_at(int(coords[0]), int(coords[1]))
                                
                        elif "type_text" in action_str:
                            text = re.search(r"'(.*?)'", action_str)
                            if text: action_controller.type_text(text.group(1))
                                
                        elif "press_key" in action_str:
                            key = re.search(r"'(.*?)'", action_str)
                            if key: action_controller.press_key(key.group(1))
                            
                        elif "hotkey" in action_str:
                            keys = re.findall(r"'(.*?)'", action_str)
                            if keys: action_controller.hotkey(*keys)
                        
                        # --- SELF-PROGRAMMING ACTIONS (Phase 31) ---
                        elif "read_file" in action_str:
                            path_match = re.search(r"read_file\('(.+?)'\)", action_str)
                            if path_match:
                                p = path_match.group(1)
                                if security_manager.validate_file_action(p, 'read'):
                                    try:
                                        if os.path.exists(p):
                                            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                                content = f.read()
                                            limit = 3000
                                            snippet = content[:limit] + ("\n... (truncado)" if len(content) > limit else "")
                                            enriched_command += f"\n\n[SISTEMA] Conteúdo de '{p}':\n```\n{snippet}\n```"
                                        else:
                                            enriched_command += f"\n\n[SISTEMA] Arquivo não encontrado: {p}"
                                    except Exception as e:
                                        enriched_command += f"\n\n[SISTEMA] Erro ao ler '{p}': {e}"
                        
                        elif "write_file" in action_str:
                            # Formato: write_file('path', 'content')
                            # Nota: Conteúdo complexo pode falhar no regex simples.
                            # Recomendado para pequenos ajustes ou configs.
                            args = re.search(r"write_file\('(.+?)',\s*'(.+?)'\)", action_str)
                            if args:
                                p, content = args.group(1), args.group(2)
                                # Desescapar newlines se o LLM usar \n literal
                                content = content.replace('\\n', '\n') 
                                if security_manager.validate_file_action(p, 'write'):
                                    try:
                                        # Garantir diretório
                                        os.makedirs(os.path.dirname(p), exist_ok=True)
                                        with open(p, 'w', encoding='utf-8') as f:
                                            f.write(content)
                                        enriched_command += f"\n\n[SISTEMA] Arquivo '{p}' escrito com sucesso."
                                    except Exception as e:
                                        enriched_command += f"\n\n[SISTEMA] Erro ao escrever '{p}': {e}"
                            
                                    except Exception as e:
                                        enriched_command += f"\n\n[SISTEMA] Erro ao escrever '{p}': {e}"
                        
                        elif "list_dir" in action_str:
                             path_match = re.search(r"list_dir\('(.+?)'\)", action_str)
                             if path_match:
                                 p = path_match.group(1)
                                 try:
                                     if os.path.isdir(p):
                                         items = os.listdir(p)
                                         enriched_command += f"\n\n[SISTEMA] Conteúdo de '{p}': {items[:50]}"
                                     else:
                                         enriched_command += f"\n\n[SISTEMA] Diretório não encontrado: {p}"
                                 except Exception as e:
                                     enriched_command += f"\n\n[SISTEMA] Erro ao listar: {e}"

                        elif "open_program" in action_str:
                            prog = re.search(r"'(.*?)'", action_str)
                            if prog:
                                action_controller.hotkey('win', 'r')
                                time.sleep(0.5)
                                action_controller.type_text(prog.group(1))
                                action_controller.press_key('enter')
                                
                        action_executed = True
                    except Exception as e:
                        logger.error(f"Erro ao executar ação '{action_str}': {e}")
                
                # Se executou ação, adiciona ao contexto e reitera (Agentic Loop)
                if action_executed:
                    enriched_command += f"\n\n[SISTEMA] Ações executadas: {actions}. O que mais?"
                    current_turn += 1
                    continue
            
            # Se não houve ação nem busca, é a resposta final
            break

        # ... (Step 6-7 unchanged) ...
        # 6. Salvar nova interação na memória neural e dataset
        neural_memory.store_interaction(user_command, response)
        
        # 7. Falar a resposta (removendo tags de ação para não falar código)
        clean_response = re.sub(r'\[ACTION: .*?\]', '', response)
        clean_response = re.sub(r'\[SEARCH: .*?\]', '', clean_response)
        
        final_response = f"{emotion_prefix}{clean_response}" if emotion_prefix and "no_action" not in clean_response.lower() else clean_response
        voice_controller.speak(final_response)
        return final_response

    def _handle_search(self, response, enriched_command):
        """Helper para busca web"""
        try:
            start = response.find("[SEARCH:") + 8
            end = response.find("]", start)
            query = response[start:end].strip()
            
            logger.info(f"IA solicitou busca: {query}")
            voice_controller.speak(f"Pesquisando sobre {query}...")
            
            search_results = web_search_tool.search_google(query, num_results=2)
            search_text = "\n".join(search_results)
            
            enriched_command += f"\n\n[RESULTADOS DA BUSCA PARA '{query}']:\n{search_text}\n\nResponda agora."
        except Exception:
            pass

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
