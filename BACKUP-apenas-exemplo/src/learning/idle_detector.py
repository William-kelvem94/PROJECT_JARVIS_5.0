# -*- coding: utf-8 -*-
# src/learning/idle_detector.py
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..utils.safe_execute import safe_execute
from .config_schema import IdleConditions

logger = logging.getLogger("JARVIS-IDLE-DETECTOR")


class IdleDetector:
    """
    Detecta quando o sistema está ocioso baseado em uso de recursos e horário.
    """
    
    def __init__(self, conditions: Optional[IdleConditions] = None):
        self.conditions = conditions or IdleConditions()
        self.idle_start_time: Optional[float] = None
        self.last_check_time: Optional[float] = None
        
    @safe_execute(default=False)
    def is_system_idle(self) -> bool:
        """
        Verifica se o sistema está em estado ocioso.
        
        Returns:
            True se o sistema estiver ocioso e dentro do horário noturno
        """
        current_time = time.time()
        
        # Verificar horário noturno primeiro
        if not self._is_night_time():
            self.idle_start_time = None
            return False
            
        # Verificar recursos do sistema
        if not self._check_system_resources():
            self.idle_start_time = None
            return False
            
        # Iniciar ou atualizar temporizador de ociosidade
        if self.idle_start_time is None:
            self.idle_start_time = current_time
            logger.debug("🕒 Iniciando contagem de ociosidade...")
            return False
            
        # Verificar se atingiu a duração mínima
        idle_duration = current_time - self.idle_start_time
        if idle_duration >= self.conditions.min_idle_duration_seconds:
            logger.debug(f"✅ Sistema ocioso por {idle_duration:.0f}s")
            return True
            
        logger.debug(f"⏳ Ociosidade: {idle_duration:.0f}s/{self.conditions.min_idle_duration_seconds}s")
        return False
    
    @safe_execute(default=False)
    def _is_night_time(self) -> bool:
        """Verifica se está dentro do horário noturno configurado."""
        now = datetime.now()
        current_hour = now.hour
        
        start_hour = self.conditions.night_start_hour
        end_hour = self.conditions.night_end_hour
        
        # Handle overnight periods (e.g., 22:00 to 06:00)
        if start_hour > end_hour:
            return current_hour >= start_hour or current_hour < end_hour
        else:
            return start_hour <= current_hour < end_hour
    
    @safe_execute(default=False)
    def _check_system_resources(self) -> bool:
        """Verifica se CPU e memória estão dentro dos limites configurados."""
        try:
            import psutil
            
            # Verificar CPU (interval=1.0 para leitura precisa)
            cpu_percent = psutil.cpu_percent(interval=1.0)
            if cpu_percent > self.conditions.max_cpu_percent:
                logger.debug(f"🚫 CPU alta: {cpu_percent:.1f}%")
                return False
                
            # Verificar Memória
            memory = psutil.virtual_memory()
            if memory.percent > self.conditions.max_memory_percent:
                logger.debug(f"🚫 Memória alta: {memory.percent:.1f}%")
                return False
                
            logger.debug(f"📊 Recursos OK - CPU: {cpu_percent:.1f}%, Mem: {memory.percent:.1f}%")
            return True
            
        except ImportError:
            logger.warning("📛 psutil não disponível, usando detecção baseada apenas em tempo")
            return True  # Fallback para apenas verificação de tempo
    
    @safe_execute(default={})
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema para monitoramento (não bloqueante)."""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'is_night_time': self._is_night_time(),
            'idle_duration': time.time() - self.idle_start_time if self.idle_start_time else 0,
        }
        
        # Adicionar métricas de sistema se psutil disponível
        # Usa interval=None (não bloqueante) para não travar o loop de status
        try:
            import psutil
            stats.update({
                'cpu_percent': psutil.cpu_percent(interval=None),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
            })
        except Exception:
            pass
            
        return stats
