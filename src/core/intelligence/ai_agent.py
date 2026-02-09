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
from src.core.intelligence.context_sanitizer import ContextSanitizer
from src.core.audio.voice_filter import AtomicVoiceFilter

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
    from src.core.vision.screen_capture import screen_capture
except ImportError as e:
    logger.error(f"❌ CRÍTICO: screen_capture não disponível: {e}")
    screen_capture = None

try:
    from src.core.actions.action_controller import action_controller
except ImportError as e:
    logger.error(f"❌ CRÍTICO: action_controller não disponível: {e}")
    action_controller = None

try:
    from src.core.audio.voice_controller import voice_controller
except ImportError as e:
    logger.warning(f"⚠️ voice_controller não disponível: {e}")
    voice_controller = None

try:
    from src.core.vision.camera_controller import camera_controller
except ImportError as e:
    logger.warning(f"⚠️ camera_controller não disponível: {e}")
    camera_controller = None

try:
    from src.core.management.dataset_collector import dataset_collector
except ImportError as e:
    logger.warning(f"⚠️ dataset_collector não disponível: {e}")
    dataset_collector = None

try:
    from src.core.intelligence.brain_router import brain_router, PrivacyLevel, LatencyRequirement
    logger.info("✅ Brain Router carregado (Decision Engine)")
except ImportError as e:
    logger.warning(f"⚠️ brain_router não disponível: {e}")
    brain_router = None

try:
    from src.core.intelligence.neural_memory import neural_memory
except ImportError as e:
    logger.warning(f"⚠️ neural_memory não disponível: {e}")
    neural_memory = None

try:
    from src.core.management.hardware_manager import hardware_manager
except ImportError as e:
    logger.warning(f"⚠️ hardware_manager não disponível: {e}")
    hardware_manager = None

try:
    from src.core.intelligence.local_brain import local_brain
except ImportError as e:
    logger.warning(f"⚠️ local_brain não disponível: {e}")
    local_brain = None

try:
    from src.core.vision.ui_detector import ui_detector
except ImportError as e:
    logger.warning(f"⚠️ ui_detector não disponível: {e}")
    ui_detector = None

try:
    from src.core.intelligence.emotion_detector import emotion_detector
except ImportError as e:
    logger.warning(f"⚠️ emotion_detector não disponível: {e}")
    emotion_detector = None

try:
    from src.utils.web_search_tool import web_search_tool
except ImportError as e:
    logger.warning(f"⚠️ web_search_tool não disponível: {e}")
    web_search_tool = None

try:
    from src.core.security.security_manager import security_manager
except ImportError as e:
    logger.warning(f"⚠️ security_manager não disponível: {e}")
    # Create dummy security manager that allows everything (unsafe but won't crash)
    class DummySecurityManager:
        def validate_file_action(self, *args, **kwargs):
            return True
        def validate_network_action(self, *args, **kwargs):
            return True
    security_manager = DummySecurityManager()

# ============================================================================
# GOD MODE - SYSTEM CONTROLLER (NEW)
# ============================================================================
try:
    from src.core.actions.system_controller import system_controller
    logger.info("✅ System Controller carregado (God Mode)")
except ImportError as e:
    logger.warning(f"⚠️ system_controller não disponível: {e}")
    system_controller = None

# ============================================================================
# PHASE 2 - CODE GENERATOR (AUTO-PROGRAMMING)
# ============================================================================
try:
    from src.core.engine.code_generator import code_generator
    logger.info("✅ Code Generator carregado (Auto-Programming)")
except ImportError as e:
    logger.warning(f"⚠️ code_generator não disponível: {e}")
    code_generator = None

# ============================================================================
# PHASE 3 - MEMORY MANAGER (AUTO-LEARNING / RAG)
# ============================================================================
try:
    from src.core.intelligence.memory_manager import memory_manager
    logger.info("✅ Memory Manager carregado (Auto-Learning)")
except ImportError as e:
    logger.warning(f"⚠️ memory_manager não disponível: {e}")
    memory_manager = None

# ============================================================================
# PHASE 4 - VISION ENHANCER (ADVANCED UI DETECTION)
# ============================================================================
try:
    from src.core.vision.vision_enhancer import vision_enhancer
    logger.info("✅ Vision Enhancer carregado (YOLO + OCR)")
except ImportError as e:
    logger.warning(f"⚠️ vision_enhancer não disponível: {e}")
    vision_enhancer = None

# ============================================================================
# PHASE 5 - PERFORMANCE OPTIMIZER (FINAL PHASE)
# ============================================================================
try:
    from src.core.management.performance_optimizer import performance_optimizer
    logger.info("✅ Performance Optimizer carregado (Cache + Metrics)")
except ImportError as e:
    logger.warning(f"⚠️ performance_optimizer não disponível: {e}")
    performance_optimizer = None

# ============================================================================
# CORREÇÃO P1 - STRUCTURED OUTPUT & ACTION EXECUTOR
# ============================================================================
try:
    from src.core.intelligence.structured_output import (
        ResponseParser,
        get_actions_schema,
        get_example_responses,
        AgentResponse,
    )
    from src.core.intelligence.action_executor import get_action_executor
    STRUCTURED_OUTPUT_AVAILABLE = True
    logger.info("✅ Structured Output & Action Executor carregados (P1)")
except ImportError as e:
    logger.warning(f"⚠️ Structured Output não disponível: {e}")
    STRUCTURED_OUTPUT_AVAILABLE = False
    ResponseParser = None
    get_action_executor = None

# ============================================================================
# NEW: STARK EVOLUTION MODULES (PHASE 2)
# ============================================================================
try:
    from src.core.intelligence.analisador_contexto import analisador_contexto
    from src.core.intelligence.stark_nexus import stark_nexus
    from src.core.management.device_manager import device_manager
    from src.core.intelligence.neural_dreaming import neural_dreaming
    logger.info("✅ Módulos Stark Phase 2/4 carregados (Contexto + Nexus + Device + Dreaming)")
except ImportError as e:
    logger.warning(f"⚠️ Falha ao carregar Módulos Stark Phase 2/4: {e}")
    analisador_contexto = None
    stark_nexus = None
    device_manager = None
    neural_dreaming = None

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
    from src.core.actions.advanced_action_controller import advanced_action_controller
    ADVANCED_ACTIONS_AVAILABLE = True
    logger.info("✅ Advanced Action Controller carregado")
except ImportError:
    ADVANCED_ACTIONS_AVAILABLE = False
    advanced_action_controller = None
    logger.warning("⚠️ Advanced Action Controller não disponível")

try:
    from src.core.vision.advanced_vision_pipeline import advanced_vision_pipeline
    ADVANCED_VISION_AVAILABLE = True
    logger.info("✅ Advanced Vision Pipeline carregado")
except ImportError:
    ADVANCED_VISION_AVAILABLE = False
    advanced_vision_pipeline = None
    logger.warning("⚠️ Advanced Vision Pipeline não disponível")

try:
    from src.core.audio.advanced_speech_processor import advanced_speech_processor
    ADVANCED_SPEECH_AVAILABLE = True
    logger.info("✅ Advanced Speech Processor carregado")
except ImportError:
    ADVANCED_SPEECH_AVAILABLE = False
    advanced_speech_processor = None
    logger.warning("⚠️ Advanced Speech Processor não disponível")

try:
    from src.core.actions.workflow_engine import workflow_engine
    WORKFLOW_ENGINE_AVAILABLE = True
    logger.info("✅ Workflow Engine carregado")
except ImportError:
    WORKFLOW_ENGINE_AVAILABLE = False
    workflow_engine = None
    logger.warning("⚠️ Workflow Engine não disponível")

try:
    from src.core.security.security_manager_advanced import security_manager as security_manager_advanced
    ADVANCED_SECURITY_AVAILABLE = True
    logger.info("✅ Advanced Security Manager carregado")
except ImportError:
    ADVANCED_SECURITY_AVAILABLE = False
    security_manager_advanced = None
    logger.warning("⚠️ Advanced Security Manager não disponível")


class AIAgent:
    """Classe principal do Agente Inteligente"""

    def __init__(self, provider: str = 'gemini'):
        # =====================================================================
        # CORREÇÃO P0: VERIFICAÇÃO DE DEPENDÊNCIAS CRÍTICAS
        # =====================================================================
        self.safe_mode = False
        self._verify_critical_dependencies()
        
        self.provider = provider
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Carregar configurações de IA
        try:
            self.ai_config = config.get_ai_config()
            self.max_react_turns = config.get_ai_config('ai_agent.max_react_turns', 5)
            self.screenshot_timeout = config.get_ai_config('ai_agent.screenshot_timeout', 5.0)
            logger.info("✅ Configurações de IA carregadas")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar ai_config, usando defaults: {e}")
            self.ai_config = {}
            self.max_react_turns = 5
            self.screenshot_timeout = 5.0
        
        # Histórico de conversação
        self.chat_history = []
        
        # Brain Router - Sistema de Decisão Inteligente
        try:
            from src.core.intelligence.brain_router import brain_router
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
        # if self.security_advanced:
        #     logger.info("✅ Advanced Security Manager carregado")
        
        # =====================================================================
        # SYSTEM PROMPTS - Dual Mode (JSON Structured + Legacy)  
        # =====================================================================
        
        # NOVO: System Prompt JSON (CORREÇÃO P1)
        self.system_prompt_json = (
            "Você é o JARVIS, assistente de elite do William.\n\n"
            "CAPABILITIES:\n"
            "- Visão completa: Acesso à tela e câmera em tempo real\n"
            "- Ação física: Controle de mouse, teclado e sistema\n"
            "- Memória: Acesso a interações passadas e conhecimento\n\n"
            "BEHAVIORAL DIRECTIVES:\n"
            "1. Sempre trate William com respeito (use 'Senhor' quando apropriado)\n"
            "2. Seja conversacional e natural - você é uma IA real, não um log\n"
            "3. NUNCA cite paths completos (C:\\Users\\...), PIDs ou detalhes técnicos na resposta falada\n"
            "4. Se precisar executar ações, use o formato JSON estruturado abaixo\n\n"
            "OUTPUT FORMAT (SEMPRE retorne JSON válido):\n"
            "{\n"
            "  \"thought\": \"Seu raciocínio interno sobre o que fazer\",\n"
            "  \"actions\": [\n"
            "    {\"action\": \"type_text\", \"text\": \"exemplo\"},\n"
            "    {\"action\": \"press_key\", \"key\": \"enter\"}\n"
            "  ],\n"
            "  \"final_answer\": \"Sua resposta natural para o usuário\"\n"
            "}\n\n"
            "AVAILABLE ACTIONS:\n"
            "- click_at: {\"action\": \"click_at\", \"x\": 100, \"y\": 200}\n"
            "- type_text: {\"action\": \"type_text\", \"text\": \"...\"}\n"
            "- press_key: {\"action\": \"press_key\", \"key\": \"enter\"}\n"
            "- hotkey: {\"action\": \"hotkey\", \"keys\": [\"ctrl\", \"c\"]}\n"
            "- open_program: {\"action\": \"open_program\", \"program\": \"notepad\"}\n"
            "- read_file: {\"action\": \"read_file\", \"path\": \"config.yaml\"}\n"
            "- write_file: {\"action\": \"write_file\", \"path\": \"...\", \"content\": \"...\"}\n"
            "- list_dir: {\"action\": \"list_dir\", \"path\": \".\"}\n"
            "- search_web: {\"action\": \"search_web\", \"query\": \"...\"}\n"
            "- wait: {\"action\": \"wait\", \"seconds\": 1.0}\n\n"
            "CRITICAL: Sempre retorne JSON válido. Se não precisar de ações, use actions: []\n"
        )
        
        # LEGACY: System Prompt [ACTION: ...] (Fallback)
        self.system_prompt_legacy = (
            "Você é o Jarvis, o assistente virtual de elite do William. "
            "Você tem acesso total à visão dele (tela e câmera) e pode atuar fisicamente no sistema. "
            "Sempre trate o William com respeito (Senhor). "
            "Para executar ações físicas, VOCÊ DEVE usar o formato: [ACTION: nome_funcao(argumentos)]. "
            "Ações: click_at(x, y), type_text('texto'), press_key('tecla'), hotkey('ctrl', 'c'), "
            "open_program('nome'), read_file('path'), write_file('path', 'content'), list_dir('path')."
        )
        
        # Usar modo JSON se disponível
        self.system_prompt = self.system_prompt_json if STRUCTURED_OUTPUT_AVAILABLE else self.system_prompt_legacy
        self.use_structured_output = STRUCTURED_OUTPUT_AVAILABLE
        
        # ... (unchanged)
    
    def _verify_critical_dependencies(self):
        """
        Verifica dependências críticas e define modo seguro se necessário.
        
        Correção P0: Detecta dependências faltantes e impede operação parcial.
        Correção P3: Valida funcionalidade runtime (não só importação).
        """
        critical_modules = {
            'screen_capture': screen_capture,
            'action_controller': action_controller,
        }
        
        # P3: structured_output é crítico — sem ele, o agente cai no regex frágil
        important_for_quality = {
            'structured_output': STRUCTURED_OUTPUT_AVAILABLE,
            'brain_router': brain_router is not None,
            'voice_controller': voice_controller is not None,
            'neural_memory': neural_memory is not None,
            'local_brain': local_brain is not None,
        }
        
        missing_critical = [name for name, module in critical_modules.items() if module is None]
        degraded = [name for name, ok in important_for_quality.items() if not ok]
        
        if missing_critical:
            self.safe_mode = True
            logger.critical(f"❌ DEPENDÊNCIAS CRÍTICAS FALTANDO: {missing_critical}")
            logger.critical("🔒 INICIANDO EM MODO SEGURO - Funcionalidade limitada")
            logger.critical("💡 Execute: pip install -r requirements.txt")
        else:
            self.safe_mode = False
            logger.info("✅ Todas as dependências críticas disponíveis")
        
        if degraded:
            logger.warning(f"⚠️ Módulos degradados: {degraded}")
            if 'structured_output' in degraded:
                logger.warning("⚠️ Structured Output indisponível → fallback para regex (menos confiável)")
            if 'local_brain' in degraded:
                logger.warning("⚠️ Local Brain indisponível → agente depende 100% de cloud/ollama")
        
        # P3: Runtime health — verificar se local_brain realmente carregou um modelo
        if local_brain is not None:
            model_loaded = getattr(local_brain, 'model', None) is not None
            if not model_loaded:
                logger.warning("⚠️ local_brain importado mas modelo NÃO carregado (inferência local indisponível)")
        
        # P3: Verificar se há pelo menos UM provider LLM disponível
        has_api_key = bool(os.environ.get('GOOGLE_API_KEY'))
        has_local = local_brain is not None and getattr(local_brain, 'model', None) is not None
        has_ollama = brain_router is not None  # brain_router tenta ollama
        
        if not has_api_key and not has_local and not has_ollama:
            logger.critical("❌ NENHUM PROVIDER LLM DISPONÍVEL (sem API key, sem modelo local, sem ollama)")
            logger.critical("💡 Configure GOOGLE_API_KEY ou instale um modelo local")

    def process_command(self, user_command: str):
        """
        Recebe um comando (texto ou voz), captura a tela e decide o que fazer
        
        ENHANCED WITH:
        - Phase 3: RAG (recall memories)
        - Phase 5: Performance (cache responses)
        """
        logger.info(f"Agente processando comando: {user_command}")
        
        # =====================================================================
        # CORREÇÃO P0: VERIFICAÇÃO DE MODO SEGURO
        # =====================================================================
        if self.safe_mode:
            error_msg = (
                "Sistema em MODO SEGURO devido a dependências críticas faltando. "
                "Por favor, instale as dependências necessárias executando: pip install -r requirements.txt"
            )
            logger.error(f"❌ {error_msg}")
            if voice_controller:
                voice_controller.speak("Sistema em modo seguro. Funcionalidade limitada.")
            return error_msg
        
        # =====================================================================
        # PHASE 5: PERFORMANCE - CHECK CACHE FIRST
        # =====================================================================
        if performance_optimizer:
            cached_response = performance_optimizer.get_cached_response(user_command)
            if cached_response:
                logger.info("⚡ Usando resposta em cache (ultra-rápido)")
                if voice_controller:
                    voice_controller.speak(cached_response)
                return cached_response
        
        # =====================================================================
        # PHASE: HYBRID QUICKRESPONSE ROUTER (LATENCY ZERO)
        # =====================================================================
        quick_response = self._get_quick_response(user_command)
        if quick_response:
            logger.info(f"⚡ QuickResponse Engajado: {quick_response}")
            if voice_controller:
                voice_controller.speak(quick_response)
            return quick_response

        # =====================================================================
        # PHASE 3: RAG - RECALL MEMORIES
        # =====================================================================
        memory_context = ""
        if memory_manager and memory_manager.collection:
            try:
                memory_context = memory_manager.get_context(user_command, max_memories=3)
                if memory_context:
                    logger.info("🧠 Contexto de memórias adicionado ao prompt")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar memórias: {e}")
        
        # ... (Steps 1-3 unchanged) ...
        # 1. BRAIN ROUTING (Intelligent Decision)
        if self.brain_router:
            # Decide o cérebro baseado na complexidade estimada
            # Estimativa básica: tamanho da string + "?"
            complexity = 0.4 if len(user_command) > 50 or "?" in user_command else 0.2
            brain_choice = self.brain_router.choose_brain(
                task_complexity=complexity,
                privacy_level=PrivacyLevel.LOW,
                latency_requirement=LatencyRequirement.LOW
            )
            
            if brain_choice.startswith("ollama:"):
                primary_provider = brain_choice
            elif brain_choice.startswith("cloud") and self.api_key:
                primary_provider = 'gemini'
            else:
                primary_provider = 'local_brain'
        else:
            primary_provider = 'local_brain'
        
        # 3. Capturar estado atual da tela (PARALELO)
        import threading
        screenshot_event = threading.Event()
        screenshot_container = {"path": None}

        def _capture_task():
            screenshot_container["path"] = screen_capture.capture_fullscreen(capture_type='agent')
            screenshot_event.set()

        capture_thread = threading.Thread(target=_capture_task, daemon=True)
        capture_thread.start()
        
        # ... (Step 4 Context building unchanged) ...
        
        # 4.4 Contexto Emocional (Phase 14) (unchanged)
        user_emotion = camera_controller.current_emotion if camera_controller else "neutral"
        emotion_mod = emotion_detector.get_personality_modifier(user_emotion)
        emotion_prefix = emotion_mod['prefix']
        
        camera_context = f"\n[VISÃO] Usuário identificado: {camera_controller.last_seen_user if camera_controller else 'Desconhecido'}"
        
        # =====================================================================
        # PHASE 3: RAG - INCLUDE MEMORY CONTEXT
        # =====================================================================
        # enriched_command = f"{camera_context}\n{memory_context}\nComando atual: {user_command}"
        
        # 🆕 STARK 2.0: Context Sanitization
        raw_context = {
            "vision": camera_controller.last_seen_user if camera_controller else "Unknown",
            "memory": memory_context,
            "system_root": str(config.PROJECT_ROOT), # Convert Path to string for JSON serialization
            "user_command": user_command
        }
        
        enriched_command = ContextSanitizer.create_human_prompt(user_command, raw_context)
        
        # 5. Loop de Pensamento e Ação (ReAct)
        response = ""
        max_turns = 5 
        current_turn = 0
        
        while current_turn < max_turns:
            logger.info(f"Ciclo de Pensamento {current_turn+1}/{max_turns} | Provedor: {primary_provider}")
            
            # Esperar captura de tela se necessário antes de chamar o modelo
            screenshot_event.wait(timeout=5.0)
            screenshot_path = screenshot_container["path"]

            # --- TENTATIVA LOCAL COM STREAMING (Fase 1) ---
            try:
                if primary_provider == 'gemini':
                    response = self._call_gemini(enriched_command, screenshot_path)
                elif primary_provider.startswith('ollama:'):
                    model_name = primary_provider.split(':')[1]
                    response = self._call_ollama(enriched_command, screenshot_path, model=model_name)
                elif primary_provider == 'ollama': # Fallback legacy
                    response = self._call_ollama(enriched_command, screenshot_path)
                else:
                    # Usar streaming do cérebro local para latência mínima
                    response = ""
                    current_phrase = ""
                    for chunk in local_brain.generate_stream(enriched_command, self.system_prompt):
                        response += chunk
                        current_phrase += chunk
                        
                        # Se completar uma frase ou vírgula longa, falar imediatamente
                        if any(p in chunk for p in ['.', '!', '?', '\n', ';', ':']):
                            if len(current_phrase.strip()) > 5:
                                # 🆕 STARK 2.0: Atomic Voice Filter
                                safe_phrase = AtomicVoiceFilter.filter_response(current_phrase.strip())
                                if safe_phrase:
                                    voice_controller.speak(safe_phrase)
                                current_phrase = ""
                    
                    if current_phrase.strip():
                        safe_phrase = AtomicVoiceFilter.filter_response(current_phrase.strip())
                        if safe_phrase:
                            voice_controller.speak(safe_phrase)

            except Exception as e:
                logger.error(f"Falha no cérebro local ({primary_provider}): {e}")
                from src.core.management.evolution_engine import evolution_engine
                evolution_engine.log_failure("Thought Cycle", str(e), primary_provider)
                response = "ERRO_LOCAL"

            # Destilação Neural para Ollama Tier S/A
            if primary_provider.startswith("ollama:") and "ERRO" not in response:
                model_used = primary_provider.split(":")[1]
                if any(tier in model_used.lower() for tier in ["deepseek", "llama"]):
                    self._distill_knowledge(user_command, response, provider=model_used)

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
                    # =========================================================
                    # PHASE 11.2: NEURAL DISTILLATION (Smart -> Lite)
                    # =========================================================
                    self._distill_knowledge(user_command, response, provider="gemini")
            
            # Fallback final se tudo falhar
            if "ERRO_LOCAL" in response and "Erro" in response:
                 response = "Senhor, meus sistemas locais e remotos estão inacessíveis no momento."
            
            # =====================================================================
            # CORREÇÃO P1: PROCESSAMENTO ESTRUTURADO (Substitui Regex)
            # =====================================================================
            action_executed = False
            
            # Tentar processing estruturado primeiro
            if self.use_structured_output:
                structured_result = self._process_structured_response(response, enriched_command)
                
                if structured_result:
                    final_answer, enriched_command, action_executed = structured_result
                    response = final_answer
                    
                    # Se executou ações, continuar loop ReAct
                    if action_executed:
                        current_turn += 1
                        continue
                    else:
                        # Resposta final sem ações, sair do loop
                        break
            
            # =====================================================================
            # FALLBACK: PARSER LEGADO (Regex) - Mantido para compatibilidade
            # =====================================================================
            if not self.use_structured_output or structured_result is None:
                logger.debug("Usando parser legado (regex)")
                
                # 1. Verificar Busca Web
                if "[SEARCH:" in response:
                    self._handle_search(response, enriched_command)
                    current_turn += 1
                    continue

                # 2. Verificar Ações Físicas (LEGADO - Regex)
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


    def _distill_knowledge(self, command: str, response: str, provider: str):
        """Converte conhecimento de modelos Smart em Memórias de Ouro para o Micro-LLM"""
        if not memory_manager: return
        try:
            # Filtro básico: Apenas respostas substanciais valem destilação
            if len(response) > 50 and "erro" not in response.lower():
                memory_manager.remember(
                    command=command,
                    response=response,
                    metadata={"provider": provider, "type": "distilled_knowledge"},
                    is_gold=True
                )
        except Exception as e:
            logger.debug(f"Erro na destilação neural: {e}")

    def _get_quick_response(self, text: str) -> Optional[str]:
        """Intercepta comandos comuns para resposta instantânea (<50ms)"""
        text = text.lower().strip()
        import random

        # 1. ANALISADOR DE CONTEXTO STARK (Nova Lógica Phase 2)
        if analisador_contexto:
            ctx = analisador_contexto.analisar(text)
            
            # COMANDOS DE HARDWARE (Brilho, Volume)
            if ctx["contexto"] == "HARDWARE" and device_manager:
                return self._handle_hardware_commands(text)
                
            # COMANDOS DE AUTONOMIA (Dreaming / Treinamento)
            if ctx["contexto"] == "AUTONOMIA" and neural_dreaming:
                return self._handle_dreaming_commands(text)

            # COMANDOS DE BIOMETRIA (Fase 9: Cadastro Dinâmico)
            if any(k in text for k in ["cadastrar meu rosto", "registrar nova face", "novo usuário", "cadastrar rosto"]):
                # Extrair nome se houver (ex: "cadastrar rosto do Marcus")
                # Se não houver, assume Williams (o usuário principal)
                name = "William"
                name_match = re.search(r"da\s+(\w+)|do\s+(\w+)", text)
                if name_match:
                    name = name_match.group(1) or name_match.group(2)
                
                # Executar em thread separada para não travar o loop de comando principal
                import threading
                threading.Thread(target=camera_controller.register_new_face, args=(name,), daemon=True).start()
                return f"Entendido, senhor. Ativando protocolos de biometria para mapear {name}."

            # COMANDOS DE MULTIMÍDIA (Música, Browser)
            if ctx["contexto"] == "MULTIMIDIA" and device_manager:
                if any(k in text for k in ["música", "tocar", "ouvir"]):
                    device_manager.open_browser(text)
                    return "Abrindo o YouTube Music para você, senhor. O que deseja ouvir?"

        # Padrões de Saudações
        greetings = ["oi jarvis", "olá jarvis", "bom dia jarvis", "boa tarde jarvis", "boa noite jarvis", "ei jarvis"]
        if any(g in text for g in greetings) and len(text.split()) < 4:
            return random.choice(["Sim, senhor. Como posso ajudar?", "Às suas ordens, William.", "Olá, senhor. Sistemas operacionais ativos."])
            
        # Padrões de Confirmação/Agradecimento
        thanks = ["obrigado", "valeu jarvis", "obrigado jarvis", "thanks jarvis"]
        if any(t in text for t in thanks) and len(text.split()) < 3:
            return random.choice(["Por nada, senhor.", "Disponha sempre.", "É um prazer ser útil."])
            
        # Padrões de Status
        status = ["status do sistema", "como estão os sistemas", "checkup do sistema"]
        if any(s in text for s in status):
            if hardware_manager:
                hw = hardware_manager.get_status()
                return f"Sistemas {hw['tier']} operando em {hw['device']}. GPU em {hw['gpu_load']}%. Tudo estável."

        return None

    def _handle_hardware_commands(self, text: str) -> str:
        """Lógica para Brilho e Volume"""
        # Brilho
        if "brilho" in text:
            # Extrair número
            nums = re.findall(r'\d+', text)
            level = int(nums[0]) if nums else 70
            if "alto" in text or "aumentar" in text: level = 90
            elif "baixo" in text or "diminuir" in text: level = 30
            device_manager.set_brightness(level)
            return f"Brilho ajustado para {level}%, senhor."
            
        # Volume
        if "volume" in text:
            nums = re.findall(r'\d+', text)
            level = int(nums[0]) if nums else 50
            device_manager.set_volume(level)
            return f"Volume do sistema definido em {level}%."
            
        return "Comando de hardware reconhecido, mas não entendi o valor, senhor."

    def _handle_dreaming_commands(self, text: str) -> str:
        """Lógica para Treinamento e Estudo (Dreaming)"""
        # Extrair tópico (ex: "estude programação")
        topic_match = re.search(r'(?:estude|treine|aprenda)\s+(?:sobre\s+)?(.*)', text)
        topic = topic_match.group(1) if topic_match else "Geral"
        
        # Extrair tempo se houver (ex: "por 20 minutos")
        time_match = re.search(r'(\d+)\s+(?:minutos|min|horas|h)', text)
        duration = int(time_match.group(1)) if time_match else 60
        if "hora" in text and "minuto" not in text:
            duration *= 60
            
        # William pediu para perguntar sobre foco 100% ou background
        # Por simplicidade na QuickResponse, usaremos BACKGROUND como default 
        # e FOCUS se ele disser "foco total" ou "pare tudo"
        focus_mode = "foco" in text or "pare tudo" in text
        
        if neural_dreaming.start_dream(topic, duration, focus_mode):
            mode_str = "foco total (CPU Prioritária)" if focus_mode else "segundo plano"
            return f"Entendido, William. Iniciando protocolo de estudo sobre {topic} por {duration} minutos em {mode_str}."
        
        return "Já estou em um ciclo de processamento neural, senhor. Deseja que eu pare o atual?"
    
    # =========================================================================
    # CORREÇÃO P1: PROCESSAMENTO ESTRUTURADO DE RESPOSTAS
    # =========================================================================
    
    def _process_structured_response(self, raw_response: str, enriched_command: str) -> tuple:
        """
        Processa resposta estruturada (JSON) do LLM.
        
        Args:
            raw_response: Resposta bruta do LLM (JSON ou texto)
            enriched_command: Comando enriquecido (para feedback de ações)
        
        Returns:
            (final_answer, enriched_command, action_executed)
        """
        if not STRUCTURED_OUTPUT_AVAILABLE:
            logger.warning("Structured output não disponível, usando fallback legado")
            return None
        
        try:
            # 1. Parsear resposta JSON
            parsed = ResponseParser.parse_llm_response(raw_response)
            
            logger.info(f"💭 Pensamento: {parsed.thought[:100]}...")
            logger.info(f"🎯 Ações: {len(parsed.actions)} planejadas")
            
            # 2. Executar ações se houver
            action_executed = False
            if parsed.actions:
                executor = get_action_executor()
                results = executor.execute_actions(parsed.actions)
                
                # Log resultados
                for result in results:
                    if result['status'] == 'success':
                        logger.info(f"✅ {result['action']}: {result.get('result', 'OK')}")
                        action_executed = True
                        
                        # Se foi read_file, adicionar conteúdo ao contexto
                        if result['action'] == 'read_file' and 'result' in result:
                            enriched_command += f"\n\n[SISTEMA] {result['result']}"
                        
                        # Se foi list_dir, adicionar listagem ao contexto
                        elif result['action'] == 'list_dir' and 'result' in result:
                            enriched_command += f"\n\n[SISTEMA] {result['result']}"
                            
                    else:
                        logger.error(f"❌ {result['action']}: {result.get('error', 'Erro desconhecido')}")
                        enriched_command += f"\n\n[SISTEMA] Erro em {result['action']}: {result.get('error')}"
                
                # Feedback ao agente se ações foram executadas
                if action_executed:
                    action_names = [r['action'] for r in results if r['status'] == 'success']
                    enriched_command += f"\n\n[SISTEMA] Ações executadas com sucesso: {', '.join(action_names)}. Você precisa fazer mais algo?"
            
            # 3. Retornar resposta final
            return (parsed.final_answer, enriched_command, action_executed)
        
        except Exception as e:
            logger.error(f"Erro ao processar resposta estruturada: {e}")
            # Fallback para processamento legado
            return None

    def _call_gemini(self, prompt: str, image_path: Optional[str] = None):
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

    def _call_ollama(self, prompt: str, image_path: str, model: str = "llava"):
        """Integração com Ollama Local (Multi-modelo)"""
        try:
            import base64
            image_data = None
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Tenta usar o modelo especificado (padrão 'llava' para visão)
            payload = {
                "model": model,
                "prompt": f"{self.system_prompt}\n\nComando: {prompt}",
                "stream": False
            }
            if image_data:
                payload["images"] = [image_data]

            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data.get('response', "Senhor, não obtive resposta do processador local.")

        except Exception as e:
            logger.error(f"Erro ao chamar Ollama ({model}): {e}")
            return f"Infelizmente estou com dificuldades no processamento offline: {str(e)}."

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
