"""
JARVIS Perception Manager — Versao Refatorada (02/05/2026)
"""

import threading
import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, List
from loguru import logger

try:
    from app.perception.voice_engine import VoiceResult
except Exception:
    VoiceResult = None

@dataclass
class PerceptionSnapshot:
    face_present: bool = False
    face_identity: Optional[str] = None
    face_emotion: str = "neutral"
    hand_gesture: Optional[str] = None
    wake_word_triggered: bool = False
    voice_validated: bool = False
    offline_transcript: Optional[str] = None
    detected_objects: List[dict] = field(default_factory=list)
    timestamp: str = ""


    def to_dict(self):
        d = asdict(self)
        d["type"] = "perception_update"
        return d

class PerceptionManager:
    def __init__(self):
        self._snapshot = PerceptionSnapshot()
        self._lock = threading.Lock()

    def _update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self._snapshot, k, v)
            self._snapshot.timestamp = datetime.datetime.now().isoformat()

    def get_snapshot(self):
        with self._lock:
            return self._snapshot.to_dict()

    def _on_voice_event(self, result):
        if VoiceResult is None:
            logger.warning("Voice engine not available, ignoring voice event")
            return
        if not isinstance(result, VoiceResult):
            logger.warning(f"Invalid voice result type: {type(result)}")
            return

        updates = {}
        if result.wake_word_triggered:
            # The Shield: Only trigger if voice is validated
            if result.is_validated:
                updates["wake_word_triggered"] = True
                updates["voice_validated"] = True
                logger.success("The Shield: Wake word and Voice VALIDATED!")
            else:
                logger.warning("🛡️ The Shield: Wake word detected but voice NOT validated. Ignoring.")

        if result.offline_transcript:
            updates["offline_transcript"] = result.offline_transcript

        if updates:
            self._update(**updates)


# Instancia global
perception_manager = PerceptionManager()
