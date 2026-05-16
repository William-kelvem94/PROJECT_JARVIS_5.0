import datetime
import json
import asyncio
from loguru import logger
from typing import Optional

class BaseTool:
    def __init__(self):
        from ..utils.log_manager import log_manager
        from ..utils.workflow_engine import workflow_engine
        self._log_manager = log_manager
        self._workflow_engine = workflow_engine

    async def _log_activity(self, title: str, detail: str, log_type: str = "info", status: str = "success"):
        """Salva o log de atividade no disco (o frontend consome via API/WebSocket)."""
        entry = {
            "type": "activity_log",
            "title": title,
            "detail": detail,
            "log_type": log_type,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Salva no disco
        self._log_manager.save_log(entry)
        
        # WebSocket broadcasting is available for real-time HUD updates if needed
        # logger.debug(f"Atividade registrada: {title} - {detail}")
