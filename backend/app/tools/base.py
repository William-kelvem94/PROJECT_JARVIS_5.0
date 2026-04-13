import datetime
import json
import asyncio
from loguru import logger
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from livekit.rtc import Room

class BaseTool:
    def __init__(self, room: Optional["Room"] = None):
        self._room = room
        from ..utils.log_manager import log_manager
        from ..utils.workflow_engine import workflow_engine
        self._log_manager = log_manager
        self._workflow_engine = workflow_engine

    async def _log_activity(self, title: str, detail: str, log_type: str = "info", status: str = "success"):
        """Envia o log para o frontend via LiveKit e salva no disco."""
        entry = {
            "type": "activity_log",
            "title": title,
            "detail": detail,
            "log_type": log_type,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 1. Salva no disco
        self._log_manager.save_log(entry)
        
        # 2. Envia para o frontend (Real-time) via LiveKit
        if self._room and self._room.connection_state == "connected":
            try:
                await self._room.local_participant.publish_data(
                    json.dumps(entry),
                    topic="activity"
                )
            except Exception as e:
                logger.error(f"Falha ao publicar log de atividade: {e}")
