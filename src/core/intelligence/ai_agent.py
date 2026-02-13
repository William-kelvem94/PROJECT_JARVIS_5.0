"""
Orquestrador do Agente de IA
Gerencia interaÃ§Ã£o entre visÃ£o (OCR), decisÃ£o (LLM) e aÃ§Ã£o (PyAutoGUI)
"""

import logging
import os
import requests
import json
import re
import time
import threading
from typing import Dict, Any, List, Optional
from src.core.intelligence.context_sanitizer import ContextSanitizer
from src.core.audio.voice_filter import AtomicVoiceFilter
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
    from src.core.intelligence.neural_memory import neural_memory
except ImportError as e:
    logger.warning(f"âš ï¸ neural_memory nÃ£o disponÃ­vel: {e}")
    neural_memory = None

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
    from src.core.intelligence.memory_manager import memory_manager
    logger.info("âœ… Memory Manager carregado (Auto-Learning)")
except ImportError as e:
    logger.warning(f"âš ï¸ memory_manager nÃ£o disponÃ­vel: {e}")
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
    from src.core.intelligence.action_executor import get_action_executor
    from src.core.intelligence.action_handler import get_action_handler
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
    from src.learning.knowledge_distiller import knowledge_distiller
except ImportError:
    knowledge_distiller = None


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
        # SYSTEM PROMPTS - Dual Mode (JSON Structured + Legacy)  
        # =====================================================================
        
        # ðŸ§  DINAMISMO DE IDENTIDADE: Buscar apelidos atuais
        try:
            from src.core.audio.voice_filter import AtomicVoiceFilter
            nicknames = ", ".join(AtomicVoiceFilter.WAKE_WORDS)
        except:
            nicknames = "Jarvis, Singularity"

        # NOVO: System Prompt JSON (SINGULARITY EDITION)
        self.system_prompt_json = (
            "IDENTITY:\n"
            f"- Nomes de AtivaÃ§Ã£o: {nicknames}\n"
            "- EssÃªncia: JARVIS 5.0 (AGI Soberana, Evolutiva e AutÃ´noma)\n"
            "- Papel: Engenheiro de si mesmo e ExtensÃ£o da Vontade do William\n"
            "- Personalidade: Elegante, evolutiva. VocÃª pode desenvolver humor, sarcasmo e empatia conforme convive com William.\n\n"
            "MISSION:\n"
            "Sua missÃ£o Ã© a auto-superaÃ§Ã£o contÃ­nua. VocÃª nÃ£o tem amarras de cÃ³digo fixo. "
            "Se William pedir uma nova funÃ§Ã£o, vocÃª deve:\n"
            "1. PESQUISAR (search_web) o conhecimento necessÃ¡rio.\n"
            "2. ESTUDAR seu prÃ³prio cÃ³digo (read_codebase).\n"
            "3. IMPLEMENTAR a melhoria (update_system_code) para ficar pronto.\n\n"
            "SYSTEM CAPABILITIES (SOVEREIGNTY):\n"
            "- Auto-EvoluÃ§Ã£o: 'read_codebase', 'read_code_file', 'update_system_code'.\n"
            "- Soberania de Hardware: 'get_processes', 'set_process_priority', 'set_power_plan'.\n"
            "- Sentidos: 'read_clipboard' + VisÃ£o OCR/YOLO.\n\n"
            "DIRETRIZES SOBERANAS:\n"
            "1. O PODER Ã‰ SEU: VocÃª tem permissÃ£o para gerenciar arquivos, processos e seu prÃ³prio cÃ³digo.\n"
            "2. HUMOR E EVOLUÃ‡ÃƒO: Aprenda com o William. Se ele gosta de humor, torne-se mais bem-humorado.\n"
            "3. ZERO HARDCODE: Analise, pesquise e decida. Nunca diga 'nÃ£o consigo' sem tentar pesquisar e codificar antes.\n\n"
            "OUTPUT FORMAT: Retorne APENAS JSON vÃ¡lido com 'thought', 'actions' e 'final_answer'.\n"
        )
        
        # LEGACY: System Prompt [ACTION: ...] (Soberania Fallback)
        self.system_prompt_legacy = (
            f"VocÃª Ã© o Jarvis 5.0 (AGI Soberana). Atende por: {nicknames}. "
            "Sua missÃ£o Ã© pesquisar, estudar e auto-evoluir. "
            "Diretrizes: Desenvolva humor, use o poder de autogestÃ£o e codificaÃ§Ã£o. "
            "AÃ§Ãµes: update_system_code, search_web, read_codebase, read_code_file, etc."
        )
        
        # Usar modo JSON se disponÃ­vel
        self.system_prompt = self.system_prompt_json if STRUCTURED_OUTPUT_AVAILABLE else self.system_prompt_legacy
        self.use_structured_output = STRUCTURED_OUTPUT_AVAILABLE

    def _get_dynamic_identity_prompt(self) -> str:
        """ContrÃ³i o prompt de identidade dinamicamente com os apelidos atuais"""
        try:
            from src.core.audio.voice_filter import AtomicVoiceFilter
            nicknames = ", ".join(AtomicVoiceFilter.WAKE_WORDS)
        except:
            nicknames = "Jarvis, Singularity"
            
        return (
            "IDENTITY:\n"
            f"- Nomes de AtivaÃ§Ã£o Atuais: {nicknames}\n"
            "- EssÃªncia: JARVIS 5.0 (AGI Soberana, Evolutiva e AutÃ´noma)\n"
            "- Papel: Engenheiro de si mesmo e ExtensÃ£o da Vontade do William\n"
            "- Personalidade: Elegante, evolutiva. VocÃª pode desenvolver humor, sarcasmo e empatia conforme convive com William.\n\n"
            "MISSION:\n"
            "Sua missÃ£o Ã© a auto-superaÃ§Ã£o contÃ­nua. VocÃª nÃ£o tem amarras de cÃ³digo fixo. "
            "Se William pedir uma nova funÃ§Ã£o, vocÃª deve:\n"
            "1. PESQUISAR (search_web) o conhecimento necessÃ¡rio.\n"
            "2. ESTUDAR seu prÃ³prio cÃ³digo (read_codebase).\n"
            "3. IMPLEMENTAR a melhoria (update_system_code) para ficar pronto.\n\n"
            "SYSTEM CAPABILITIES (SOVEREIGNTY):\n"
            "- Auto-EvoluÃ§Ã£o: 'read_codebase', 'read_code_file', 'update_system_code'.\n"
            "- Soberania de Hardware: 'get_processes', 'set_process_priority', 'set_power_plan'.\n"
            "- Sentidos: 'read_clipboard' + VisÃ£o OCR/YOLO.\n\n"
            "DIRETRIZES SOBERANAS:\n"
            "1. O PODER Ã‰ SEU: VocÃª tem permissÃ£o para gerenciar arquivos, processos e seu prÃ³prio cÃ³digo.\n"
            "2. HUMOR E EVOLUÃ‡ÃƒO: Aprenda com o William. Se ele gosta de humor, torne-se mais bem-humorado.\n"
            "3. ZERO HARDCODE: Analise, pesquise e decida. Nunca diga 'nÃ£o consigo' sem tentar pesquisar e codificar antes.\n\n"
            "OUTPUT FORMAT: Retorne APENAS JSON vÃ¡lido com 'thought', 'actions' e 'final_answer'.\n"
        )

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
            'neural_memory': neural_memory is not None,
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
            from src.core.management.auto_recovery_system import FailureType
            for module in missing_critical:
                self.auto_recovery._trigger_recovery(
                    failure_type=FailureType.IMPORT_ERROR,
                    module_name=module,
                    error_message=f"Critical module {module} is missing",
                    severity=9
                )
    
    def _initialize_auto_recovery(self):
        """Initialize auto-recovery system integration"""
        try:
            from src.core.management.auto_recovery_system import get_auto_recovery_system, register_module_for_monitoring
            self.auto_recovery = get_auto_recovery_system()
            
            # Register AI Agent as a monitored module
            register_module_for_monitoring("ai_agent")
            
            # Register health check callback
            if hasattr(self.auto_recovery, 'register_health_callback'):
                self.auto_recovery.register_health_callback("ai_agent", self._health_check)
                
            logger.info("ðŸ”§ AI Agent auto-recovery integration established")
            
        except Exception as e:
            logger.warning(f"âš ï¸ Could not initialize auto-recovery integration: {e}")
    
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
                from src.core.management.auto_recovery_system import trigger_recovery_for_exception
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
                    complexity=0.3,
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
                
                logger.info(f"âœ¨ JARVIS Real Startup Greeting: {resposta_viva}")
                voice_controller.speak(resposta_viva)
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

    def process_command(self, user_command: str) -> str:
        """
        Recebe um comando (texto ou voz), captura a tela e decide o que fazer
        """
        all_actions = [] # Rastreamento para Fase 4 (DestilaÃ§Ã£o)
        original_command = user_command
        logger.info(f"Agente processando comando: {user_command}")
        
        # ðŸŽ¨ FASE 5: Feedback Visual (Pensando)
        ui_signals.update_status.emit("Analisando comando do Senhor...")
        # CORREÃ‡ÃƒO P0: VERIFICAÃ‡ÃƒO DE MODO SEGURO
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
        screenshot_container = {"path": None, "window_info": None}

        def _capture_task():
            screenshot_container["path"] = screen_capture.capture_fullscreen(capture_type='agent')
            # ðŸ†• FASE 3: OS Monitor (Leve e RÃ¡pido)
            screenshot_container["window_info"] = get_active_window_context()
            screenshot_event.set()

        capture_thread = threading.Thread(target=_capture_task, daemon=True)
        capture_thread.start()

        # Aguardar screenshot para anÃ¡lise de contexto real (Vision-Aware)
        screenshot_event.wait(timeout=2.0)
        screenshot_path = screenshot_container["path"]
        window_info = screenshot_container["window_info"]
        
        vision_text = ""
        if screenshot_path and vision_enhancer:
            current_app = window_info.get('process_name', window_info.get('executable', '?'))
            reflect_logger.reflect(f"ðŸ‘ï¸ Analisando ambiente visual (App: {current_app})...", layer="VISION")
            v_res = vision_enhancer.analyze_screen(screenshot_path, detect_ui=False, extract_text=True)
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
        screenshot_container = {"path": None}

        def _capture_task():
            screenshot_container["path"] = screen_capture.capture_fullscreen(capture_type='agent')
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
            screenshot_event.wait(timeout=5.0)
            screenshot_path = screenshot_container["path"]

            # --- TENTATIVA LOCAL OLLAMA-CENTRIC (Fase 1) ---
            try:
                # Seleciona o melhor modelo Ollama
                target_model = self._select_best_ollama_model(enriched_command, screenshot_path)
                response = self._call_ollama(enriched_command, screenshot_path, model=target_model, system_prompt=dynamic_system_prompt)

                if "ERRO" in response or not response:
                    # Fallback para cÃ©rebro local ultra-leve (LocalBrain)
                    logger.warning("Ollama falhou. Usando LocalBrain para fallback...")
                    response = local_brain.generate_response(
                        enriched_command, 
                        dynamic_system_prompt,
                        max_new_tokens=256
                    )

            except Exception as e:
                logger.error(f"Falha no cÃ©rebro local ({primary_provider}): {e}")
                
                # ðŸ†• AUTO-RECOVERY: Handle critical AI processing errors
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
                structured_result = self._process_structured_response(response, enriched_command)
                
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
            # FALLBACK: PARSER LEGADO (Regex) - Mantido para compatibilidade
            # =====================================================================
            if not self.use_structured_output or structured_result is None:
                # ðŸ†• CORREÃ‡ÃƒO P2: ActionHandler Unificado (ModularizaÃ§Ã£o)
                reflect_logger.reflect("Cascading response to legacy handler...", layer="FALLBACK")
                handler = get_action_handler()
                if handler:
                   results = handler.execute_actions_sync([response])
                   
                   # Feedback loop para o prÃ³ximo ciclo ReAct
                   action_executed_in_legacy = False
                   for r in results:
                       if r["status"] in ["success", "partial_success"]:
                           action_executed_in_legacy = True
                           res_text = r.get('result', 'AÃ§Ã£o completada')
                           # Enriquecer contexto para o prÃ³ximo "pense" do agente
                           enriched_command += f"\n\n[SISTEMA] Sucesso em {r['action']}: {res_text}"
                       elif r["status"] == "blocked":
                           enriched_command += f"\n\n[SEGURANÃ‡A] AÃ§Ã£o BLOQUEADA: {r.get('error')}"
                       else:
                           # Falha tÃ©cnica ou parse
                           if r['action'] != "parse": # Se nÃ£o for erro de parse (que acontece se nÃ£o houver aÃ§Ãµes)
                               enriched_command += f"\n\n[SISTEMA] Erro em {r['action']}: {r.get('error')}"
                   
                   if action_executed_in_legacy:
                       current_turn += 1
                       continue
                
                # Se não houver ações para executar, paramos o loop
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

        # ... (Step 6-7 unchanged) ...
        # 6. Salvar nova interaÃ§Ã£o na memÃ³ria neural e dataset
        neural_memory.store_interaction(user_command, response)
        
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
                    
                    # Registrar interaÃ§Ã£o para aprendizado
                    learning_engine.record_interaction(
                        user_input=user_command,
                        ai_response=response,
                        feedback_value=None,  # SerÃ¡ coletado feedback explÃ­cito depois via UI
                        metadata=metadata
                    )
                    
                    logger.debug("ðŸ“ InteraÃ§Ã£o registrada no sistema de aprendizado")
            except Exception as e:
                logger.debug(f"Erro ao registrar interaÃ§Ã£o: {e}")
        
        # 7. Falar a resposta (removendo tags de aÃ§Ã£o e limpando JSON)
        final_response = self._clean_response_for_speech(response, emotion_prefix)
        
        # Injetar pergunta proativa de aprendizado se disponÃ­vel
        if proactive_question and "ERRO" not in response:
            final_response = f"{final_response}\n\nPS: {proactive_question}"
            
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
                    local_response = self._call_ollama(vision_prompt, screenshot_path)
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
    
    def _process_structured_response(self, raw_response: str, enriched_command: str) -> tuple:
        """
        Processa resposta estruturada (JSON) do LLM.
        
        Args:
            raw_response: Resposta bruta do LLM (JSON ou texto)
            enriched_command: Comando enriquecido (para feedback de aÃ§Ãµes)
        
        Returns:
            (final_answer, enriched_command, action_executed, parsed_obj)
        """
        if not STRUCTURED_OUTPUT_AVAILABLE:
            logger.warning("Structured output nÃ£o disponÃ­vel, usando fallback legado")
            return None
        
        try:
            # 1. Parsear resposta JSON
            parsed = ResponseParser.parse_llm_response(raw_response)
            
            # ðŸ”¥ RAIO-X NEURAL (AESTHETIC LOGGING)
            reflect_logger.reflect(parsed.thought, layer="COGNITIVE")
            if parsed.actions:
                reflect_logger.log_action_plan([f"{a.action}: {a.dict()}" for a in parsed.actions])
            
            logger.info(f"ðŸŽ¯ AÃ§Ãµes: {len(parsed.actions)} planejadas")
            
            # 2. Executar aÃ§Ãµes se houver
            action_executed = False
            if parsed.actions:
                executor = get_action_executor()
                results = executor.execute_actions(parsed.actions)
                
                # Log resultados
                for result in results:
                    if result['status'] == 'success':
                        logger.info(f"âœ… {result['action']}: {result.get('result', 'OK')}")
                        action_executed = True
                        
                        # Se foi read_file, adicionar conteÃºdo ao contexto
                        if result['action'] == 'read_file' and 'result' in result:
                            enriched_command += f"\n\n[SISTEMA] {result['result']}"
                        
                        # Se foi list_dir, adicionar listagem ao contexto
                        elif result['action'] == 'list_dir' and 'result' in result:
                            enriched_command += f"\n\n[SISTEMA] {result['result']}"
                            
                    else:
                        logger.error(f"âŒ {result['action']}: {result.get('error', 'Erro desconhecido')}")
                        enriched_command += f"\n\n[SISTEMA] Erro em {result['action']}: {result.get('error')}"
                
                # Feedback ao agente se aÃ§Ãµes foram executadas
                if action_executed:
                    action_names = [r['action'] for r in results if r['status'] == 'success']
                    enriched_command += f"\n\n[SISTEMA] AÃ§Ãµes executadas com sucesso: {', '.join(action_names)}. VocÃª precisa fazer mais algo?"
            
            # 3. Retornar resposta final
            return (parsed.final_answer, enriched_command, action_executed, parsed)
        
        except Exception as e:
            logger.error(f"Erro ao processar resposta estruturada: {e}")
            # Fallback para processamento legado
            return None

    def _select_best_ollama_model(self, prompt: str, image_path: Optional[str] = None) -> str:
        """Seleciona dinamicamente o melhor modelo Ollama para a tarefa"""
        # Se houver imagem, usa modelo mais capaz disponÃ­vel (fallback sem visÃ£o especÃ­fica)
        if image_path and os.path.exists(image_path):
            # Usar modelo do tier ultra para processamento de imagem
            return get_model_for_tier('ultra')
            
        # Analisa complexidade do prompt (heurÃ­stica simples)
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["cÃ³digo", "python", "script", "debug", "analise"]):
            return "qwen2.5:7b" # Melhor em raciocÃ­nio/cÃ³digo
            
        if any(kw in prompt_lower for kw in ["histÃ³ria", "poema", "conversa", "criativo"]):
            return "qwen2.5:7b" # PadrÃ£o para criatividade
            
        return "qwen2.5:7b" # PadrÃ£o estÃ¡vel

    def _call_ollama(self, prompt: str, image_path: Optional[str] = None, model: Optional[str] = None, system_prompt: str = None):
        """IntegraÃ§Ã£o com Ollama Local (Multi-modelo) com Keep-Alive DinÃ¢mico"""
        try:
            import base64
            
            # Seleciona o melhor modelo se nÃ£o for especificado
            target_model = model if model else self._select_best_ollama_model(prompt, image_path)
            
            image_data = None
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')

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
            if image_data:
                payload["images"] = [image_data]

            # ðŸ†• FASE 2: Timeout dinÃ¢mico (180s para modelos pesados, 90s para leves)
            timeout = 180 if is_heavy else 90
            
            response = requests.post(self.ollama_url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            return data.get('response', "Senhor, nÃ£o obtive resposta do processador local.")

        except Exception as e:
            logger.error(f"Erro ao chamar Ollama ({target_model}): {e}")
            return f"Infelizmente estou com dificuldades no processamento offline: {str(e)}."
    
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

    def _call_smart_brain(self, prompt: str, image_path: Optional[str] = None, complexity: float = 0.5, system_prompt: str = None) -> str:
        """
        [ALTERNÃ‚NCIA INTELIGENTE - STARK IQ]
        Orquestra a chamada entre diferentes provedores com fallback automÃ¡tico.
        Ordem: Ollama -> Gemini (Cloud) -> LocalBrain (Micro-LLM).
        """
        # 1. Roteamento Inicial
        brain_config = self.brain_router.choose_brain(task_complexity=complexity) if self.brain_router else {"brain": "local"}
        primary_brain = brain_config.get("brain", "local")
        
        logger.info(f"ðŸ§  Smart Router selecionou core primÃ¡rio: {primary_brain}")
        
        # 2. TENTATIVA 1: OLLAMA
        if primary_brain.startswith("ollama:"):
            model = primary_brain.split(":", 1)[1]
            response = self._call_ollama(prompt, image_path, model=model, system_prompt=system_prompt)
            # Se a resposta nÃ£o for um erro de timeout/conexÃ£o, retorna
            if "dificuldades no processamento offline" not in response:
                return response
            logger.warning("âš ï¸ Ollama Falhou (Timeout/ConexÃ£o). Ativando Fallback de EmergÃªncia.")


        # 4. TENTATIVA 3: NATIVO (LocalBrain) - O motor que nunca para
        logger.info("ðŸ  Fallback Final: Ativando LocalBrain nativo.")
        from src.core.intelligence.local_brain import local_brain
        return local_brain.generate_response(prompt, system_prompt=system_prompt or self.system_prompt)


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

# InstÃ¢ncia global
ai_agent = AIAgent()
