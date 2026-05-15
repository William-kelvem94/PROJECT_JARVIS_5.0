"""
JARVIS Perception Manager — Versao Refatorada (02/05/2026)
"""

import asyncio
import threading
import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, Callable, List
import gc
import torch
from loguru import logger

from app.perception.face_engine import analyze_frame as _face_analyze, FaceResult as _FaceResult
from app.perception.gesture_engine import analyze_frame as _gesture_analyze
from app.perception.object_engine import object_engine as _object_engine
from app.perception.voice_engine import VoiceResult

from app.config import settings
from app.voice.tts_engine import tts_engine 

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
        self._wake_callbacks: List[Callable] = []
        self._gesture_callbacks: List[Callable] = []

    def on_wake_word(self, callback: Callable):
        self._wake_callbacks.append(callback)

    def on_gesture(self, callback: Callable):
        self._gesture_callbacks.append(callback)

    def _update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self._snapshot, k, v)
            self._snapshot.timestamp = datetime.datetime.now().isoformat()

    def get_snapshot(self):
        with self._lock:
            return self._snapshot.to_dict()

    def _on_voice_event(self, result: VoiceResult):
        updates = {}
        if result.wake_word_triggered:
            # The Shield: Only trigger if voice is validated
            if result.is_validated:
                updates["wake_word_triggered"] = True
                updates["voice_validated"] = True
                logger.success("🛡️ The Shield: Wake word and Voice VALIDATED!")
                for cb in self._wake_callbacks:
                    try:
                        cb()
                    except Exception as e:
                        logger.warning(f"Wake callback error: {e}")
            else:
                logger.warning("🛡️ The Shield: Wake word detected but voice NOT validated. Ignoring.")

        if result.offline_transcript:
            updates["offline_transcript"] = result.offline_transcript

        if updates:
            self._update(**updates)


# Instancia global
perception_manager = PerceptionManager()
