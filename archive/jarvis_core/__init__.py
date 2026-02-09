"""
JARVIS Core - Init
"""

__version__ = "1.0.0-singularity"
__author__ = "William"

# Módulos principais
from jarvis_core.hive_mind.rclone_sync import rclone_sync
from jarvis_core.hive_mind.memory_manager import hybrid_memory
from jarvis_core.senses.ui_automation import neural_touch
from jarvis_core.senses.action_dispatcher import action_dispatcher
from jarvis_core.brain.neural_router import get_router
from jarvis_core.mouth.tts_engine import get_tts
from jarvis_core.guardian.privacy_filter import privacy_filter
from jarvis_core.guardian.watchdog import system_watchdog

__all__ = [
    'rclone_sync',
    'hybrid_memory',
    'neural_touch',
    'action_dispatcher',
    'get_router',
    'get_tts',
    'privacy_filter',
    'system_watchdog'
]
