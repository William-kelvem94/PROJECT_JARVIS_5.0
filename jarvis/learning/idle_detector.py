# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("JARVIS-IDLE-DETECTOR")

from .config_schema import IdleConditions

class IdleDetector:
    """Detecta ociosidade baseada em hardware (CPU/RAM) e horário."""

    def __init__(self, conditions: Optional[IdleConditions] = None):
        self.conditions = conditions or IdleConditions()
        self.idle_start_time = None

    def is_system_idle(self) -> bool:
        """Verifica se o sistema pode 'sonhar' agora."""
        # 1. Verificar Horário Noturno
        if not self._is_night_time():
            self.idle_start_time = None
            return False

        # 2. Verificar Recursos
        if not self._check_resources():
            self.idle_start_time = None
            return False

        # 3. Verificar Duração
        if self.idle_start_time is None:
            self.idle_start_time = time.time()
            return False

        if (time.time() - self.idle_start_time) >= self.conditions.min_idle_duration_seconds:
            return True

        return False

    def _is_night_time(self) -> bool:
        now = datetime.now()
        hour = now.hour
        start, end = self.conditions.night_start_hour, self.conditions.night_end_hour
        if start > end: # Virada de noite (ex: 22 as 06)
            return hour >= start or hour < end
        return start <= hour < end

    def _check_resources(self) -> bool:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None) # Não bloqueante
            mem = psutil.virtual_memory().percent
            return cpu < self.conditions.max_cpu_percent and mem < self.conditions.max_memory_percent
        except ImportError:
            return True # Fallback se não houver psutil

    def get_system_stats(self) -> Dict[str, Any]:
        """Útil para o Dashboard."""
        try:
            import psutil
            return {
                "cpu": psutil.cpu_percent(interval=None),
                "ram": psutil.virtual_memory().percent,
                "is_night": self._is_night_time()
            }
        except:
            return {"error": "psutil_missing"}
