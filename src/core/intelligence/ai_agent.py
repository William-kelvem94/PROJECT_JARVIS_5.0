"""
Orquestrador do Agente de IA
Gerencia interação entre visão (OCR), decisão (LLM) e ação (PyAutoGUI)
"""

import logging
import threading
from typing import Dict, Any

# Safe Library Imports
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

# Core Configuration
from src.utils.config import config
from src.utils.env_manager import get_model_for_tier

# UI Signals (Safe Import)
try:
    from src.interface.ui_signals import ui_signals
except ImportError:

    class MockSignal:
        def emit(self, *args):
            pass

    class MockSignals:
        update_status = MockSignal()

    ui_signals = MockSignals()

# Logger Setup
logger = logging.getLogger(__name__)

# ============================================================================
# CORE IMPORTS - SAFE LOADING
# ============================================================================
# Instinct Engine
try:
    from src.core.intelligence.instinct_engine import instinct_engine
except ImportError:
    instinct_engine = None

# Hardware Control
try:
    from src.utils.hardware_control import hw_control
except ImportError:

    class MockHW:
        def get_last_system_errors(self):
            return []

        def set_system_volume(self, *args):
            pass

    hw_control = MockHW()

# Context Manager
try:
    from src.core.management.context_manager import context_manager
except ImportError:

    class MockContext:
        night_mode = False

        def should_be_quiet(self):
            return False

        def check_politeness(self):
            return True

        def should_initiate_conversation(self):
            return False

        def record_interaction(self, *args, **kwargs):
            pass

        def update_visual_context(self, *args):
            pass

    context_manager = MockContext()

# Voice Filter
try:
    from src.core.audio.voice_filter import AtomicVoiceFilter
except Exception:
    AtomicVoiceFilter = None

# Database Models
try:
    from src.database.models import db_manager, OCRResult
except ImportError:
    db_manager = None
    OCRResult = None

# Vision System Components
try:
    from src.core.vision.screen_capture import screen_capture
except ImportError:
    screen_capture = None

try:
    from src.core.actions.action_controller import action_controller
except ImportError:
    action_controller = None

try:
    from src.core.audio.voice_controller import voice_controller
except ImportError:
    voice_controller = None

try:
    from src.core.vision.camera_controller import camera_controller
except ImportError:
    camera_controller = None

# Brain Router
try:
    from src.core.intelligence.brain_router import (
        brain_router,
        PrivacyLevel,
        LatencyRequirement,
    )
except ImportError:
    brain_router = None
    PrivacyLevel = None
    LatencyRequirement = None

try:
    from src.core.intelligence.local_brain import local_brain
except ImportError:
    local_brain = None

try:
    from src.core.vision.ui_detector import ui_detector
except ImportError:
    ui_detector = None

try:
    from src.core.intelligence.emotion_detector import emotion_detector
except ImportError:
    emotion_detector = None

# Security Manager (Lazy Load)
security_manager = None

# ============================================================================
# SYSTEM CONTROLLER (GOD MODE)
# ============================================================================
try:
    from src.core.actions.system_controller import system_controller
except ImportError:
    system_controller = None

# ============================================================================
# MEMORY MANAGER
# ============================================================================
try:
    from src.core.intelligence.memory import memory_manager
except ImportError:
    memory_manager = None

# ============================================================================
# LEARNING ENGINE
# ============================================================================
try:
    from src.learning.learning_engine import get_learning_engine
except ImportError:
    get_learning_engine = None

try:
    from src.learning.knowledge_distiller import knowledge_distiller
except ImportError:
    knowledge_distiller = None

try:
    from src.learning.curiosity_engine import CuriosityEngine

    curiosity_engine = CuriosityEngine()
except ImportError:
    curiosity_engine = None

# ============================================================================
# VISION ENHANCER
# ============================================================================
try:
    from src.core.vision.vision_enhancer import vision_enhancer
except ImportError:
    vision_enhancer = None

# ============================================================================
# PERFORMANCE OPTIMIZER
# ============================================================================
try:
    from src.core.management.performance_optimizer import performance_optimizer
except ImportError:
    performance_optimizer = None

# ============================================================================
# STRUCTURED OUTPUT & ACTIONS
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
except ImportError:
    STRUCTURED_OUTPUT_AVAILABLE = False

# ============================================================================
# STARK EVOLUTION MODULES
# ============================================================================
try:
    from src.core.intelligence.analisador_contexto import analisador_contexto
    from src.core.intelligence.stark_nexus import stark_nexus
    from src.core.management.device_manager import device_manager
    from src.core.intelligence.neural_dreaming import neural_dreaming
    from src.learning.neural_curiosity import neural_curiosity
except ImportError:
    analisador_contexto = None
    stark_nexus = None
    device_manager = None
    neural_dreaming = None

try:
    from src.core.vision.os_monitor import get_active_window_context
    from src.core.security.action_validator import action_validator
except ImportError:
    get_active_window_context = lambda: {
        "title": "Unknown",
        "executable": "Unknown",
        "process_name": "Unknown",
    }
    action_validator = None

try:
    from src.utils.web_emitter import emit_status_sync, emit_log_sync
except ImportError:
    emit_status_sync = lambda *args, **kwargs: None
    emit_log_sync = lambda *args, **kwargs: None

# ============================================================================
# ADVANCED MODULES
# ============================================================================
try:
    from src.core.actions.advanced_action_controller import advanced_action_controller

    ADVANCED_ACTIONS_AVAILABLE = True
except ImportError:
    ADVANCED_ACTIONS_AVAILABLE = False
    advanced_action_controller = None

try:
    from src.core.vision.advanced_vision_pipeline import advanced_vision_pipeline

    ADVANCED_VISION_AVAILABLE = True
except ImportError:
    ADVANCED_VISION_AVAILABLE = False
    advanced_vision_pipeline = None

try:
    from src.core.audio.advanced_speech_processor import advanced_speech_processor

    ADVANCED_SPEECH_AVAILABLE = True
except ImportError:
    ADVANCED_SPEECH_AVAILABLE = False
    advanced_speech_processor = None

try:
    from src.core.actions.workflow_engine import workflow_engine

    WORKFLOW_ENGINE_AVAILABLE = True
except ImportError:
    WORKFLOW_ENGINE_AVAILABLE = False
    workflow_engine = None

try:
    from src.core.security.security_manager_advanced import (
        security_manager as security_manager_advanced,
    )

    ADVANCED_SECURITY_AVAILABLE = True
except ImportError:
    ADVANCED_SECURITY_AVAILABLE = False
    security_manager_advanced = None

# ============================================================================
# AI AGENT CLASS
# ============================================================================


class AIAgent:
    """Classe principal do Agente Inteligente"""

    def __init__(self, provider: str = "ollama"):
        self.auto_recovery = None
        self._initialize_auto_recovery()
        self.safe_mode = False
        self._verify_critical_dependencies()

        self.provider = provider

        # OLLAMA URL from Config
        try:
            from src.utils.env_manager import get_config

            config_obj = get_config()
            self.ollama_url = f"{config_obj.ollama_url}/api/generate"
        except ImportError:
            self.ollama_url = "http://localhost:11434/api/generate"

        # AI Config
        self.ai_config = config.get_ai_config()
        self.max_react_turns = config.get_ai_config("ai_agent.max_react_turns", 5)
        self.screenshot_timeout = config.get_ai_config(
            "ai_agent.screenshot_timeout", 5.0
        )

        # History
        self.chat_history = []

        # Brain Router
        self.brain_router = brain_router
        if self.brain_router:
            self.brain_router.on_heavy_model_loading = self._on_heavy_model_loading

        # Components
        self.advanced_actions = (
            advanced_action_controller if ADVANCED_ACTIONS_AVAILABLE else None
        )
        self.advanced_vision = (
            advanced_vision_pipeline if ADVANCED_VISION_AVAILABLE else None
        )
        self.advanced_speech = (
            advanced_speech_processor if ADVANCED_SPEECH_AVAILABLE else None
        )
        self.workflow_engine = workflow_engine if WORKFLOW_ENGINE_AVAILABLE else None
        self.security_advanced = (
            security_manager_advanced if ADVANCED_SECURITY_AVAILABLE else None
        )

        # Agent Delegates
        try:
            from .agent.prompt_manager import AgentPromptManager
            from .agent.engagement_manager import AgentEngagementManager

            self.prompt_manager = AgentPromptManager()
            self.engagement_manager = AgentEngagementManager(self)
            self.system_prompt = self.prompt_manager.get_system_prompt()
        except ImportError:
            self.prompt_manager = None
            self.engagement_manager = None
            self.system_prompt = "You are JARVIS."

        self.use_structured_output = STRUCTURED_OUTPUT_AVAILABLE
        self.event_bus = None

        # Sensory awareness (agent nasce 'cego' até receber VISION_READY/AUDIO_READY)
        self.vision_ready = False
        self.vision_mock_mode = False
        self.audio_ready = False
        self.audio_mock_mode = False

    def connect_event_bus(self, event_bus):
        """Connects AI Agent to AsyncEventBus"""
        try:
            from src.core.infrastructure.async_event_bus import EventType

            self.event_bus = event_bus
            if self.event_bus:
                logger.info("✅ AI Agent connected to AsyncEventBus.")
                # Subscrição padrão (visão dinâmica)
                self.event_bus.subscribe(
                    EventType.VISION_SCREEN_CHANGE, self._handle_vision_event
                )

                # Ouvido para prontidão do subsistema de visão (Boot orientado a eventos)
                try:
                    self.event_bus.subscribe(EventType.VISION_READY, self._on_vision_ready)
                    logger.debug("AI Agent subscribed to VISION_READY events")
                except Exception as e:
                    logger.debug(f"Failed to subscribe to VISION_READY: {e}")

                # Ouvido para subsistema de áudio (AUDIO_READY + transcrições)
                try:
                    self.event_bus.subscribe(EventType.AUDIO_READY, self._on_audio_ready)
                    self.event_bus.subscribe(EventType.AUDIO_TRANSCRIPTION, self._on_audio_transcription)
                    logger.debug("AI Agent subscribed to AUDIO_READY and AUDIO_TRANSCRIPTION events")
                except Exception as e:
                    logger.debug(f"Failed to subscribe to audio events: {e}")

                # Let BrainRouter also be aware of the event bus if present
                try:
                    if self.brain_router and hasattr(self.brain_router, "connect_event_bus"):
                        self.brain_router.connect_event_bus(self.event_bus)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Failed to connect event bus: {e}")

    def _verify_critical_dependencies(self):
        """Checks for critical dependencies and sets Safe Mode."""
        critical_modules = {
            "voice_controller": voice_controller,
            "vision_enhancer": vision_enhancer,
            "screen_capture": screen_capture,
            "action_controller": action_controller,
        }

        missing = [name for name, mod in critical_modules.items() if mod is None]

        if missing:
            self.safe_mode = True
            logger.critical(f"❌ MISSING CRITICAL MODULES: {missing}")
            logger.critical("🔒 ENTERING SAFE MODE")
        else:
            self.safe_mode = False

    def _initialize_auto_recovery(self):
        try:
            from src.core.management.universal_recovery_manager import (
                get_universal_recovery_manager,
                register_module_for_monitoring,
            )

            self.auto_recovery = get_universal_recovery_manager()
            register_module_for_monitoring("ai_agent")
            if hasattr(self.auto_recovery, "register_health_callback"):
                self.auto_recovery.register_health_callback(
                    "ai_agent", self._health_check
                )
        except Exception:
            pass

    def _health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if not self.safe_mode else "degraded",
            "safe_mode": self.safe_mode,
        }

    def _on_heavy_model_loading(self, message: str):
        if voice_controller:
            threading.Thread(
                target=voice_controller.speak, args=(message,), daemon=True
            ).start()

    async def _on_vision_ready(self, event):
        """Callback acionado quando o subsistema de visão publica VISION_READY.

        Atualiza o estado interno (`vision_ready`, `vision_mock_mode`) e
        informa via log/voz se apropriado.
        """
        try:
            payload = getattr(event, "data", {}) or {}
            available = payload.get("available", False)
            mock_mode = payload.get("mock", False)

            if available:
                self.vision_ready = True
                self.vision_mock_mode = bool(mock_mode)

                logger.info(
                    f"👁️ Vision subsystem ready (mock={self.vision_mock_mode}) — AI Agent now 'can see'"
                )

                # Feedback auditável (voz opcional)
                try:
                    if voice_controller:
                        threading.Thread(
                            target=voice_controller.speak,
                            args=(
                                "Sistemas visuais online. Operando em modo de simulação." 
                                if self.vision_mock_mode
                                else "Sistemas visuais online.",
                            ),
                            daemon=True,
                        ).start()
                except Exception:
                    pass
            else:
                self.vision_ready = False
                logger.warning("⚠️ Vision subsystem reported NOT available — agent remains blind")
        except Exception as e:
            logger.error(f"Error handling VISION_READY event: {e}")

    async def _on_audio_ready(self, event):
        """Handler for AUDIO_READY - updates audio_ready state."""
        try:
            payload = getattr(event, "data", {}) or {}
            available = payload.get("available", False)
            mock_mode = payload.get("mock", False)

            self.audio_ready = bool(available)
            self.audio_mock_mode = bool(mock_mode)

            if available:
                logger.info(f"🔊 Audio subsystem ready (mock={self.audio_mock_mode})")
            else:
                logger.warning("🔇 Audio subsystem reported NOT available")
        except Exception as e:
            logger.error(f"Error handling AUDIO_READY event: {e}")

    async def _on_audio_transcription(self, event):
        """Receives audio.transcription events and forwards to process_command.

        Runs asynchronously and does not block the event loop while processing.
        """
        try:
            payload = getattr(event, "data", {}) or {}
            text = (payload.get("text") or "").strip()
            if not text:
                return

            logger.debug(f"🔊 AUDIO_TRANSCRIPTION received: {text[:80]}")

            # Enfileirar o processamento do comando (fire-and-forget)
            try:
                import asyncio

                asyncio.create_task(self.process_command(text))
            except Exception as e:
                # Last-resort: run in thread
                threading.Thread(target=lambda: asyncio.run(self.process_command(text)), daemon=True).start()
        except Exception as e:
            logger.error(f"Error handling AUDIO_TRANSCRIPTION: {e}")

    async def process_command(self, user_command: str) -> str:
        """Main processing loop for user commands."""
        logger.info(f"Processing command: {user_command}")
        ui_signals.update_status.emit("Analisando...")

        if self.safe_mode:
            return "Modo de segurança ativo. Verifique as dependências."

        # 1. Check Instinct Engine
        if instinct_engine:
            instinct_res = await instinct_engine.check(user_command)
            if instinct_res:
                response = instinct_res.get("final_answer", "")
                if voice_controller:
                    voice_controller.speak(response)
                return response

        # 2. Performance Cache
        if performance_optimizer:
            cached = performance_optimizer.get_cached_response(user_command)
            if cached:
                if voice_controller:
                    voice_controller.speak(cached)
                return cached

        # 3. Vision Context
        vision_text = ""
        screenshot_image = None
        # Só usar visão se o subsistema reportou prontidão (Boot orientado a eventos)
        if screen_capture and getattr(self, "vision_ready", False):
            # Simple synchronous capture for robustness in this refactor
            try:
                screenshot_image = screen_capture.capture_fullscreen(
                    capture_type="agent", return_image=True
                )
                if screenshot_image and vision_enhancer:
                    v_res = vision_enhancer.analyze_screen(
                        image_data=screenshot_image, detect_ui=False, extract_text=True
                    )
                    vision_text = " ".join(
                        [t["text"] for t in v_res.get("text_regions", [])]
                    )
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
        else:
            if screen_capture and not getattr(self, "vision_ready", False):
                logger.debug("Vision subsystem not ready — skipping screenshot_capture")

        # 4. Memory Context
        memory_context = ""
        if memory_manager:
            try:
                memory_context = memory_manager.get_context(user_command)
            except:
                pass

        # 5. Build Prompt
        final_prompt = (
            f"Context: {vision_text}\nMemory: {memory_context}\nCommand: {user_command}"
        )

        # 6. Call LLM (Ollama)
        response = await self._call_ollama_async(final_prompt, screenshot_image)

        # 7. Post-process (Actions)
        # Simplified action execution for reliability
        if self.use_structured_output and "{" in response:
            # Try parse actions
            pass

        # 8. Record Interaction
        if get_learning_engine:
            try:
                le = get_learning_engine()
                if le:
                    le.record_interaction(user_command, response)
            except:
                pass

        # 9. Speak
        clean_response = self._clean_response_for_speech(response)
        if voice_controller:
            voice_controller.speak(clean_response)

        return clean_response

    async def _call_ollama_async(
        self,
        prompt: str,
        image_data: Any = None,
        model: str = None,
        system_prompt: str = None,
    ) -> str:
        if not AIOHTTP_AVAILABLE:
            return "Erro: aiohttp não instalado."

        target_model = model or "gemma2:2b"  # Fallback model

        # Try to get better model from config
        try:
            target_model = get_model_for_tier("pro")
        except:
            pass

        payload = {
            "model": target_model,
            "prompt": f"{system_prompt or self.system_prompt}\n\nUser: {prompt}",
            "stream": False,
        }

        # Handle Image
        if image_data:
            # Convert to base64 if needed
            pass

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ollama_url, json=payload, timeout=60
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "")
                    else:
                        return f"Erro Ollama: {resp.status}"
        except Exception as e:
            logger.error(f"Ollama Call Failed: {e}")
            return "Erro ao conectar com o cérebro local."

    def _clean_response_for_speech(self, text: str) -> str:
        return text.replace("*", "").strip()

    async def _handle_vision_event(self, event_data: dict):
        pass


# Global Instance
ai_agent = AIAgent()
