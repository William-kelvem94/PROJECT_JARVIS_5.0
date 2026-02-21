"""
JARVIS 5.0 - Perception Engine
================================
CORREÃ‡ÃƒO P2: SeparaÃ§Ã£o do God Object AIAgent

RESPONSABILIDADE:
  Gerenciar todas as ENTRADAS perceptuais do sistema:
  - VisÃ£o: Captura de tela, OCR, UI Detection
  - Ãudio: Processamento de voz
  - CÃ¢mera: DetecÃ§Ã£o facial, emoÃ§Ãµes
  - MemÃ³ria: Busca em neural memory

ARQUITETURA:
  AIAgent (Orquestrador)
    â†“
  PerceptionEngine â† ESTE MÃ“DULO
  DecisionEngine
  ActionHandler
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# ============================================================================
# SAFE IMPORTS - Graceful degradation se dependÃªncias nÃ£o disponÃ­veis
# ============================================================================
try:
    from src.core.vision.screen_capture import screen_capture

    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ screen_capture nÃ£o disponÃ­vel: {e}")
    screen_capture = None
    SCREEN_CAPTURE_AVAILABLE = False

try:
    from src.core.vision.camera_controller import camera_controller

    CAMERA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ camera_controller nÃ£o disponÃ­vel: {e}")
    camera_controller = None
    CAMERA_AVAILABLE = False

try:
    from src.core.intelligence.neural_memory import neural_memory

    NEURAL_MEMORY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ neural_memory nÃ£o disponÃ­vel: {e}")
    neural_memory = None
    NEURAL_MEMORY_AVAILABLE = False

try:
    from src.core.vision.ui_detector import ui_detector

    UI_DETECTOR_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"âš ï¸ ui_detector nÃ£o disponÃ­vel: {e}")
    ui_detector = None
    UI_DETECTOR_AVAILABLE = False

try:
    from src.core.intelligence.emotion_detector import emotion_detector

    EMOTION_DETECTOR_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"âš ï¸ emotion_detector nÃ£o disponÃ­vel: {e}")
    emotion_detector = None
    EMOTION_DETECTOR_AVAILABLE = False

try:
    from src.database.models import db_manager, OCRResult

    DATABASE_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"âš ï¸ database nÃ£o disponÃ­vel: {e}")
    db_manager = None
    OCRResult = None
    DATABASE_AVAILABLE = False


class PerceptionEngine:
    """
    Motor de PercepÃ§Ã£o - Gerencia todas as entradas sensoriais do JARVIS

    CAPABILITIES:
      1. VisÃ£o: Screenshot + OCR + UI Detection
      2. CÃ¢mera: Face detection + Emotion recognition
      3. MemÃ³ria: RAG search em neural memory
      4. Contexto: AgregaÃ§Ã£o de todos os dados perceptuais

    USAGE:
      perception = PerceptionEngine()
      context = await perception.gather_context("abrir notepad")
      # context = {
      #     "screenshot_path": "...",
      #     "user_face": "William",
      #     "user_emotion": "happy",
      #     "memory_context": "...",
      #     "ui_elements": [...]
      # }
    """

    def __init__(self):
        """Inicializa engine com verificaÃ§Ã£o de dependÃªncias"""
        self.screen_capture = screen_capture if SCREEN_CAPTURE_AVAILABLE else None
        self.camera = camera_controller if CAMERA_AVAILABLE else None
        self.neural_memory = neural_memory if NEURAL_MEMORY_AVAILABLE else None
        self.ui_detector = ui_detector if UI_DETECTOR_AVAILABLE else None
        self.emotion_detector = emotion_detector if EMOTION_DETECTOR_AVAILABLE else None
        self.db_manager = db_manager if DATABASE_AVAILABLE else None

        # Estado interno
        self.last_screenshot_path: Optional[str] = None
        self.last_user_detected: Optional[str] = None
        self.last_emotion: str = "neutral"

        logger.info("âœ… PerceptionEngine inicializado")
        if not SCREEN_CAPTURE_AVAILABLE:
            logger.warning("âš ï¸ Modo degradado: VisÃ£o desativada")
        if not CAMERA_AVAILABLE:
            logger.warning("âš ï¸ Modo degradado: CÃ¢mera desativada")
        if not NEURAL_MEMORY_AVAILABLE:
            logger.warning("âš ï¸ Modo degradado: MemÃ³ria desativada")

    async def gather_context(
        self, user_command: str, enable_vision: bool = True
    ) -> Dict[str, Any]:
        """
        Coleta TODO contexto perceptual de forma paralela

        Args:
            user_command: Comando do usuÃ¡rio (para busca em memÃ³ria)
            enable_vision: Se True, captura screenshot (default: True)

        Returns:
            DicionÃ¡rio com todos os dados perceptuais:
            {
                "screenshot_path": str ou None,
                "user_face": str ou "Unknown",
                "user_emotion": str (neutral/happy/sad/angry),
                "memory_context": str,
                "ui_elements": List[Dict] ou [],
                "ocr_text": str ou "",
                "timestamp": float
            }
        """
        logger.info("ðŸ” Gathering perceptual context...")

        # FASE 1: LanÃ§ar tasks em paralelo
        tasks = []

        if enable_vision and self.screen_capture:
            tasks.append(self._capture_screen())
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))  # No-op task

        if self.camera:
            tasks.append(self._detect_user())
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))

        if self.neural_memory:
            tasks.append(self._search_memory(user_command))
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))

        # FASE 2: Aguardar todas as tasks (paralelas) com timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=10.0,  # Timeout global de 10s
            )
        except asyncio.TimeoutError:
            logger.error("âŒ Timeout em gather_context (10s)")
            results = [None, None, None]
        except Exception as e:
            logger.error(f"âŒ Erro em gather_context: {e}")
            results = [None, None, None]

        screenshot_path = (
            results[0] if isinstance(results[0], (str, type(None))) else None
        )
        user_face = results[1] if isinstance(results[1], str) else "Unknown"
        memory_context = results[2] if isinstance(results[2], str) else ""

        # FASE 3: Processamento sequencial (depende de screenshot)
        ui_elements = []
        ocr_text = ""

        if screenshot_path and self.ui_detector:
            ui_elements = await self._detect_ui_elements(screenshot_path)

        if screenshot_path and self.db_manager:
            ocr_text = await self._extract_ocr(screenshot_path)

        # FASE 4: Detectar emoÃ§Ã£o
        user_emotion = self.last_emotion
        if self.camera and hasattr(self.camera, "current_emotion"):
            user_emotion = self.camera.current_emotion
            self.last_emotion = user_emotion

        # FASE 5: Construir contexto final
        context = {
            "screenshot_path": screenshot_path,
            "user_face": user_face,
            "user_emotion": user_emotion,
            "memory_context": memory_context,
            "ui_elements": ui_elements,
            "ocr_text": ocr_text,
            "timestamp": asyncio.get_event_loop().time(),
        }

        logger.info(
            f"âœ… Context gathered: vision={bool(screenshot_path)}, user={user_face}, emotion={user_emotion}"
        )
        return context

    async def _capture_screen(self) -> Optional[str]:
        """Captura screenshot de forma assÃ­ncrona com timeout"""
        if not self.screen_capture:
            return None

        try:
            # Rodar captura sÃ­ncrona em thread separada com timeout de 5s
            loop = asyncio.get_event_loop()
            screenshot_path = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self.screen_capture.capture_fullscreen,
                    "agent",  # capture_type
                ),
                timeout=5.0,
            )
            self.last_screenshot_path = screenshot_path
            logger.debug(f"ðŸ“¸ Screenshot: {screenshot_path}")
            return screenshot_path
        except asyncio.TimeoutError:
            logger.error("âŒ Timeout ao capturar tela (5s)")
            return None
        except Exception as e:
            logger.error(f"âŒ Erro ao capturar tela: {e}")
            return None

    async def _detect_user(self) -> str:
        """Detecta usuÃ¡rio pela cÃ¢mera"""
        if not self.camera:
            return "Unknown"

        try:
            # Se camera_controller tem detecÃ§Ã£o async, usar
            if hasattr(self.camera, "detect_faces_async"):
                user = await self.camera.detect_faces_async()
            else:
                # Fallback: rodar sÃ­ncrono em thread
                loop = asyncio.get_event_loop()
                user = await loop.run_in_executor(
                    None, lambda: self.camera.last_seen_user
                )

            self.last_user_detected = user if user else "Unknown"
            return self.last_user_detected
        except Exception as e:
            logger.error(f"âŒ Erro ao detectar usuÃ¡rio: {e}")
            return "Unknown"

    async def _search_memory(self, query: str, top_k: int = 3) -> str:
        """Busca contexto relevante em neural memory"""
        if not self.neural_memory or not query:
            return ""

        try:
            # RAG search
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self.neural_memory.search, query, top_k
            )

            if results:
                memory_text = "\n".join([f"- {r['text']}" for r in results[:top_k]])
                logger.debug(f"ðŸ§  Memory: {len(results)} resultados")
                return f"[MEMÃ“RIA RELEVANTE]\n{memory_text}"
            return ""
        except Exception as e:
            logger.error(f"âŒ Erro ao buscar memÃ³ria: {e}")
            return ""

    async def _detect_ui_elements(self, screenshot_path: str) -> List[Dict[str, Any]]:
        """Detecta elementos de UI na screenshot"""
        if not self.ui_detector:
            return []

        try:
            loop = asyncio.get_event_loop()
            elements = await loop.run_in_executor(
                None, self.ui_detector.detect, screenshot_path
            )
            logger.debug(f"ðŸŽ¯ UI: {len(elements)} elementos detectados")
            return elements or []
        except Exception as e:
            logger.error(f"âŒ Erro ao detectar UI: {e}")
            return []

    async def _extract_ocr(self, screenshot_path: str) -> str:
        """Extrai texto via OCR"""
        if not self.db_manager:
            return ""

        try:
            # Buscar OCR do banco de dados
            loop = asyncio.get_event_loop()

            def _get_ocr():
                if OCRResult:
                    latest_ocr = (
                        self.db_manager.session.query(OCRResult)
                        .order_by(OCRResult.timestamp.desc())
                        .first()
                    )
                    return latest_ocr.text if latest_ocr else ""
                return ""

            ocr_text = await loop.run_in_executor(None, _get_ocr)

            if ocr_text:
                logger.debug(f"ðŸ“ OCR: {len(ocr_text)} caracteres")
            return ocr_text
        except Exception as e:
            logger.error(f"âŒ Erro ao extrair OCR: {e}")
            return ""

    def get_emotional_modifier(self) -> Dict[str, Any]:
        """Retorna modificador de personalidade baseado em emoÃ§Ã£o"""
        if not self.emotion_detector:
            return {"prefix": "", "tone": "neutral"}

        try:
            modifier = self.emotion_detector.get_personality_modifier(self.last_emotion)
            return modifier
        except Exception as e:
            logger.error(f"âŒ Erro ao obter modificador emocional: {e}")
            return {"prefix": "", "tone": "neutral"}


# ============================================================================
# SINGLETON GETTER
# ============================================================================
_perception_engine_instance = None


def get_perception_engine() -> PerceptionEngine:
    """Retorna instÃ¢ncia singleton do PerceptionEngine"""
    global _perception_engine_instance
    if _perception_engine_instance is None:
        _perception_engine_instance = PerceptionEngine()
    return _perception_engine_instance
