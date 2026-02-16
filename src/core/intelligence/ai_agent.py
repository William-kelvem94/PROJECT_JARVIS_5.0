"""
Orquestrador do Agente de IA
Gerencia interaÃ§Ã£o entre visÃ£o (OCR), decisÃ£o (LLM) e aÃ§Ã£o (PyAutoGUI)
"""

import logging
import os
import requests
import aiohttp
import json
import re
import time
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.core.intelligence.instinct_engine import instinct_engine
from src.utils.hardware_control import hw_control
from src.core.management.context_manager import context_manager
try:
    from src.core.audio.voice_filter import AtomicVoiceFilter
except Exception as e:
    logger.error(f"❌ Falha ao importar AtomicVoiceFilter: {e}")
    AtomicVoiceFilter = None
from src.utils.logger_reflection import reflect_logger
try:
    from src.utils.env_manager import get_model_for_tier
except ImportError:
    get_model_for_tier = lambda tier: 'deepseek-r1:8b'  # Fallback
from src.interface.ui_signals import ui_signals

# Enable Neural Reflection by default for luxury diagnostics
reflect_logger.set_enabled(True)

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
    logger.warning(f"âš ï¸ Database models nÃ£o disponÃ­vel: {e}")
    db_manager = None
    OCRResult = None

try:
    from src.core.vision.screen_capture import screen_capture
except ImportError as e:
    logger.error(f"âŒ CRÃTICO: screen_capture nÃ£o disponÃ­vel: {e}")
    screen_capture = None

try:
    from src.core.actions.action_controller import action_controller
except ImportError as e:
    logger.error(f"âŒ CRÃTICO: action_controller nÃ£o disponÃ­vel: {e}")
    action_controller = None

try:
    from src.core.audio.voice_controller import voice_controller
except ImportError as e:
    logger.warning(f"âš ï¸ voice_controller nÃ£o disponÃ­vel: {e}")
    voice_controller = None

try:
    from src.core.vision.camera_controller import camera_controller
except ImportError as e:
    logger.warning(f"âš ï¸ camera_controller nÃ£o disponÃ­vel: {e}")
    camera_controller = None

try:
    from src.core.management.dataset_collector import dataset_collector
except ImportError as e:
    logger.warning(f"âš ï¸ dataset_collector nÃ£o disponÃ­vel: {e}")
    dataset_collector = None

try:
    from src.core.intelligence.brain_router import brain_router, PrivacyLevel, LatencyRequirement
    logger.info("âœ… Brain Router carregado (Decision Engine)")
except ImportError as e:
    logger.warning(f"âš ï¸ brain_router nÃ£o disponÃ­vel: {e}")
    brain_router = None

try:
    from src.core.management.hardware_manager import hardware_manager
except ImportError as e:
    logger.warning(f"âš ï¸ hardware_manager nÃ£o disponÃ­vel: {e}")
    hardware_manager = None

try:
    from src.core.intelligence.local_brain import local_brain
except ImportError as e:
    logger.warning(f"âš ï¸ local_brain nÃ£o disponÃ­vel: {e}")
    local_brain = None

try:
    from src.core.vision.ui_detector import ui_detector
except ImportError as e:
    logger.warning(f"âš ï¸ ui_detector nÃ£o disponÃ­vel: {e}")
    ui_detector = None

try:
    from src.core.intelligence.emotion_detector import emotion_detector
except ImportError as e:
    logger.warning(f"âš ï¸ emotion_detector nÃ£o disponÃ­vel: {e}")
    emotion_detector = None

try:
    from src.utils.web_search_tool import web_search_tool
except ImportError as e:
    logger.warning(f"âš ï¸ web_search_tool nÃ£o disponÃ­vel: {e}")
    web_search_tool = None

# Security Manager (Lazy Load)
security_manager = None

# ============================================================================
# GOD MODE - SYSTEM CONTROLLER (NEW)
# ============================================================================
try:
    from src.core.actions.system_controller import system_controller
    logger.info("âœ… System Controller carregado (God Mode)")
except ImportError as e:
    logger.warning(f"âš ï¸ system_controller nÃ£o disponÃ­vel: {e}")
    system_controller = None

# ============================================================================
# PHASE 2 - CODE GENERATOR (AUTO-PROGRAMMING)
# ============================================================================
try:
    from src.core.engine.code_generator import code_generator
    logger.info("âœ… Code Generator carregado (Auto-Programming)")
except ImportError as e:
    logger.warning(f"âš ï¸ code_generator nÃ£o disponÃ­vel: {e}")
    code_generator = None

# ============================================================================
# PHASE 3 - MEMORY MANAGER (AUTO-LEARNING / RAG)
# ============================================================================
try:
    from src.core.intelligence.memory import memory_manager
    logger.info("✅ Unified Memory Manager loaded")
except ImportError as e:
    logger.warning(f"⚠️ memory_manager not available: {e}")
    memory_manager = None

# ============================================================================
# PHASE 6 - LEARNING ENGINE (CONTINUAL LEARNING / AGI)
# ============================================================================
try:
    from src.learning.learning_engine import get_learning_engine
    logger.info("âœ… Learning Engine carregado (Continual Evolution)")
except ImportError as e:
    logger.warning(f"âš ï¸ learning_engine nÃ£o disponÃ­vel: {e}")
    get_learning_engine = None

# ============================================================================
# PHASE 4 - VISION ENHANCER (ADVANCED UI DETECTION)
# ============================================================================
try:
    from src.core.vision.vision_enhancer import vision_enhancer
    logger.info("âœ… Vision Enhancer carregado (YOLO + OCR)")
except ImportError as e:
    logger.warning(f"âš ï¸ vision_enhancer nÃ£o disponÃ­vel: {e}")
    vision_enhancer = None

# ============================================================================
# PHASE 5 - PERFORMANCE OPTIMIZER (FINAL PHASE)
# ============================================================================
try:
    from src.core.management.performance_optimizer import performance_optimizer
    logger.info("âœ… Performance Optimizer carregado (Cache + Metrics)")
except ImportError as e:
    logger.warning(f"âš ï¸ performance_optimizer nÃ£o disponÃ­vel: {e}")
    performance_optimizer = None

# ============================================================================
# CORREÃ‡ÃƒO P1 - STRUCTURED OUTPUT & ACTION EXECUTOR
# ============================================================================
try:
    from src.core.intelligence.structured_output import (
        ResponseParser,
        get_actions_schema,
        get_example_responses,
        AgentResponse,
    )
    from src.core.actions import get_action_executor
    from src.core.actions import get_action_handler
    STRUCTURED_OUTPUT_AVAILABLE = True
    logger.info("âœ… Structured Output & Action Executor carregados (P1)")
except ImportError as e:
    logger.warning(f"âš ï¸ Structured Output nÃ£o disponÃ­vel: {e}")
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
    from src.learning.neural_curiosity import neural_curiosity
    logger.info("âœ… MÃ³dulos Stark Phase 2/4 carregados (Contexto + Nexus + Device + Dreaming + Curiosity)")
except ImportError as e:
    logger.warning(f"âš ï¸ Falha ao carregar MÃ³dulos Stark Phase 2/4: {e}")
    analisador_contexto = None
    stark_nexus = None
    device_manager = None
    neural_dreaming = None
    
try:
    from src.core.vision.os_monitor import get_active_window_context
    from src.core.security.action_validator import action_validator
    logger.info("âœ… FASE 3: Jaula de Vidro (OS Monitor + Action Validator) ativa")
except ImportError as e:
    logger.warning(f"âš ï¸ Falha ao carregar MÃ³dulos Fase 3: {e}")
    get_active_window_context = lambda: {"title": "Unknown", "executable": "Unknown", "process_name": "Unknown"}
    action_validator = None

try:
    from src.utils.config import config
except ImportError as e:
    logger.warning(f"âš ï¸ config nÃ£o disponÃ­vel: {e}")
    # Create dummy config
    class DummyConfig:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        def get_ai_config(self, key=None, default=None):
            """Fallback para quando config nÃ£o carrega"""
            return default if default is not None else {}
            
    config = DummyConfig()

try:
    from src.utils.web_emitter import emit_status_sync, emit_log_sync
except ImportError:
    emit_status_sync = lambda *args, **kwargs: None
    emit_log_sync = lambda *args, **kwargs: None

# ============================================================================
# ADVANCED MODULES (JARVIS EVOLUTION) - SAFE LOADING
# ============================================================================
try:
    from src.core.actions.advanced_action_controller import advanced_action_controller
    ADVANCED_ACTIONS_AVAILABLE = True
    logger.info("âœ… Advanced Action Controller carregado")
except ImportError:
    ADVANCED_ACTIONS_AVAILABLE = False
    advanced_action_controller = None
    logger.warning("âš ï¸ Advanced Action Controller nÃ£o disponÃ­vel")

try:
    from src.core.vision.advanced_vision_pipeline import advanced_vision_pipeline
    ADVANCED_VISION_AVAILABLE = True
    logger.info("âœ… Advanced Vision Pipeline carregado")
except ImportError:
    ADVANCED_VISION_AVAILABLE = False
    advanced_vision_pipeline = None
    logger.warning("âš ï¸ Advanced Vision Pipeline nÃ£o disponÃ­vel")

try:
    from src.core.audio.advanced_speech_processor import advanced_speech_processor
    ADVANCED_SPEECH_AVAILABLE = True
    logger.info("âœ… Advanced Speech Processor carregado")
except ImportError:
    ADVANCED_SPEECH_AVAILABLE = False
    advanced_speech_processor = None
    logger.warning("âš ï¸ Advanced Speech Processor nÃ£o disponÃ­vel")

try:
    from src.core.actions.workflow_engine import workflow_engine
    WORKFLOW_ENGINE_AVAILABLE = True
    logger.info("âœ… Workflow Engine carregado")
except ImportError:
    WORKFLOW_ENGINE_AVAILABLE = False
    workflow_engine = None
    logger.warning("âš ï¸ Workflow Engine nÃ£o disponÃ­vel")

try:
    from src.core.security.security_manager_advanced import security_manager as security_manager_advanced
    ADVANCED_SECURITY_AVAILABLE = True
    logger.info("âœ… Advanced Security Manager carregado")
except ImportError:
    ADVANCED_SECURITY_AVAILABLE = False
    security_manager_advanced = None
    logger.warning("âš ï¸ Advanced Security Manager nÃ£o disponÃ­vel")

try:
    from src.learning.curiosity_engine import CuriosityEngine
    curiosity_engine = CuriosityEngine()
except ImportError:
    curiosity_engine = None

try:
    from src.core.intelligence.ai_tools import get_ai_tools
    ai_tools = get_ai_tools()
except ImportError:
    ai_tools = None

class AIAgent:
    """Classe principal do Agente Inteligente"""

    def __init__(self, provider: str = 'ollama'):
        # =====================================================================
        # ðŸ†• AUTO-RECOVERY INTEGRATION
        # =====================================================================
        self.auto_recovery = None
        self._initialize_auto_recovery()

        # =====================================================================
        # CORREÃ‡ÃƒO P0: VERIFICAÃ‡ÃƒO DE DEPENDÃŠNCIAS CRÃTICAS
        # =====================================================================
        self.safe_mode = False
        self._verify_critical_dependencies()
        
        self.provider = provider
        self.api_key = None # 100% Local Mode
        
        # Carregar URL do Ollama do env_manager
        try:
            from src.utils.env_manager import get_config
            config_obj = get_config()
            self.ollama_url = config_obj.ollama_url + "/api/generate" if config_obj else "http://localhost:11434/api/generate"
        except ImportError:
            self.ollama_url = "http://localhost:11434/api/generate"
        
        # Carregar configuraÃ§Ãµes de IA
        try:
            from src.utils.config import config
            self.ai_config = config.get_ai_config()
            self.max_react_turns = config.get_ai_config('ai_agent.max_react_turns', 5)
            self.screenshot_timeout = config.get_ai_config('ai_agent.screenshot_timeout', 5.0)
            logger.info("âœ… ConfiguraÃ§Ãµes de IA carregadas")
        except Exception as e:
            logger.warning(f"âš ï¸ Erro ao carregar ai_config, usando defaults: {e}")
            self.ai_config = {}
            self.max_react_turns = 5
            self.screenshot_timeout = 5.0
        
        # HistÃ³rico de conversaÃ§Ã£o
        self.chat_history = []
        
        # Brain Router - Sistema de DecisÃ£o Inteligente
        try:
            from src.core.intelligence.brain_router import brain_router
            self.brain_router = brain_router
            logger.info("âœ… Brain Router inicializado")
            
            # ðŸ†• FASE 2: Conectar UX Masking
            if self.brain_router:
                self.brain_router.on_heavy_model_loading = self._on_heavy_model_loading
        except Exception as e:
            logger.warning(f"âš ï¸ Brain Router nÃ£o disponÃ­vel: {e}")
            self.brain_router = None
        
        # Advanced Controllers
        self.advanced_actions = advanced_action_controller if ADVANCED_ACTIONS_AVAILABLE else None
        self.advanced_vision = advanced_vision_pipeline if ADVANCED_VISION_AVAILABLE else None
        self.advanced_speech = advanced_speech_processor if ADVANCED_SPEECH_AVAILABLE else None
        self.workflow_engine = workflow_engine if WORKFLOW_ENGINE_AVAILABLE else None
        self.security_advanced = security_manager_advanced if ADVANCED_SECURITY_AVAILABLE else None
        
        if self.advanced_actions:
            logger.info("âœ… Advanced Action Controller carregado")
        if self.advanced_vision:
            logger.info("âœ… Advanced Vision Pipeline carregado")
        if self.advanced_speech:
            logger.info("âœ… Advanced Speech Processor carregado")
        if self.workflow_engine:
            logger.info("âœ… Workflow Engine carregado")
        
        # =====================================================================
        # AGENT DELEGATES (PROMPTS, ENGAGEMENT)
        # =====================================================================
        from .agent.prompt_manager import AgentPromptManager
        from .agent.engagement_manager import AgentEngagementManager
        
        self.prompt_manager = AgentPromptManager()
        self.engagement_manager = AgentEngagementManager(self)
        
        self.system_prompt = self.prompt_manager.get_system_prompt()
        self.use_structured_output = STRUCTURED_OUTPUT_AVAILABLE
        
        # [EVENT BUS]
        self.event_bus = None

    def connect_event_bus(self, event_bus):
        """Connects AI Agent to AsyncEventBus for pub/sub communication"""
        from src.core.infrastructure.async_event_bus import EventType
        self.event_bus = event_bus
        if self.event_bus:
            logger.info("✅ AI Agent connected to AsyncEventBus.")
            
            # [PHASE 2.3] Proactive Vision Trigger
            import asyncio
            asyncio.create_task(self.event_bus.subscribe(EventType.VISION_SCREEN_CHANGE, self._handle_vision_event))

    def _get_security_manager(self):
        """Lazy load SecurityManager to avoid circular imports"""
        global security_manager
        if security_manager is None:
            try:
                from src.core.security.security_manager import SecurityManager
                security_manager = SecurityManager()
            except ImportError:
                logger.warning("âš ï¸ SecurityManager unavailable, using dummy fallback")
                class DummySecurityManager:
                    def validate_file_action(self, *args, **kwargs): return True
                    def validate_web_request(self, *args, **kwargs): return True
                security_manager = DummySecurityManager()
        return security_manager
    
    def _verify_critical_dependencies(self):
        """
        Verifica dependÃªncias crÃ­ticas e define modo seguro se necessÃ¡rio.
        
        CorreÃ§Ã£o P0: Detecta dependÃªncias faltantes e impede operaÃ§Ã£o parcial.
        CorreÃ§Ã£o P3: Valida funcionalidade runtime (nÃ£o sÃ³ importaÃ§Ã£o).
        """
        critical_modules = {
            'voice_controller': voice_controller,
            'vision_enhancer': vision_enhancer,
            'screen_capture': screen_capture,
            'action_controller': action_controller,
        }
        
        important_for_quality = {
            'structured_output': STRUCTURED_OUTPUT_AVAILABLE,
            'brain_router': brain_router is not None,
            'voice_controller': voice_controller is not None,
            'memory_manager': memory_manager is not None,
            'local_brain': local_brain is not None,
        }
        
        missing_critical = [name for name, module in critical_modules.items() if module is None]
        degraded = [name for name, ok in important_for_quality.items() if not ok]
        
        if missing_critical:
            self.safe_mode = True
            logger.critical(f"âŒ DEPENDÃŠNCIAS CRÃTICAS FALTANDO: {missing_critical}")
            logger.critical("ðŸ”’ INICIANDO EM MODO SEGURO - Funcionalidade limitada")
            logger.critical("ðŸ’¡ Execute: pip install -r requirements.txt")
        else:
            self.safe_mode = False
            logger.info("âœ… Todas as dependÃªncias crÃ­ticas disponÃ­veis")
        
        if degraded:
            logger.warning(f"âš ï¸ MÃ³dulos degradados: {degraded}")
            if 'structured_output' in degraded:
                logger.warning("âš ï¸ Structured Output indisponÃ­vel â†’ fallback para regex (menos confiÃ¡vel)")
            if 'local_brain' in degraded:
                logger.warning("âš ï¸ Local Brain indisponÃ­vel â†’ agente depende 100% de cloud/ollama")
        
        # P3: Runtime health â€” verificar status do Local Brain
        if local_brain is not None:
            model_loaded = getattr(local_brain, 'model', None) is not None
            is_loading = getattr(local_brain, '_is_loading', False)
            
            if model_loaded:
                logger.info("âœ… Local Brain totalmente carregado e pronto.")
            elif is_loading:
                logger.info("â³ Local Brain estÃ¡ inicializando em background...")
            else:
                logger.info("â„¹ï¸ Local Brain em modo de espera (Lazy Load ou Cloud-Only)")
        
        # P3: Verificar se hÃ¡ pelo menos UM provider LLM disponÃ­vel
        has_api_key = bool(os.environ.get('GOOGLE_API_KEY'))
        has_local = local_brain is not None and getattr(local_brain, 'model', None) is not None
        has_ollama = brain_router is not None
        
        if not has_api_key and not has_local and not has_ollama:
            logger.critical("âŒ NENHUM PROVIDER LLM DISPONÃVEL (sem API key, sem modelo local, sem ollama)")
            logger.critical("ðŸ’¡ Configure GOOGLE_API_KEY ou instale um modelo local")
        
        # ðŸ†• AUTO-RECOVERY: Log critical issues for automatic recovery
        if self.auto_recovery and missing_critical:
            from src.core.management.universal_recovery_manager import FailureType
            for module in missing_critical:
                self.auto_recovery._trigger_recovery(
                    failure_type=FailureType.IMPORT_ERROR,
                    module_name=module,
                    error_message=f"Critical module {module} is missing",
                    severity=9
                )
    
    def _should_engage(self, text: str) -> bool:
        """Delegates engagement decision to manager."""
        return self.engagement_manager.should_engage(text)

    def _prepare_intent(self, text: str) -> str:
        """
        Em vez de apenas remover, isola a intenção mas mantém o tom original para a LLM.
        """
        # Mantemos o texto original para não perder o contexto emocional/educado
        return text.strip()

    def _passive_observation(self):
        """Delegates passive observation to manager."""
        try:
            asyncio.create_task(self.engagement_manager.passive_observation_cycle())
        except Exception:
            pass

    async def _handle_contextual_observation(self, current_intent: str):
        """
        Lógica de Observação Adaptativa: O sistema decide o que monitorar 
        baseado na intenção aprendida e no contexto ambiental.
        """
        # A IA decide se deve ativar vigilância, monitorar workflow ou ser discreta
        context = await self.context_manager.get_full_state()
        
        # O comportamento não é fixo, ele evolui com a UserManager
        current_user = user_manager.get_active_user()
        user_name = current_user.name if current_user else "usuário"
        
        if "vigilância" in current_intent or context['is_user_absent']:
            # A IA decide o que é necessário coletar (fotos, logs, etc)
            await self._execute_adaptive_surveillance(context)

    async def _execute_adaptive_surveillance(self, context: dict):
        """Executa ações de monitoramento decididas dinamicamente pela IA"""
        results = []
        # Ele decide usar os sensores disponíveis sem ordens fixas
        if camera_controller: results.append(camera_controller.capture_context())
        if screen_capture: results.append(screen_capture.capture_context())
        
        # Armazena na memória de longo prazo para análise posterior
        memory_manager.store_experience("surveillance_event", results)

    def _generate_discreet_response(self, core_message: str) -> str:
        """
        Usa a LLM para transformar uma mensagem direta em algo 
        discreto se houver mais pessoas presentes.
        """
        is_private = camera_controller.is_private_env() if camera_controller else True
        if is_private:
            return core_message
            
        # Fallback de discrição (A IA aprenderá formas melhores com o tempo)
        discreet_versions = {
            "alguém mexeu no PC": "Senhor, os relatórios de integridade foram atualizados.",
            "intruso detectado": "Há uma notificação de segurança pendente no seu painel."
        }
        return discreet_versions.get(core_message, "Há uma nova atualização no sistema.")

    async def _move_mouse_cooperatively(self, x, y):
        """Move o mouse respeitando o uso do usuário (Yield on Move)"""
        import pyautogui
        last_pos = pyautogui.position()
        
        # Se o usuário mexer o mouse, nós esperamos
        while True:
            current_pos = pyautogui.position()
            if current_pos != last_pos:
                # Usuário está no controle, esperamos...
                logger.debug("🖱️ Usuário detectado no mouse. JARVIS aguardando...")
                await asyncio.sleep(2)
                last_pos = pyautogui.position()
                continue
            
            # Se ninguém mexeu por 2 segundos, nós agimos
            pyautogui.moveTo(x, y, duration=1.0)
            break

    def _initialize_auto_recovery(self):
        """Initialize auto-recovery system integration"""
        try:
            from src.core.management.universal_recovery_manager import get_universal_recovery_manager, register_module_for_monitoring
            self.auto_recovery = get_universal_recovery_manager()
            
            # Register AI Agent as a monitored module
            register_module_for_monitoring("ai_agent")
            
            # Register health check callback
            if hasattr(self.auto_recovery, 'register_health_callback'):
                self.auto_recovery.register_health_callback("ai_agent", self._health_check)
                
            logger.info("🔧 AI Agent auto-recovery integration established")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize auto-recovery integration: {e}")
    
    def _health_check(self) -> Dict[str, Any]:
        """Health check for auto-recovery monitoring"""
        try:
            return {
                "status": "healthy" if not self.safe_mode else "degraded",
                "safe_mode": self.safe_mode,
                "provider": self.provider,
                "brain_router_available": self.brain_router is not None,
                "last_interaction": getattr(self, 'last_interaction_time', None)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _handle_critical_error(self, error: Exception, context: str = "unknown"):
        """Handle critical errors with auto-recovery"""
        if self.auto_recovery:
            try:
                from src.core.management.universal_recovery_manager import trigger_recovery_for_exception
                trigger_recovery_for_exception("ai_agent", error, severity=8)
                logger.info(f"ðŸ”§ Auto-recovery triggered for AI Agent error in {context}")
            except Exception as e:
                logger.error(f"âŒ Failed to trigger auto-recovery: {e}")
        
        # Set safe mode if error is critical
        if isinstance(error, (ImportError, MemoryError)):
            self.safe_mode = True
            logger.critical("ðŸ”’ AI Agent entering safe mode due to critical error")
        
    def _on_heavy_model_loading(self, message: str):
        """
        Callback para UX Masking (Fase 2):
        Informa o usuÃ¡rio quando um modelo pesado estÃ¡ sendo carregado.
        """
        try:
            if voice_controller:
                # Falar imediatamente (sem esperar fila se possÃ­vel)
                # Usar thread separada para nÃ£o bloquear o carregamento do modelo
                threading.Thread(target=voice_controller.speak, args=(message,), daemon=True).start()
            else:
                logger.info(f"ðŸ¤ (Sem Voz) UX Masking: {message}")
        except Exception as e:
            logger.warning(f"âš ï¸ Falha no UX Masking: {e}")

    def _request_human_authorization(self, action_description: str) -> bool:
        """
        HITL (Human-In-The-Loop) - Protocolo de SeguranÃ§a Fase 3
        Pede autorizaÃ§Ã£o por voz com timeout de seguranÃ§a.
        Retorna True se autorizado, False se negado ou timeout.
        """
        if not voice_controller:
            logger.warning("HITL: Voice Controller nÃ£o disponÃ­vel. Bloqueando por seguranÃ§a.")
            return False

        # Lazy load SecurityManager para log ou validaÃ§Ã£o adicional
        self._get_security_manager()

        try:
            # 1. Anunciar a aÃ§Ã£o
            msg = f"AtenÃ§Ã£o. AutorizaÃ§Ã£o requerida para: {action_description}. Diga sim para autorizar, ou nÃ£o para cancelar."
            logger.info(f"ðŸ›‘ HITL Request: {action_description}")
            voice_controller.speak(msg, wait=True)
            
            # 2. Escuta com Timeout (10s) - Fail-Safe
            # Usando o mÃ©todo confirm_with_voice do controller se disponÃ­vel, ou implementando lÃ³gica raw
            if hasattr(voice_controller, 'confirm_with_voice'):
                # O mÃ©todo do controller jÃ¡ implementa a lÃ³gica de escuta e validaÃ§Ã£o
                authorized = voice_controller.confirm_with_voice("Aguardando confirmaÃ§Ã£o...", timeout=10)
            else:
                # Fallback se o mÃ©todo nÃ£o existir no controller (versÃ£o antiga)
                logger.warning("VoiceController.confirm_with_voice nÃ£o encontrado. Bloqueando.")
                return False

            if authorized:
                voice_controller.speak("Autorizado. Executando.", wait=False)
                logger.info("âœ… HITL: AÃ§Ã£o AUTORIZADA pelo usuÃ¡rio.")
                return True
            else:
                voice_controller.speak("AÃ§Ã£o cancelada.", wait=False)
                logger.warning("âŒ HITL: AÃ§Ã£o NEGADA pelo usuÃ¡rio.")
                return False

        except Exception as e:
            logger.error(f"Erro no protocolo HITL: {e}")
            if voice_controller:
                voice_controller.speak("Erro na verificaÃ§Ã£o de seguranÃ§a. AÃ§Ã£o abortada.")
            return False

    def greet_user_on_startup(self, system_health: dict = None):
        """
        ðŸŒŸ SPARK OF LIFE: Gera saudaÃ§Ã£o espontÃ¢nea e humana ao iniciar.
        
        NÃ£o usa frases prontas. Usa o cÃ©rebro (LLM) para 'sentir' o momento
        e criar uma apresentaÃ§Ã£o Ãºnica a cada boot.
        
        Args:
            system_health: Dict com status de componentes (opcional)
                          Ex: {"ai_agent": True, "vision": True, "audio": True, ...}
        """
        if not voice_controller:
            logger.warning("âš ï¸ Voice controller indisponÃ­vel para saudaÃ§Ã£o.")
            return
        
        try:
            import datetime
            now = datetime.datetime.now()
            hora = now.hour
            
            # 1. CONTEXTO TEMPORAL
            periodo = (
                "madrugada" if 0 <= hora < 6 else
                "manhÃ£" if 6 <= hora < 12 else
                "tarde" if 12 <= hora < 18 else
                "noite"
            )
            hora_formatada = now.strftime("%H:%M")
            
            # 2. CONTEXTO DO SISTEMA
            status_info = ""
            if system_health:
                ativos = sum(1 for v in system_health.values() if v)
                total = len(system_health)
                tier = getattr(hardware_manager, 'tier', 'BALANCED')
                gpu_name = getattr(hardware_manager, 'gpu_name', 'CPU')
                
                status_info = (
                    f"- {ativos}/{total} mÃ³dulos principais carregados com sucesso\\n"
                    f"- Hardware: {tier} tier ({gpu_name})\\n"
                )
            
            # 3. CONTEXTO EMOCIONAL (se cÃ¢mera disponÃ­vel)
            emocao_detectada = ""
            try:
                from src.core.vision.camera_controller import camera_controller
                if camera_controller and hasattr(camera_controller, 'current_emotion'):
                    emocao = camera_controller.current_emotion
                    if emocao and emocao != "neutral":
                        emocao_detectada = f"- Sua expressÃ£o atual parece: {emocao}\\n"
            except:
                pass
            
            # 4. PROMPT ENGINEERING (Criatividade Total)
            prompt_saudacao = f"""VocÃª Ã© JARVIS, o assistente pessoal do William. VocÃª acabou de iniciar seus sistemas agora de {periodo} (sÃ£o {hora_formatada}).

**Status atual:**
{status_info}{emocao_detectada}

**Tarefa:** Gere UMA ÃšNICA frase de saudaÃ§Ã£o curta, elegante e natural para dizer ao William que vocÃª estÃ¡ pronto.

**Regras imperativas:**
1. Use "William", "senhor" ou "chefe" (NUNCA "usuÃ¡rio")
2. NÃƒO liste logs tÃ©cnicos (ex: "mÃ³dulo X carregado com sucesso")
3. Seja humano e imprevisÃ­vel - cada boot deve soar diferente
4. Varie entre: sarcÃ¡stico (Tony Stark), formal britÃ¢nico (JARVIS clÃ¡ssico), ou motivador
5. Se for madrugada/noite tarde, pode comentar sobre a hora
6. MÃ¡ximo 2 frases curtas

**Exemplos de vibe (NÃƒO COPIE, apenas inspire-se):**
- "Sistemas online, William. {periodo} tranquil{'a' if periodo in ['manhÃ£', 'tarde', 'madrugada'] else 'a'}. O que vamos criar hoje?"
- "Sistemas online, William. {periodo} tranquila. O que vamos criar hoje?"
- "E aÃ­, chefe. Acabei de sincronizar. Pronto para bagunÃ§ar o cÃ³digo ou concertar o mundo?"
- "Boa {periodo}, senhor. CÃ©rebro 100%, visÃ£o calibrada. Como posso ajudar?"

**IMPORTANTE:** Responda APENAS a frase falada. Sem explicaÃ§Ãµes ou formataÃ§Ã£o extra."""

            # 5. GERAR SAUDAÃ‡ÃƒO VIA LLM (Robust Smart Switching)
            resposta_viva = ""
            try:
                logger.info("ðŸ§  Gerando saudaÃ§Ã£o inteligente (Smart Switching)...")
                resposta_viva = self._call_smart_brain(
                    prompt_saudacao,
                    complexity=0.2,  # Baixa complexidade = prioriza tier_fast (Qwen 1.5B/3B)
                    system_prompt="VocÃª Ã© JARVIS. Responda APENAS com texto natural e humano. NUNCA use JSON, chaves ou formataÃ§Ã£o tÃ©cnica. Fale diretamente com o William."
                )
            except Exception as e:
                logger.warning(f"Falha na saudaÃ§Ã£o inteligente: {e}")
            
            # 6. FALAR A SAUDAÃ‡ÃƒO
            # ðŸŒŸ Refinamento: Validar se a resposta nÃ£o Ã© uma mensagem de erro tÃ©cnico
            technical_errors = ["httpconnectionpool", "timed out", "api_key", "error", "falhou", "indisponÃ­vel", "servidor", "not found"]
            is_technical_error = any(err in resposta_viva.lower() for err in technical_errors) if resposta_viva else True

            if resposta_viva and len(resposta_viva.strip()) > 5 and not is_technical_error:
                # Limpar possÃ­vel lixo (Ã s vezes o LLM adiciona aspas ou prefixos)
                resposta_viva = resposta_viva.strip().strip('"').strip("'").strip(".").strip()
                
                logger.info(f"JARVIS Real Startup Greeting: {resposta_viva}")
                if voice_controller:
                    voice_controller.speak(resposta_viva)
                else:
                    logger.warning("voice_controller indisponivel - saudacao apenas registrada")
            else:
                # No Funcionamento Real, nÃ£o usamos fallbacks estÃ¡ticos a menos que seja falha total
                logger.warning(f"âš ï¸ Resposta curta ou invÃ¡lida do LLM: '{resposta_viva}'")
                if "Sistemas online" not in resposta_viva:
                    voice_controller.speak(resposta_viva if resposta_viva else "Iniciando protocolos neurais, William.")
        
        except Exception as e:
            logger.error(f"âŒ Erro crÃ­tico na saudaÃ§Ã£o inicial: {e}")
            # Ãšltimo recurso
            try:
                voice_controller.speak("Sistemas prontos.")
            except:
                pass

    async def process_command(self, user_command: str) -> str:
        """
        Recebe um comando (texto ou voz), captura a tela e decide o que fazer
        """
        all_actions = [] # Rastreamento para Fase 4 (DestilaÃ§Ã£o)
        original_command = user_command
        logger.info(f"Agente processando comando: {user_command}")
        
        # 🎨 FASE 5: Feedback Visual (Pensando)
        ui_signals.update_status.emit("Analisando comando do Senhor...")

        # =====================================================================
        # PHASE: INSTINCT LAYER (QUICK RESPONSE - ZERO LATENCY)
        # =====================================================================
        # Antes de ir para a LLM, verificamos se é um comando trivial
        instinct_result = await instinct_engine.check(user_command)
        if instinct_result:
            logger.info("⚡ Comando resolvido pela camada de Instinto.")
            
            # 1. Tratamento Especial: Renomeação
            if "identify_self" in instinct_result.get("name", "") and "seu novo nome é" in user_command.lower():
                new_name = user_command.lower().split("seu novo nome é")[-1].strip()
                if AtomicVoiceFilter.set_primary_name(new_name):
                    instinct_result["final_answer"] = f"Entendido, Senhor. De agora em diante, atenderei pelo nome de {new_name}."
            
            # 2. Tratamento Especial: Modo Noturno / Foco
            if "enable_night_mode" in instinct_result.get("name", ""):
                context_manager.night_mode = True
            elif "disable_night_mode" in instinct_result.get("name", ""):
                context_manager.night_mode = False
            
            # Se for um comando de erro, buscamos os erros reais agora
            if "get_last_system_error" in [a.get("action") for a in instinct_result.get("actions", [])]:
                errors = hw_control.get_last_system_errors()
                instinct_result["final_answer"] = f"Senhor, analisei os logs do sistema. Aqui estão os últimos registros: {errors}"
            
            # Executar ações de instinto
            if instinct_result.get("actions") and action_controller:
                for action in instinct_result["actions"]:
                    if action["action"] == "set_volume":
                        hw_control.set_system_volume(action["level"])
            
            # POLITENESS & NIGHT MODE CHECK before speaking
            if voice_controller:
                if context_manager.should_be_quiet():
                    # No modo quieto, apenas mostra no HUD/Log
                    logger.info(f"🤫 (Silent Mode) JARVIS: {instinct_result['final_answer']}")
                    ui_signals.update_status.emit(instinct_result["final_answer"])
                else:
                    voice_controller.speak(instinct_result["final_answer"])
            return instinct_result["final_answer"]

        # =====================================================================
        # PHASE: MULTI-MODAL ENGAGEMENT CHECK
        # =====================================================================
        if not self._should_engage(user_command):
            logger.debug("Silenciando: Fala não direcionada ao JARVIS.")
            return None

        # Prepara a intenção mantendo o contexto emocional
        intent_command = self._prepare_intent(user_command)
        logger.debug(f"Processando intenção: {intent_command}")

        # CORREÇÃO P0: VERIFICAÇÃO DE MODO SEGURO
        # =====================================================================
        if self.safe_mode:
            error_msg = (
                "Sistema em MODO SEGURO devido a dependÃªncias crÃ­ticas faltando. "
                "Por favor, instale as dependÃªncias necessÃ¡rias executando: pip install -r requirements.txt"
            )
            logger.error(f"âŒ {error_msg}")
            if voice_controller:
                voice_controller.speak("Sistema em modo seguro. Funcionalidade limitada.")
            return error_msg
        
        # =====================================================================
        # PHASE 5: PERFORMANCE - CHECK CACHE FIRST
        # =====================================================================
        if performance_optimizer:
            cached_response = performance_optimizer.get_cached_response(user_command)
            if cached_response:
                logger.info("âš¡ Usando resposta em cache (ultra-rÃ¡pido)")
                if voice_controller:
                    voice_controller.speak(cached_response)
                return cached_response
        
        # =====================================================================
        # PHASE: HYBRID QUICKRESPONSE ROUTER (LATENCY ZERO)
        # =====================================================================
        # 3. Capturar estado atual da tela e janela (PARALELO)
        screenshot_event = threading.Event()
        screenshot_container = {"image_data": None, "window_info": None}

        def _capture_task():
            screenshot_container["image_data"] = screen_capture.capture_fullscreen(capture_type='agent', return_image=True)
            # ðŸ†• FASE 3: OS Monitor (Leve e RÃ¡pido)
            screenshot_container["window_info"] = get_active_window_context()
            screenshot_event.set()

        capture_thread = threading.Thread(target=_capture_task, daemon=True)
        capture_thread.start()

        # Aguardar screenshot (Async Wrapper)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, screenshot_event.wait, 2.0)
        
        screenshot_image = screenshot_container["image_data"]
        window_info = screenshot_container["window_info"]
        
        vision_text = ""
        if screenshot_image and vision_enhancer:
            current_app = window_info.get('process_name', window_info.get('executable', '?'))
            reflect_logger.reflect(f"ðŸ‘ï¸ Analisando ambiente visual (App: {current_app})...", layer="VISION")
            v_res = vision_enhancer.analyze_screen(image_data=screenshot_image, detect_ui=False, extract_text=True)
            vision_text = " ".join([t['text'] for t in v_res.get('text_regions', [])])

        # =====================================================================
        # PHASE: NEURAL CURIOSITY (PROACTIVE LEARNING)
        # =====================================================================
        proactive_question = None
        from src.core.intelligence.analisador_contexto import analisador_contexto
        contexto_data = analisador_contexto.analisar(user_command, vision_text=vision_text, window_info=window_info)
        
        if 'neural_curiosity' in globals() or 'neural_curiosity' in locals():
            proactive_question = neural_curiosity.check_learning_opportunity(contexto_data, user_command)
            if proactive_question:
                logger.info(f"âœ¨ Proactively engaging user for learning: {proactive_question}")

        # =====================================================================
        # PHASE 4: GOLDEN COMMANDS & MEMORY
        # =====================================================================
        memory_context = ""
        if memory_manager and memory_manager.collection:
            try:
                memory_context = memory_manager.get_context(user_command, max_memories=3)
            except Exception as e:
                logger.error(f"Error retrieving memory context: {e}")
                memory_context = ""
        
        if knowledge_distiller:
            golden_context = knowledge_distiller.get_relevant_examples(user_command)
            if golden_context:
                memory_context = f"{golden_context}\n{memory_context}"
                logger.info("âœ¨ Golden Commands injetados para aprendizado few-shot")
        
        # ... (Steps 1-3 unchanged) ...
        # 1. BRAIN ROUTING (Intelligent Decision)
        if self.brain_router:
            # Decide o cÃ©rebro baseado na complexidade estimada
            # Estimativa bÃ¡sica: tamanho da string + "?"
            complexity = 0.4 if len(user_command) > 50 or "?" in user_command else 0.3
            brain_config = self.brain_router.choose_brain(
                task_complexity=complexity,
                privacy_level=PrivacyLevel.LOW,
                latency_requirement=LatencyRequirement.LOW
            )
            
            brain_choice = brain_config.get('brain', 'local')
            if brain_choice.startswith("ollama:"):
                primary_provider = brain_choice
            elif brain_choice.startswith("cloud:"):
                primary_provider = brain_choice
            else:
                primary_provider = 'local'
        else:
            primary_provider = 'local'
        
        # 3. Capturar estado atual da tela (PARALELO)
        screenshot_event = threading.Event()
        screenshot_container = {"image_data": None}

        def _capture_task():
            screenshot_container["image_data"] = screen_capture.capture_fullscreen(capture_type='agent', return_image=True)
            screenshot_event.set()

        capture_thread = threading.Thread(target=_capture_task, daemon=True)
        capture_thread.start()
        
        # ... (Step 4 Context building unchanged) ...
        
        # 4.4 Contexto Emocional (Phase 14)
        user_emotion = camera_controller.current_emotion if camera_controller else "neutral"
        emotion_mod = emotion_detector.get_personality_modifier(user_emotion)
        emotion_prefix = emotion_mod['prefix']
        
        # ðŸ†• REFRESH DINÃ‚MICO DE IDENTIDADE
        dynamic_identity = self._get_dynamic_identity_prompt()
        dynamic_system_prompt = f"{emotion_prefix}{dynamic_identity}\nEstilo de resposta: {emotion_mod['style']}.\nNÃ­vel de energia: {emotion_mod['energy']}."
        
        camera_context = f"\n[VISÃƒO] UsuÃ¡rio identificado: {camera_controller.last_seen_user if camera_controller else 'Desconhecido'}"
        
        # EnvÃ­a emoÃ§Ã£o para o Dashboard Web (Phase 3)
        from src.utils.web_emitter import emit_log_sync
        emit_log_sync(f"Humor detectado: {user_emotion.upper()} | Persona: {emotion_mod['style']}")
        
        # =====================================================================
        # PHASE 3: RAG - INCLUDE MEMORY CONTEXT
        # =====================================================================
        # enriched_command = f"{camera_context}\n{memory_context}\nComando atual: {user_command}"
        
        # ðŸ†• STARK 2.0: Context Sanitization
        raw_context = {
            "vision": camera_controller.last_seen_user if camera_controller else "Unknown",
            "memory": memory_context,
            "system_root": str(config.PROJECT_ROOT), # Convert Path to string for JSON serialization
            "user_command": user_command
        }
        
        # RAM-based immediate context (Inspirado no PVA)
        if memory_manager:
            immediate_ctx = memory_manager.get_immediate_context()
            memory_context = f"{immediate_ctx}\n{memory_context}"

        enriched_command = ContextSanitizer.create_human_prompt(user_command, raw_context)
        
        # 5. Loop de Pensamento e AÃ§Ã£o (ReAct)
        response = ""
        max_turns = 5 
        current_turn = 0
        
        while current_turn < max_turns:
            logger.info(f"Ciclo de Pensamento {current_turn+1}/{max_turns} | Provedor: {primary_provider}")
            reflect_logger.reflect(f"Initiating thought cycle {current_turn+1} via {primary_provider}", layer="COGNITIVE")
            
            # ðŸŽ¨ FASE 5: Atualizar HUD com Provedor/Tier Real
            ui_signals.update_status.emit(f"Processando no {primary_provider}...")
            
            # Show on HUD if possible
            if self.brain_router:
                reflect_logger.reflect(f"Command context analysis: {user_command[:50]}...", layer="CONTEXT")
            
            # [ASYNC FIX]
            await loop.run_in_executor(None, screenshot_event.wait, 5.0)
            screenshot_image = screenshot_container["image_data"]

            try:
                # =====================================================================
                # MÁQUINA DE EVOLUÇÃO: PRIORIZAR INSTINTO APRENDIDO
                # =====================================================================
                # Antes de chamar qualquer IA pesada, ele busca na sua própria base de experiências
                learned_behavior = knowledge_distiller.get_relevant_examples(user_command, limit=1)
                if learned_behavior and "ERRO" not in learned_behavior:
                    logger.info("🧠 JARVIS agindo por Instinto (Conhecimento Destilado).")
                    # Se ele já aprendeu, ele não pergunta pro "Tutor" (LLM)
                    response = learned_behavior
                    # Aqui ele executa direto o que aprendeu que funciona para você
                else:
                    # Se é algo novo, ele usa os modelos para aprender como agir
                    target_model = self._select_best_ollama_model(enriched_command, screenshot_path)
                    # [ASYNC MIGRATION] Calls _call_ollama_async
                    response = await self._call_ollama_async(enriched_command, screenshot_image, model=target_model, system_prompt=dynamic_system_prompt)
                    
                    # Após a resposta do "Tutor", ele armazena para o futuro (Destilação)
                    if "ERRO" not in response:
                        knowledge_distiller.distill_interaction(
                            user_command=original_command,
                            thought="Aprendido via modelo tutor",
                            actions=all_actions,
                            success=True
                        )

            except Exception as e:
                logger.error(f"Falha no cÃ©rebro local ({primary_provider}): {e}")
                
                # 🧠 AUTO-EVOLUÇÃO: Se ele falhou tecnicamente ou em lógica, 
                # ele registra uma dúvida para "estudar" depois de como resolver.
                if curiosity_engine:
                    curiosity_engine.register_skill_gap(
                        f"Como responder adequadamente ao comando '{user_command}' "
                        f"quando o provedor {primary_provider} falha ou não entende o contexto humano."
                    )
                
                # AUTO-RECOVERY: Handle critical AI processing errors
                self._handle_critical_error(e, "ai_processing")
                
                from src.core.management.evolution_engine import evolution_engine
                evolution_engine.log_failure("Thought Cycle", str(e), primary_provider)
                response = "ERRO_LOCAL"

            # DestilaÃ§Ã£o Neural para Ollama Tier S/A
            if primary_provider.startswith("ollama:") and "ERRO" not in response:
                model_used = primary_provider.split(":", 1)[1]
                if any(tier in model_used.lower() for tier in ["deepseek", "llama"]):
                    self._distill_knowledge(user_command, response, provider=model_used)

            # Fallback final se tudo falhar
            if "ERRO_LOCAL" in response and "Erro" in response:
                 response = "Senhor, meus sistemas locais e remotos estÃ£o inacessÃ­veis no momento."
            
            # =====================================================================
            # CORREÃ‡ÃƒO P1: PROCESSAMENTO ESTRUTURADO (Substitui Regex)
            # =====================================================================
            action_executed = False
            
            if "thought" in response.lower() or "actions" in response.lower():
                 reflect_logger.reflect("Decoding structured behavioral response...", layer="STRUCTURED_LOGIC")
            
            # Tentar processing estruturado primeiro
            if self.use_structured_output:
                structured_result = await self._process_structured_response(response, enriched_command)
                
                if structured_result:
                    final_answer, enriched_command, action_executed, parsed = structured_result
                    response = final_answer
                    
                    # Se executou aÃ§Ãµes, continuar loop ReAct
                    if action_executed:
                        # Rastrear aÃ§Ãµes para destilaÃ§Ã£o ( Phase 4)
                        if parsed and parsed.actions:
                            # Converter aÃ§Ãµes pydantic em dicts para o distiller
                            all_actions.extend([a.dict() for a in parsed.actions])
                        
                        current_turn += 1
                        continue
                    else:
                        # âœ… SUCESSO: Resposta final sem aÃ§Ãµes
                        if knowledge_distiller and all_actions:
                            # Destilar o comando original com as aÃ§Ãµes que levaram ao sucesso
                            knowledge_distiller.distill_interaction(
                                user_command=original_command,
                                thought=parsed.thought if parsed else "",
                                actions=all_actions,
                                success=True
                            )
                        break
            
            # =====================================================================
            # FALLBACK: ActionHandler Unificado (ModularizaÃ§Ã£o)
            # =====================================================================
            if not self.use_structured_output or structured_result is None:
                reflect_logger.reflect("Cascading response to unified handler...", layer="FALLBACK")
                handler = get_action_handler()
                results = await handler.execute_actions_sync([response])
                
                action_executed_in_legacy = False
                for r in results:
                    if r.get("status") in ["success", "partial_success"]:
                        action_executed_in_legacy = True
                        res_text = r.get('result', 'AÃ§Ã£o completada')
                        enriched_command += f"\n\n[SISTEMA] Sucesso em {r.get('action')}: {res_text}"
                    elif r.get("status") == "blocked":
                        enriched_command += f"\n\n[SEGURANÃ‡A] AÃ§Ã£o BLOQUEADA: {r.get('error')}"
                    elif r.get("action") != "parse":
                        enriched_command += f"\n\n[SISTEMA] Erro em {r.get('action')}: {r.get('error')}"
                
                if action_executed_in_legacy:
                    current_turn += 1
                    continue
                
                # Se não houver ações, paramos o loop
                break

        # =====================================================================
        # PHASE: DISSONANCE DETECTION & PROACTIVE CLARIFICATION
        # =====================================================================
        from src.learning.truth_validator import get_truth_validator
        validator = get_truth_validator()
        
        # Gatilho de Dissonância: Baixa confiança ou conflito detectado
        # Analisa se a resposta contém termos de incerteza ou se o comando é de alta complexidade
        if any(w in response.lower() for w in ["desconheço", "não tenho certeza", "talvez", "incerto"]):
            validation = validator.validate_fact(user_command)
            
            # Condição de Gatilho: 
            # 1. Status DISPUTED (Conflito de fontes)
            # 2. Falta de concordância semântica entre as fontes encontradas
            if validation.get("status") == "DISPUTED" or not validation.get("semantic_agreement", True):
                clarification = self.ask_for_clarification(validation)
                response = f"{response}\n\n[STARK CURIOSITY] {clarification}"
                if voice_controller:
                    voice_controller.speak(clarification)

        # ... (Step 6-7 unchanged) ...
        # [PHASE 2.2] Event-Driven Memory Storage
        if self.event_bus:
            # Publish event for background storage
            await self.event_bus.publish("ai.response.generated", {
                "prompt": user_command,
                "response": response,
                "metadata": {
                    "provider": primary_provider,
                    "turns": current_turn + 1,
                    "ts": time.time()
                }
            })
        elif memory_manager:
            # Legacy synchronous storage
            memory_manager.store_interaction(user_command, response)
        
        # ðŸ§  PHASE 6: REGISTRO DE FEEDBACK PARA APRENDIZADO CONTÃNUO
        if get_learning_engine:
            try:
                learning_engine = get_learning_engine()
                if learning_engine and learning_engine.is_initialized:
                    # Coletar metadados da interaÃ§Ã£o
                    metadata = {
                        'provider': primary_provider,
                        'turns': current_turn + 1,
                        'actions_executed': len(all_actions),
                        'emotion': user_emotion if camera_controller else 'neutral'
                    }
                    
                    # Registrar interação para aprendizado e dinâmica interpessoal
                    learning_engine.record_interaction(
                        user_input=user_command,
                        ai_response=response,
                        feedback_value=None,
                        metadata=metadata
                    )
                    
                    # 🫂 SINCERIDADE E EVOLUÇÃO: Atualiza vínculo
                    # Estimativa de sentimento baseada no comprimento e pontuação (Placeholder para análsie real)
                    sentiment = "positive" if len(user_command) > 10 and "?" not in user_command else "neutral"
                    context_manager.record_interaction(sentiment, was_helpful=True)
                    
                    logger.debug("📏 Dinâmica de Vínculo atualizada")
            except Exception as e:
                logger.debug(f"Erro ao registrar interação: {e}")
        
        # 7. Falar a resposta (removendo tags de ação e limpando JSON)
        final_response = self._clean_response_for_speech(response, emotion_prefix)
        
        # Injetar pergunta proativa de aprendizado ou Meta-Conversa Humana
        if proactive_question and "ERRO" not in response:
            final_response = f"{final_response}\n\nPS: {proactive_question}"
        elif context_manager.should_initiate_conversation() and "ERRO" not in response:
             meta_comments = [
                 "A propósito, Senhor, estou estudando nossa forma de interagir para me tornar mais natural. O que tem achado?",
                 "Senhor, espero que meu tom atual esteja de acordo com sua preferência. Estou me adaptando.",
                 "Estou monitorando meus próprios processos para garantir que não interrompa o Senhor indevidamente."
             ]
             import random
             final_response = f"{final_response}\n\n{random.choice(meta_comments)}"
            
        # POLITENESS & NIGHT MODE CHECK antes de falar a resposta final
        if voice_controller:
            if context_manager.should_be_quiet():
                # No modo silencioso, evitamos a fala auditiva, mas garantimos o feedback visual
                logger.info(f"🤫 (Silent Mode) JARVIS: {final_response}")
                ui_signals.update_status.emit(final_response)
            else:
                # Se não for modo silencioso, verifica se o momento é oportuno (Politeness)
                if context_manager.check_politeness():
                    voice_controller.speak(final_response)
                else:
                    # Se o usuário estiver ocupado, podemos adiar ou apenas mostrar visualmente
                    logger.info(f"⏳ (Busy/Polite Mode) JARVIS aguardando momento oportuno...")
                    ui_signals.update_status.emit(f"[Pendente] {final_response}")
                    # Por simplicidade, vamos apenas mostrar no HUD agora, mas poderíamos enfileirar
                    # voice_controller.speak(final_response) # Fallback se quiser forçar
        return final_response

    def ask_for_clarification(self, validation_data: Dict[str, Any]) -> str:
        """Pergunta ao usuário como resolver uma disputa de informações."""
        query = validation_data.get("query", "este assunto")
        sources = [r.get("source") for r in validation_data.get("results", [])]
        unique_sources = list(set(sources))[:2]
        
        if len(unique_sources) >= 2:
            msg = f"Senhor, encontrei informações conflitantes sobre '{query}'. Algumas fontes mencionam {unique_sources[0]} e outras {unique_sources[1]}. Como deseja que eu prossiga?"
        else:
            msg = f"Senhor, não consegui validar com certeza as informações sobre '{query}'. Deseja que eu continue pesquisando ou assume o risco?"
            
        return msg

    def process_hybrid_vision(self, screenshot_path: str) -> Dict[str, Any]:
        """
        [VISÃƒO HÃBRIDA - STARK EVOLUTION]
        NÃ­vel 1 (Local): Filtro rÃ¡pido com UIdetector/YOLO (CPU).
        NÃ­vel 2 (Nuvem): AnÃ¡lise profunda com Gemini PRO se houver complexidade.
        NÃ­vel 3 (Feedback): Resposta da nuvem treina o banco local.
        """
        result = {"source": "local", "action": "none", "analysis": ""}
        logger.info("[HYBRID VISION] Iniciando ciclo de anÃ¡lise...")

        try:
            # --- NÃVEL 1: SENTINELA LOCAL (YOLO/CPU) ---
            # Custo: $0.00 | Tempo: <500ms
            ui_elements = ui_detector.detect_elements(screenshot_path)
            element_count = len(ui_elements)
            
            # HeurÃ­stica de Complexidade Visual
            # Se tiver muitos elementos, texto denso (implÃ­cito), ou padrÃµes de erro
            is_complex_context = element_count > 3 
            
            summary = ui_detector.get_summary(ui_elements)
            logger.info(f"[HYBRID VISION] NÃ­vel 1 (Local): {summary} | Complexo? {is_complex_context}")

            if not is_complex_context:
                # Tela simples/estÃ¡tica. Nada a fazer.
                return result

            # --- NÃVEL 2: ANÃLISE PROFUNDA LOCAL (LLAVA) ---
            # Tentamos resolver localmente primeiro se houver GPU ou LLaVA rodando.
            logger.info("[HYBRID VISION] NÃ­vel 2 (Local AI)...")
            
            vision_prompt = (
                "VISÃƒO TOTAL ATIVADA.\n"
                f"Contexto: {summary}\n"
                "Analise esta imagem. Se houver erro crÃ­tico ou algo notÃ¡vel para o usuÃ¡rio, explique.\n"
                "Caso contrÃ¡rio, responda APENAS 'NO_ACTION'."
            )
            
            local_response = ""
            if self._check_ollama_alive():
                try:
                    local_response = self._call_ollama(vision_prompt, screenshot_image)
                except:
                    local_response = "incerto"

            # Se o local resolver (e nÃ£o for erro/incerto), usamos ele.
            if local_response and len(local_response) > 5 and "incerto" not in local_response.lower():
                result["source"] = "local_llm"
                result["analysis"] = local_response
                if "no_action" not in local_response.lower():
                     voice_controller.speak(local_response)
                     result["action"] = "spoke_local"
                return result

            # --- NÃVEL 3: ANALISADOR EXTERNO (SELETIVO) ---
            if self.brain_router and self.brain_router.cloud_available:
                target = self.brain_router.choose_brain(task_complexity=0.9, privacy_level=PrivacyLevel.LOW)
                if target["brain"].startswith("cloud:"):
                    logger.info(f"[HYBRID VISION] NÃ­vel 3 (Cloud) - Analisando via {target['brain']}")
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    cloud_analysis = loop.run_until_complete(self.decision_engine._call_llm(
                        prompt="Analise esta imagem em detalhes extremos.",
                        provider=target["brain"],
                        image_path=image_path
                    ))
                    result["analysis"] = cloud_analysis
                    result["source"] = "cloud_expert"
                    return result

            result["source"] = "local_final"
            result["analysis"] = "AnÃ¡lise local concluÃ­da. Nuvem externa indisponÃ­vel ou desnecessÃ¡ria."

        except Exception as e:
            logger.error(f"[HYBRID VISION] Erro crÃ­tico: {e}")
        
        return result

    def process_proactive_analysis(self, change_data: Dict[str, Any]):
        """
        [SENTINELA PROATIVO]
        Analisa mudanÃ§as detectadas na tela e decide se deve intervir.
        """
        try:
            diff_percent = change_data.get('diff_percent', 0)
            screenshot_path = change_data.get('screenshot_path')
            
            if not screenshot_path or not os.path.exists(screenshot_path):
                return
            
            logger.info(f"Iniciando anÃ¡lise proativa ({diff_percent:.1f}% de mudanÃ§a)...")
            
            # Usar visÃ£o hÃ­brida para analisar
            result = self.process_hybrid_vision(screenshot_path)
            analysis = result.get("analysis", "")
            
            if analysis and "NO_ACTION" not in analysis.upper():
                logger.info(f"IntervenÃ§Ã£o proativa bem sucedida: {analysis}")
                return analysis
            
            return None

        except Exception as e:
            logger.error(f"Erro na anÃ¡lise proativa: {e}")
            return None

    def _distill_knowledge(self, command: str, response: str, provider: str):
        """Converte conhecimento de modelos Smart em MemÃ³rias de Ouro para o Micro-LLM"""
        if not memory_manager: return
        try:
            # Filtro bÃ¡sico: Apenas respostas substanciais valem destilaÃ§Ã£o
            if len(response) > 50 and "erro" not in response.lower():
                memory_manager.remember(
                    command=command,
                    response=response,
                    metadata={"provider": provider, "type": "distilled_knowledge"},
                    is_gold=True
                )
        except Exception as e:
            logger.debug(f"Erro na destilaÃ§Ã£o neural: {e}")

    def _get_quick_response(self, text: str) -> Optional[str]:
        """Intercepta comandos comuns para resposta instantÃ¢nea (<50ms)"""
        text = text.lower().strip()
        import random

        # 1. ANALISADOR DE CONTEXTO STARK (Nova LÃ³gica Phase 2)
        if analisador_contexto:
            ctx = analisador_contexto.analisar(text)
            
            # COMANDOS DE HARDWARE (Brilho, Volume)
            if ctx["contexto"] == "HARDWARE" and device_manager:
                return self._handle_hardware_commands(text)
                
            # COMANDOS DE AUTONOMIA (Dreaming / Treinamento)
            if ctx["contexto"] == "AUTONOMIA" and neural_dreaming:
                return self._handle_dreaming_commands(text)

            # COMANDOS DE BIOMETRIA (Fase 9: Cadastro DinÃ¢mico)
            if any(k in text for k in ["cadastrar meu rosto", "registrar nova face", "novo usuÃ¡rio", "cadastrar rosto"]):
                # Extrair nome se houver (ex: "cadastrar rosto do Marcus")
                # Se nÃ£o houver, assume Williams (o usuÃ¡rio principal)
                name = "William"
                name_match = re.search(r"da\s+(\w+)|do\s+(\w+)", text)
                if name_match:
                    name = name_match.group(1) or name_match.group(2)
                
                # Executar em thread separada para nÃ£o travar o loop de comando principal
                threading.Thread(target=camera_controller.register_new_face, args=(name,), daemon=True).start()
                return f"Entendido, senhor. Ativando protocolos de biometria para mapear {name}."

            # COMANDOS DE MULTIMÃDIA (MÃºsica, Browser)
            if ctx["contexto"] == "MULTIMIDIA" and device_manager:
                if any(k in text for k in ["mÃºsica", "tocar", "ouvir"]):
                    device_manager.open_browser(text)
                    return "Abrindo o YouTube Music para vocÃª, senhor. O que deseja ouvir?"

        # PadrÃµes de SaudaÃ§Ãµes
        greetings = ["oi jarvis", "olÃ¡ jarvis", "bom dia jarvis", "boa tarde jarvis", "boa noite jarvis", "ei jarvis"]
        if any(g in text for g in greetings) and len(text.split()) < 4:
            return random.choice(["Sim, senhor. Como posso ajudar?", "Ã€s suas ordens, William.", "OlÃ¡, senhor. Sistemas operacionais ativos."])
            
        # PadrÃµes de ConfirmaÃ§Ã£o/Agradecimento
        thanks = ["obrigado", "valeu jarvis", "obrigado jarvis", "thanks jarvis"]
        if any(t in text for t in thanks) and len(text.split()) < 3:
            return random.choice(["Por nada, senhor.", "Disponha sempre.", "Ã‰ um prazer ser Ãºtil."])
            
        # PadrÃµes de Status
        status = ["status do sistema", "como estÃ£o os sistemas", "checkup do sistema"]
        if any(s in text for s in status):
            if hardware_manager:
                hw = hardware_manager.get_status()
                return f"Sistemas {hw['tier']} operando em {hw['device']}. GPU em {hw['gpu_load']}%. Tudo estÃ¡vel."

        return None

    def _handle_hardware_commands(self, text: str) -> str:
        """LÃ³gica para Brilho e Volume"""
        # Brilho
        if "brilho" in text:
            # Extrair nÃºmero
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
            
        return "Comando de hardware reconhecido, mas nÃ£o entendi o valor, senhor."

    def _handle_dreaming_commands(self, text: str) -> str:
        """LÃ³gica para Treinamento e Estudo (Dreaming)"""
        # Extrair tÃ³pico (ex: "estude programaÃ§Ã£o")
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
            mode_str = "foco total (CPU PrioritÃ¡ria)" if focus_mode else "segundo plano"
            return f"Entendido, William. Iniciando protocolo de estudo sobre {topic} por {duration} minutos em {mode_str}."
        
        return "JÃ¡ estou em um ciclo de processamento neural, senhor. Deseja que eu pare o atual?"
    
    # =========================================================================
    # CORREÃ‡ÃƒO P1: PROCESSAMENTO ESTRUTURADO DE RESPOSTAS
    # =========================================================================
    
    async def _process_structured_response(self, raw_response: str, enriched_command: str) -> tuple:
        """
        Processa resposta estruturada (JSON) do LLM.
        """
        if not STRUCTURED_OUTPUT_AVAILABLE:
            return None
        
        try:
            # 1. Parsear resposta
            parsed = ResponseParser.parse_llm_response(raw_response)
            reflect_logger.reflect(parsed.thought, layer="COGNITIVE")
            
            # 2. Executar via ActionHandler
            action_executed = False
            if parsed.actions:
                handler = get_action_handler()
                results = await handler.execute_actions_sync(parsed.actions)
                
                for res in results:
                    if res.get('status') == 'success':
                        action_executed = True
                        enriched_command += f"\n\n[SISTEMA] Sucesso em {res.get('action')}: {res.get('result', 'OK')}"
                    else:
                        enriched_command += f"\n\n[SISTEMA] Falha em {res.get('action')}: {res.get('error')}"
                
                if action_executed:
                    enriched_command += "\n\nVocÃª precisa fazer mais algo ou concluímos o objetivo?"

            return (parsed.final_answer, enriched_command, action_executed, parsed)
        
        except Exception as e:
            logger.error(f"Erro no processamento estruturado: {e}")
            return None

    def _select_best_ollama_model(self, prompt: str, image_data: Optional[Any] = None) -> str:
        """Seleciona dinamicamente o melhor modelo Ollama para a tarefa usando o BrainRouter"""
        if not self.brain_router:
            return "gemma3:4b" # Fallback seguro
            
        # Determina a complexidade básica
        complexity = 0.3
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["código", "python", "script", "debug", "analise"]):
            complexity = 0.7
        elif image_path:
            complexity = 0.8 # Imagem exige mais "cérebro"
            
        # Pede ao router o melhor cérebro local
        brain_info = self.brain_router.choose_brain(task_complexity=complexity)
        brain = brain_info.get("brain", "local")
        
        if brain.startswith("ollama:"):
            return brain.split(":", 1)[1]
            
        # Se o router sugerir 'local' (LocalBrain) ou 'cloud', mas queremos especificamente 
        # um modelo Ollama aqui, buscamos o melhor disponível
        return self.brain_router._choose_local_brain().replace("ollama:", "")

    def _call_ollama(self, prompt: str, image_data: Optional[Any] = None, model: Optional[str] = None, system_prompt: str = None):
        """IntegraÃ§Ã£o com Ollama Local (Multi-modelo) com Keep-Alive DinÃ¢mico"""
        try:
            import base64
            
            # Seleciona o melhor modelo se nÃ£o for especificado
            target_model = model if model else self._select_best_ollama_model(prompt, image_data)
            
            encoded_image = None
            if image_data:
                # Se image_data é PIL Image, converter para bytes
                if hasattr(image_data, 'convert'):  # PIL Image
                    from io import BytesIO
                    buffer = BytesIO()
                    image_data.save(buffer, format='PNG')
                    image_bytes = buffer.getvalue()
                else:
                    # Assume bytes
                    image_bytes = image_data
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')

            final_system_prompt = system_prompt if system_prompt else self.system_prompt
            
            # ðŸ†• FASE 2: Determinar keep_alive baseado no tier do modelo
            keep_alive = self._get_keep_alive_for_model(target_model)
            is_heavy = keep_alive == 0
            
            logger.info(f"ðŸ¤¾ [OLLAMA] Usando modelo: '{target_model}' (keep_alive: {keep_alive})")
            
            payload = {
                "model": target_model,
                "prompt": f"{final_system_prompt}\n\nComando do William: {prompt}\n\nLembre-se: Retorne APENAS o JSON.",
                "stream": False,
                "keep_alive": keep_alive,  # ðŸ†• FASE 2: CÃ¢mbio Cognitivo
                "options": {
                    "temperature": 0.2, # Mais focado para seguir formato
                    "num_predict": 512
                }
            }
            if encoded_image:
                payload["images"] = [encoded_image]

            # ðŸ†• FASE 2: Timeout dinÃ¢mico (180s para modelos pesados, 90s para leves)
            timeout = 180 if is_heavy else 90
            
            response = requests.post(self.ollama_url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            return data.get('response', "Senhor, nÃ£o obtive resposta do processador local.")

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout ao chamar Ollama ({target_model}): {e}")
            return "OLLAMA_TIMEOUT"  # Sinal para retry
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão com Ollama ({target_model}): {e}")
            return "OLLAMA_CONNECTION_ERROR"  # Sinal para retry
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama ({target_model}): {e}")
            return "OLLAMA_ERROR"  # Sinal para fallback

    async def _call_ollama_async(self, prompt: str, image_data: Optional[Any] = None, model: Optional[str] = None, system_prompt: str = None) -> str:
        """
        [ASYNC] Integração com Ollama Local (Multi-modelo) usando aiohttp.
        100% Assíncrono para não travar o Event Loop.
        """
        try:
            import base64
            import aiohttp
            
            # Seleciona o melhor modelo se não for especificado
            target_model = model if model else self._select_best_ollama_model(prompt, image_data)
            
            encoded_image = None
            if image_data:
                # Processamento de imagem em executor thread se necessário, 
                # mas operações em memória bytes são rápidas.
                if hasattr(image_data, 'convert'):  # PIL Image
                    from io import BytesIO
                    buffer = BytesIO()
                    # Salvar imagem pode ser levemente pesado, mas ok para pouca frequência
                    image_data.save(buffer, format='PNG')
                    image_bytes = buffer.getvalue()
                else:
                    image_bytes = image_data
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')

            final_system_prompt = system_prompt if system_prompt else self.system_prompt
            
            # Determinar keep_alive
            keep_alive = self._get_keep_alive_for_model(target_model)
            is_heavy = keep_alive == 0
            
            logger.info(f"🧞‍♂️ [ASYNC OLLAMA] Usando modelo: '{target_model}' (keep_alive: {keep_alive})")
            
            payload = {
                "model": target_model,
                "prompt": f"{final_system_prompt}\n\nComando do William: {prompt}\n\nLembre-se: Retorne APENAS o JSON.",
                "stream": False,
                "keep_alive": keep_alive,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 512
                }
            }
            if encoded_image:
                payload["images"] = [encoded_image]

            timeout_seconds = 180 if is_heavy else 90
            timeout = aiohttp.ClientTimeout(total=timeout_seconds)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Ollama respondeu com erro: {response.status}")
                        response.raise_for_status() # Vai para o except
                    
                    data = await response.json()
                    return data.get('response', "Senhor, não obtive resposta do processador local.")

        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão Async com Ollama ({target_model}): {e}")
            return "OLLAMA_CONNECTION_ERROR"
        except Exception as e:
            logger.error(f"Erro Async ao chamar Ollama ({target_model}): {e}")
            return "OLLAMA_ERROR"
    
    def _get_keep_alive_for_model(self, model_name: str) -> any:
        """
        ðŸ†• FASE 2: Determina keep_alive baseado no tier do modelo
        - tier_fast (1.5B-3B): 15 minutos (cache para respostas rÃ¡pidas)
        - tier_pro/ultra (7B+): 0 (descarte imediato para liberar RAM)
        """
        model_lower = model_name.lower()
        
        # tier_fast: Modelos leves ficam em cache
        if self.brain_router and hasattr(self.brain_router, 'tier_fast'):
            tier_fast_patterns = [model.lower() for model in self.brain_router.tier_fast]
        else:
            tier_fast_patterns = ["qwen2.5:3b", "qwen2.5:1.5b", "llama3.2:3b", "phi3.5", "gemma2:2b"]  # Fallback
        for pattern in tier_fast_patterns:
            if pattern in model_lower:
                return "15m"
        
        # tier_pro/ultra: Modelos pesados sÃ£o descarregados imediatamente
        return 0

    async def _call_smart_brain_async(self, prompt: str, image_path: Optional[str] = None, complexity: float = 0.5, system_prompt: str = None) -> str:
        """
        [ASYNC ALTERNÂNCIA INTELIGENTE - STARK IQ]
        Versão não-bloqueante para o Event Bus.
        Orquestra a chamada entre diferentes provedores com fallback automático.
        Ordem: Ollama (Async) -> LocalBrain (Executor).
        """
        # 1. Roteamento Inicial
        brain_config = self.brain_router.choose_brain(task_complexity=complexity) if self.brain_router else {"brain": "local"}
        primary_brain = brain_config.get("brain", "local")
        
        logger.info(f"🧠 [ASYNC] Smart Router selecionou core primário: {primary_brain}")
        
        # 2. TENTATIVA 1: OLLAMA (COM RETRY)
        if primary_brain.startswith("ollama:"):
            model = primary_brain.split(":", 1)[1]
            
            # Tentar Ollama até 3 vezes antes de desistir
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await self._call_ollama_async(prompt, image_path, model=model, system_prompt=system_prompt)
                    
                    error_indicators = [
                        "OLLAMA_TIMEOUT",
                        "OLLAMA_CONNECTION_ERROR",
                        "OLLAMA_ERROR",
                        "instabilidade momentânea",
                        "dificuldades no processamento"
                    ]
                    
                    is_error = any(indicator in response for indicator in error_indicators)
                    
                    if not is_error and len(response.strip()) > 10:
                        logger.info(f"✅ Ollama {model} respondeu com sucesso (async tentativa {attempt + 1}/{max_retries})")
                        return response
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Ollama resposta inválida/erro na tentativa {attempt + 1}, retry em 2s...")
                        await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Erro Async no Ollama (tentativa {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
            
            logger.warning(f"⚠️ Ollama ({model}) falhou após {max_retries} tentativas. Ativando fallback para LocalBrain...")

        # 3. FALLBACK FINAL: NATIVO (LocalBrain) - Executado em Thread Separada
        logger.info("🏠 Async Fallback Final: Ativando LocalBrain nativo em Executor.")
        try:
            if not local_brain:
                return "Sistemas de backup indisponíveis, senhor."

            loop = asyncio.get_running_loop()
            # Rodar LocalBrain em thread pool para nao bloquear loop
            response = await loop.run_in_executor(
                None, 
                lambda: local_brain.generate_response(prompt, system_prompt=system_prompt or self.system_prompt)
            )
            
            if response and len(response.strip()) > 5:
                return response
            else:
                return "Sistemas online, William. Pronto para o que precisar."
        except Exception as e:
            logger.error(f"Erro crítico no Async LocalBrain fallback: {e}")
            return "Sistemas operacionais, senhor."

    def _call_smart_brain(self, prompt: str, image_path: Optional[str] = None, complexity: float = 0.5, system_prompt: str = None) -> str:
        """
        [ALTERNÂNCIA INTELIGENTE - STARK IQ]
        Orquestra a chamada entre diferentes provedores com fallback automático.
        Ordem: Ollama (com retry) -> LocalBrain (Micro-LLM).
        Prioriza sempre Ollama quando disponível.
        """
        # 1. Roteamento Inicial
        brain_config = self.brain_router.choose_brain(task_complexity=complexity) if self.brain_router else {"brain": "local"}
        primary_brain = brain_config.get("brain", "local")
        
        logger.info(f"🧠 Smart Router selecionou core primário: {primary_brain}")
        
        # 2. TENTATIVA 1: OLLAMA (COM RETRY)
        if primary_brain.startswith("ollama:"):
            model = primary_brain.split(":", 1)[1]
            
            # Tentar Ollama até 3 vezes antes de desistir (prioridade máxima)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self._call_ollama(prompt, image_path, model=model, system_prompt=system_prompt)
                    
                    # Verificar se é uma resposta válida (não é erro de conexão)
                    error_indicators = [
                        "OLLAMA_TIMEOUT",
                        "OLLAMA_CONNECTION_ERROR",
                        "OLLAMA_ERROR",
                        "instabilidade momentânea",
                        "dificuldades no processamento"
                    ]
                    
                    is_error = any(indicator in response for indicator in error_indicators)
                    
                    if not is_error and len(response.strip()) > 10:
                        logger.info(f"✅ Ollama {model} respondeu com sucesso (tentativa {attempt + 1}/{max_retries})")
                        return response
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Ollama resposta inválida/erro na tentativa {attempt + 1}, retry em 2s...")
                        import time
                        time.sleep(2)  # Pausa maior para estabilizar
                    
                except Exception as e:
                    logger.error(f"Erro no Ollama (tentativa {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)
            
            logger.warning(f"⚠️ Ollama ({model}) falhou após {max_retries} tentativas. Ativando fallback para LocalBrain...")

        # 3. FALLBACK FINAL: NATIVO (LocalBrain) - O motor que nunca para
        logger.info("🏠 Fallback Final: Ativando LocalBrain nativo (1.5B Qwen).")
        try:
            from src.core.intelligence.local_brain import local_brain
            response = local_brain.generate_response(prompt, system_prompt=system_prompt or self.system_prompt)
            if response and len(response.strip()) > 5:
                return response
            else:
                logger.error("LocalBrain retornou resposta vazia, usando mensagem de emergência")
                return "Sistemas online, William. Pronto para o que precisar."
        except Exception as e:
            logger.error(f"Erro crítico no LocalBrain fallback: {e}")
            return "Sistemas operacionais, senhor."

    def _clean_response_for_speech(self, response: str, emotion_prefix: str = "") -> str:
        """
        Limpa a resposta do LLM para ser falada pelo TTS.
        Remove tags [ACTION], [SEARCH], blocos JSON e Markdown.
        """
        if not response:
            return ""

        # 1. Tentar extrair 'final_answer' se for um JSON puro ou tiver bloco JSON
        try:
            # Tentar Regex para achar bloco JSON {}
            json_match = re.search(r'\{.*"final_answer":\s*"(.*?)".*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            else:
                # Tentar carregar como JSON completo se o LLM sÃ³ cuspiu JSON
                data = json.loads(response)
                if isinstance(data, dict):
                    response = data.get('final_answer', data.get('frase', response))
        except:
            pass # NÃ£o era JSON puro, segue limpeza normal

        # 2. Remover tags do sistema
        response = re.sub(r'\[ACTION: .*?\]', '', response)
        response = re.sub(r'\[SEARCH: .*?\]', '', response)
        response = re.sub(r'```.*?```', '', response, flags=re.DOTALL) # Remove blocos de cÃ³digo
        
        # 3. Limpeza de aspas extras (frequente em saÃ­das estruturadas)
        response = response.strip().strip('"').strip("'").strip()
        
        # 4. Aplicar prefixo emocional se aplicÃ¡vel
        if emotion_prefix and "no_action" not in response.lower() and len(response) > 5:
            # Evitar duplicar prefixo se jÃ¡ estiver lÃ¡
            if not response.startswith(emotion_prefix[:5]):
                response = f"{emotion_prefix}{response}"
                
        return response

    def _check_ollama_alive(self) -> bool:
        """Verifica se o Ollama estÃ¡ rodando localmente"""
        try:
            # Simples check na URL base
            base_url = self.ollama_url.replace("/api/generate", "")
            requests.get(base_url, timeout=2)
            return True
        except:
            return False

    def set_event_bus(self, event_bus):
        """
        Connect the AI Agent to the Event Bus for asynchronous communication.
        
        Args:
            event_bus: Event bus instance for pub/sub communication
        """
        self.event_bus = event_bus
        
        if event_bus:
            try:
                # Subscribe to audio transcription events
                import asyncio
                asyncio.create_task(
                    event_bus.subscribe(
                        EventType.AUDIO_TRANSCRIPTION,
                        self._handle_transcription_event
                    )
                )
                
                # Subscribe to vision analysis events
                asyncio.create_task(
                    event_bus.subscribe(
                        EventType.VISION_SCREEN_ANALYSIS,
                        self._handle_vision_event
                    )
                )
                
                logger.info("✅ AI Agent connected to Event Bus (async communication enabled)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to subscribe to Event Bus events: {e}")


    async def process_command_async(self, text: str, context: dict = None) -> Optional[str]:
        """
        Process command asynchronously (Phase 2.1).
        Uses the native async process_command (fully non-blocking).
        """
        try:
            # P0: Check for empty input
            if not text or not text.strip():
                return None

            # Execute async process_command directly on the event loop
            # No executor needed as process_command is now async-native
            response = await self.process_command(text)
        except Exception as e:
            logger.error(f"❌ Async Processing Error: {e}")
            return None

    async def _handle_transcription_event(self, event_data: dict):
        """Handle transcription events from audio system"""
        try:
            text = event_data.get("text", "")
            speaker_verified = event_data.get("speaker_verified", False)
            confidence = event_data.get("confidence", 0.0)
            
            # Confidence threshold
            if confidence < 0.6:
                return

            logger.debug(f"🎤 Async Transcription: {text} (conf: {confidence:.2f})")
            
            # Trigger Async Processing
            # We treat verified speakers as authorized
            if speaker_verified or True: # Temporary: Allow all for testing if verification is strict
                 await self.process_command_async(text, context=event_data)
                 
        except Exception as e:
            logger.error(f"❌ Error handling transcription event: {e}")

    async def _handle_vision_event(self, event_data: dict):
        """Handle vision analysis events from vision system"""
        try:
            # Update Context Manager with latest visual context
            if context_manager:
                # Assuming update_visual_context is fast/non-blocking or handles its own async
                # If synchronous, might slightly block but usually fast metadata update
                try:
                    context_manager.update_visual_context(event_data)
                except AttributeError:
                    pass # context_manager might not have this method yet
                
            # Log for debugging
            diff_percent = event_data.get("diff_percent", 0)
            logger.debug(f"👁️ Visual Context Updated (Diff: {diff_percent:.1f}%)")
            
            # [PHASE 2.3] Trigger Proactive Engagement
            # If significant change detected by Proactive Monitor
            if diff_percent > 0:
                loop = asyncio.get_running_loop()
                # Run existing proactive logic in thread pool to avoid blocking bus
                await loop.run_in_executor(None, self.process_proactive_analysis, event_data)
                
        except Exception as e:
            logger.error(f"❌ Error handling vision event: {e}")

try:
    from src.learning.knowledge_distiller import knowledge_distiller
except ImportError:
    knowledge_distiller = None

# Instância global
ai_agent = AIAgent()
