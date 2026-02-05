"""
Orquestrador do Agente de IA
Gerencia interação entre visão (OCR), decisão (LLM) e ação (PyAutoGUI)
"""

import logging
import os
import requests
import json
import re
import time
from typing import Dict, Any, List, Optional

# ============================================================================
# LOGGER SETUP - DEVE VIR ANTES DE QUALQUER IMPORT QUE USE LOGGER
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# CORE IMPORTS - SAFE LOADING
# ============================================================================
try:
    from src.database.models import db_manager, OCRResult
except ImportError as e:
    logger.warning(f"⚠️ Database models não disponível: {e}")
    db_manager = None
    OCRResult = None

try:
    from src.core.screen_capture import screen_capture
except ImportError as e:
    logger.error(f"❌ CRÍTICO: screen_capture não disponível: {e}")
    screen_capture = None

try:
    from src.core.action_controller import action_controller
except ImportError as e:
    logger.error(f"❌ CRÍTICO: action_controller não disponível: {e}")
    action_controller = None

try:
    from src.core.voice_controller import voice_controller
except ImportError as e:
    logger.warning(f"⚠️ voice_controller não disponível: {e}")
    voice_controller = None

try:
    from src.core.camera_controller import camera_controller
except ImportError as e:
    logger.warning(f"⚠️ camera_controller não disponível: {e}")
    camera_controller = None

try:
    from src.core.dataset_collector import dataset_collector
except ImportError as e:
    logger.warning(f"⚠️ dataset_collector não disponível: {e}")
    dataset_collector = None

try:
    from src.core.neural_memory import neural_memory
except ImportError as e:
    logger.warning(f"⚠️ neural_memory não disponível: {e}")
    neural_memory = None

try:
    from src.core.hardware_manager import hardware_manager
except ImportError as e:
    logger.warning(f"⚠️ hardware_manager não disponível: {e}")
    hardware_manager = None

try:
    from src.core.local_brain import local_brain
except ImportError as e:
    logger.warning(f"⚠️ local_brain não disponível: {e}")
    local_brain = None

try:
    from src.core.ui_detector import ui_detector
except ImportError as e:
    logger.warning(f"⚠️ ui_detector não disponível: {e}")
    ui_detector = None

try:
    from src.core.emotion_detector import emotion_detector
except ImportError as e:
    logger.warning(f"⚠️ emotion_detector não disponível: {e}")
    emotion_detector = None

try:
    from src.utils.web_search_tool import web_search_tool
except ImportError as e:
    logger.warning(f"⚠️ web_search_tool não disponível: {e}")
    web_search_tool = None

try:
    from src.core.security_manager import security_manager
except ImportError as e:
    logger.warning(f"⚠️ security_manager não disponível: {e}")
    # Create dummy security manager that allows everything (unsafe but won't crash)
    class DummySecurityManager:
        def validate_file_action(self, path, action):
            logger.warning(f"⚠️ Security manager ausente - permitindo {action} em {path}")
            return True
    security_manager = DummySecurityManager()

try:
    from src.utils.config import config
except ImportError as e:
    logger.warning(f"⚠️ config não disponível: {e}")
    # Create dummy config
    class DummyConfig:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config = DummyConfig()

# ============================================================================
# ADVANCED MODULES (JARVIS EVOLUTION) - SAFE LOADING
# ============================================================================
try:
    from src.core.advanced_action_controller import advanced_action_controller
    ADVANCED_ACTIONS_AVAILABLE = True
    logger.info("✅ Advanced Action Controller carregado")
except ImportError:
    ADVANCED_ACTIONS_AVAILABLE = False
    advanced_action_controller = None
    logger.warning("⚠️ Advanced Action Controller não disponível")

try:
    from src.core.advanced_vision_pipeline import advanced_vision_pipeline
    ADVANCED_VISION_AVAILABLE = True
    logger.info("✅ Advanced Vision Pipeline carregado")
except ImportError:
    ADVANCED_VISION_AVAILABLE = False
    advanced_vision_pipeline = None
    logger.warning("⚠️ Advanced Vision Pipeline não disponível")

try:
    from src.core.advanced_speech_processor import advanced_speech_processor
    ADVANCED_SPEECH_AVAILABLE = True
    logger.info("✅ Advanced Speech Processor carregado")
except ImportError:
    ADVANCED_SPEECH_AVAILABLE = False
    advanced_speech_processor = None
    logger.warning("⚠️ Advanced Speech Processor não disponível")

try:
    from src.core.workflow_engine import workflow_engine
    WORKFLOW_ENGINE_AVAILABLE = True
    logger.info("✅ Workflow Engine carregado")
except ImportError:
    WORKFLOW_ENGINE_AVAILABLE = False
    workflow_engine = None
    logger.warning("⚠️ Workflow Engine não disponível")

try:
    from src.core.security_manager_advanced import security_manager as security_manager_advanced
    ADVANCED_SECURITY_AVAILABLE = True
    logger.info("✅ Advanced Security Manager carregado")
except ImportError:
    ADVANCED_SECURITY_AVAILABLE = False
    security_manager_advanced = None
    logger.warning("⚠️ Advanced Security Manager não disponível")


class AIAgent:
    """Classe principal do Agente Inteligente"""

    def __init__(self, provider: str = 'gemini'):
        self.provider = provider
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Histórico de conversação
        self.chat_history = []
        
        # Brain Router - Sistema de Decisão Inteligente
        try:
            from src.core.brain_router import brain_router
            self.brain_router = brain_router
            logger.info("✅ Brain Router inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Brain Router não disponível: {e}")
            self.brain_router = None
        
        # Advanced Controllers
        self.advanced_actions = advanced_action_controller if ADVANCED_ACTIONS_AVAILABLE else None
        self.advanced_vision = advanced_vision_pipeline if ADVANCED_VISION_AVAILABLE else None
        self.advanced_speech = advanced_speech_processor if ADVANCED_SPEECH_AVAILABLE else None
        self.workflow_engine = workflow_engine if WORKFLOW_ENGINE_AVAILABLE else None
        self.security_advanced = security_manager_advanced if ADVANCED_SECURITY_AVAILABLE else None
        
        if self.advanced_actions:
            logger.info("✅ Advanced Action Controller carregado")
        if self.advanced_vision:
            logger.info("✅ Advanced Vision Pipeline carregado")
        if self.advanced_speech:
            logger.info("✅ Advanced Speech Processor carregado")
        if self.workflow_engine:
            logger.info("✅ Workflow Engine carregado")
        if self.security_advanced:
            logger.info("✅ Advanced Security Manager carregado")
        
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
        # 1. Definir Provedor Primário (LOCAL FIRST)
        # O Jarvis deve pensar localmente primeiro. A nuvem é auxílio.
        primary_provider = 'ollama' if self._check_ollama_alive() else 'local_brain'
        
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
        max_turns = 5 
        current_turn = 0
        
        while current_turn < max_turns:
            logger.info(f"Ciclo de Pensamento {current_turn+1}/{max_turns} | Provedor: {primary_provider}")
            
            # --- TENTATIVA LOCAL ---
            try:
                if primary_provider == 'ollama':
                    response = self._call_ollama(enriched_command, screenshot_path)
                else:
                    response = local_brain.generate_response(enriched_command, self.system_prompt)
            except Exception as e:
                logger.error(f"Falha no cérebro local ({primary_provider}): {e}")
                response = "ERRO_LOCAL"

            # --- ESCALONAMENTO PARA NUVEM (SUPLEMENTO) ---
            # Se o local falhar, não souber, ou for complexo demais
            triggers_cloud = ["não sei", "i don't know", "desculpe", "erro_local", "complexo"]
            needs_cloud = any(t in response.lower() for t in triggers_cloud) or len(response) < 5
            
            if needs_cloud and self.api_key and voice_controller.check_internet():
                logger.info("Cérebro Local incerto. Consultando a Nuvem (Gemini) para auxílio...")
                voice_controller.speak("Consultando minha base de conhecimento na nuvem...", wait=False)
                
                cloud_response = self._call_gemini(enriched_command, screenshot_path)
                
                if "Erro" not in cloud_response:
                    response = cloud_response
                    # APRENDIZADO (Distillation): Salvar resposta da nuvem para treino futuro
                    neural_memory.store_interaction(user_command, cloud_response, source="cloud_teacher")
            
            # Fallback final se tudo falhar
            if "ERRO_LOCAL" in response and "Erro" in response:
                 response = "Senhor, meus sistemas locais e remotos estão inacessíveis no momento."
            
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
                            args = re.search(r"write_file\('(.+?)',\s*'(.+?)'\)", action_str)
                            if args:
                                p, content = args.group(1), args.group(2)
                                content = content.replace('\\n', '\n') 
                                if security_manager.validate_file_action(p, 'write'):
                                    try:
                                        os.makedirs(os.path.dirname(p), exist_ok=True)
                                        with open(p, 'w', encoding='utf-8') as f:
                                            f.write(content)
                                        enriched_command += f"\n\n[SISTEMA] Arquivo '{p}' escrito com sucesso."
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

    def process_hybrid_vision(self, screenshot_path: str) -> Dict[str, Any]:
        """
        [VISÃO HÍBRIDA - STARK EVOLUTION]
        Nível 1 (Local): Filtro rápido com UIdetector/YOLO (CPU).
        Nível 2 (Nuvem): Análise profunda com Gemini PRO se houver complexidade.
        Nível 3 (Feedback): Resposta da nuvem treina o banco local.
        """
        result = {"source": "local", "action": "none", "analysis": ""}
        logger.info("[HYBRID VISION] Iniciando ciclo de análise...")

        try:
            # --- NÍVEL 1: SENTINELA LOCAL (YOLO/CPU) ---
            # Custo: $0.00 | Tempo: <500ms
            ui_elements = ui_detector.detect_elements(screenshot_path)
            element_count = len(ui_elements)
            
            # Heurística de Complexidade Visual
            # Se tiver muitos elementos, texto denso (implícito), ou padrões de erro
            is_complex_context = element_count > 3 
            
            summary = ui_detector.get_summary(ui_elements)
            logger.info(f"[HYBRID VISION] Nível 1 (Local): {summary} | Complexo? {is_complex_context}")

            if not is_complex_context:
                # Tela simples/estática. Nada a fazer.
                return result

            # --- NÍVEL 2: ANÁLISE PROFUNDA LOCAL (LLAVA) ---
            # Tentamos resolver localmente primeiro se houver GPU ou LLaVA rodando.
            logger.info("[HYBRID VISION] Nível 2 (Local AI)...")
            
            vision_prompt = (
                "VISÃO TOTAL ATIVADA.\n"
                f"Contexto: {summary}\n"
                "Analise esta imagem. Se houver erro crítico ou algo notável para o usuário, explique.\n"
                "Caso contrário, responda APENAS 'NO_ACTION'."
            )
            
            local_response = ""
            if self._check_ollama_alive():
                try:
                    local_response = self._call_ollama(vision_prompt, screenshot_path)
                except:
                    local_response = "incerto"

            # Se o local resolver (e não for erro/incerto), usamos ele.
            if local_response and len(local_response) > 5 and "incerto" not in local_response.lower():
                result["source"] = "local_llm"
                result["analysis"] = local_response
                if "no_action" not in local_response.lower():
                     voice_controller.speak(local_response)
                     result["action"] = "spoke_local"
                return result

            # --- NÍVEL 3: OBSERVADOR DA NUVEM (GEMINI - SUPLEMENTO) ---
            # Só acionamos se o Local falhar ou estiver incerto.
            
            logger.info("[HYBRID VISION] Local incerto. Escalando para Nível 3 (Nuvem)...")
            
            # Usar Gemini Flash (Rápido) ou Pro (Inteligente)
            cloud_response = self._call_gemini(vision_prompt, screenshot_path)
            
            result["source"] = "cloud"
            result["analysis"] = cloud_response
            
            # --- FEEDBACK / APRENDIZADO (DISTILLATION) ---
            if "NO_ACTION" not in cloud_response:
                dataset_collector.save_sample(
                    image_path=screenshot_path,
                    prompt=vision_prompt,
                    response=cloud_response,
                    source="hybrid_vision_auto"
                )
                
                logger.info(f"[HYBRID VISION] Jarvis React (Cloud): {cloud_response}")
                voice_controller.speak(cloud_response)
                result["action"] = "spoke_cloud"
            else:
                logger.info("[HYBRID VISION] Nuvem analisou e decidiu não interromper.")

        except Exception as e:
            logger.error(f"[HYBRID VISION] Erro crítico: {e}")
        
        return result

    def process_proactive_analysis(self, change_data: Dict[str, Any]):
        """
        [SENTINELA PROATIVO]
        Analisa mudanças detectadas na tela e decide se deve intervir.
        """
        try:
            diff_percent = change_data.get('diff_percent', 0)
            screenshot_path = change_data.get('screenshot_path')
            
            if not screenshot_path or not os.path.exists(screenshot_path):
                return
            
            logger.info(f"Iniciando análise proativa ({diff_percent:.1f}% de mudança)...")
            
            # Usar visão híbrida para analisar
            result = self.process_hybrid_vision(screenshot_path)
            analysis = result.get("analysis", "")
            
            if analysis and "NO_ACTION" not in analysis.upper():
                logger.info(f"Intervenção proativa bem sucedida: {analysis}")
                return analysis
            
            return None

        except Exception as e:
            logger.error(f"Erro na análise proativa: {e}")
            return None


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
