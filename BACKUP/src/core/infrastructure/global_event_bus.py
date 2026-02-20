"""
JARVIS 5.0 - Global Event Bus
==============================
Wrapper global para o sistema de eventos assíncronos.
Fornece interface unificada para todo o sistema.
"""

import logging
from typing import Any, Dict, Optional, Callable, Coroutine
from .async_event_bus import AsyncEventBus, EventPriority

logger = logging.getLogger(__name__)


class GlobalEventBus:
    """
    Event Bus global singleton para comunicação entre todos os módulos JARVIS.
    Wrapper sobre AsyncEventBus com interface simplificada.
    """

    _instance: Optional["GlobalEventBus"] = None
    _bus: Optional[AsyncEventBus] = None

    def __new__(cls) -> "GlobalEventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa o event bus"""
        try:
            self._bus = AsyncEventBus()
            logger.info("Global Event Bus initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Global Event Bus: {e}")
            self._bus = None

    async def publish(
        self,
        event: str,
        data: Any = None,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """
        Publica um evento no bus global.

        Args:
            event: Nome do evento
            data: Dados do evento
            priority: Prioridade do evento

        Returns:
            True se publicado com sucesso
        """
        if not self._bus:
            logger.warning("Event bus not initialized")
            return False

        try:
            await self._bus.publish_event(
                {"event": event, "data": data, "priority": priority}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish event {event}: {e}")
            return False

    async def subscribe(
        self,
        event: str,
        callback: Callable[[Any], Coroutine[Any, Any, None]],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """
        Inscreve callback para um evento.

        Args:
            event: Nome do evento
            callback: Função async para processar o evento
            priority: Prioridade da subscription

        Returns:
            True se inscrito com sucesso
        """
        if not self._bus:
            logger.warning("Event bus not initialized")
            return False

        try:
            await self._bus.subscribe_event(event, callback, priority)
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to event {event}: {e}")
            return False

    async def unsubscribe(self, event: str, callback: Callable) -> bool:
        """
        Remove inscrição de evento.

        Args:
            event: Nome do evento
            callback: Callback a remover

        Returns:
            True se removido com sucesso
        """
        if not self._bus:
            return False

        try:
            await self._bus.unsubscribe_event(event, callback)
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe from event {event}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do event bus.

        Returns:
            Dicionário com estatísticas
        """
        if not self._bus:
            return {"status": "not_initialized"}

        try:
            return self._bus.get_bus_stats()
        except Exception as e:
            logger.error(f"Failed to get bus stats: {e}")
            return {"error": str(e)}

    async def shutdown(self) -> None:
        """Encerra o event bus"""
        if self._bus:
            await self._bus.shutdown()
            self._bus = None
            logger.info("Global Event Bus shut down")


# Convenience functions for global access
_global_bus = None


def get_global_event_bus() -> GlobalEventBus:
    """Retorna instância global do event bus"""
    global _global_bus
    if _global_bus is None:
        _global_bus = GlobalEventBus()
    return _global_bus


async def publish_event(
    event: str, data: Any = None, priority: EventPriority = EventPriority.NORMAL
) -> bool:
    """
    Função de conveniência para publicar eventos globalmente.

    Args:
        event: Nome do evento
        data: Dados do evento
        priority: Prioridade

    Returns:
        True se publicado com sucesso
    """
    bus = get_global_event_bus()
    return await bus.publish(event, data, priority)


async def subscribe_event(
    event: str,
    callback: Callable[[Any], Coroutine[Any, Any, None]],
    priority: EventPriority = EventPriority.NORMAL,
) -> bool:
    """
    Função de conveniência para inscrever em eventos globalmente.

    Args:
        event: Nome do evento
        callback: Callback async
        priority: Prioridade

    Returns:
        True se inscrito com sucesso
    """
    bus = get_global_event_bus()
    return await bus.subscribe(event, callback, priority)


# Initialize on import
try:
    _global_bus = GlobalEventBus()
    global_event_bus = _global_bus  # Export for convenience
except Exception as e:
    logger.error(f"Failed to initialize global event bus on import: {e}")
    global_event_bus = None
