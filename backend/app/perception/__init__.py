"""
JARVIS Perception Package
Adaptive multi-modal sensing: Face, Gesture and Voice recognition.
All capabilities degrade gracefully based on installed libraries.
"""
from .perception_manager import perception_manager, PerceptionSnapshot
from . import voice_engine, face_engine, gesture_engine

__all__ = [
    "perception_manager",
    "PerceptionSnapshot",
    "voice_engine",
    "face_engine",
    "gesture_engine",
]
