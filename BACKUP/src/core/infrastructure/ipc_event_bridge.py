#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - IPC Event Bridge
=============================
FASE 1.5: Ponte de comunicação entre processos para o Event Bus.
Permite que eventos publicados em um processo sejam propagados para o barramento
de eventos em outros processos de forma transparente.
"""

import asyncio
import logging
import multiprocessing
import threading
import queue
import json
from typing import Dict, List, Optional, Any, Set
from src.core.infrastructure.async_event_bus import (
    get_event_bus,
    Event,
    EventType,
    EventPriority,
)

logger = logging.getLogger(__name__)


class IPCEventBridge:
    """
    Bridge que conecta o barramento de eventos entre processos.

    Implementa um canal bidirecional usando multiprocessing.Queue para sincronizar
    eventos entre o processo pai (Kernel) e processos filhos (Workers/Serviços).
    """

    def __init__(self, inbox: multiprocessing.Queue, outbox: multiprocessing.Queue, event_bus):
        """
        Args:
            inbox: Queue de entrada (recebe eventos de outros processos)
            outbox: Queue de saída (envia eventos locais para outros processos)
        """
        self.inbox = inbox
        self.outbox = outbox
        self._running = False
        self._threads: List[threading.Thread] = []
        # OBRIGATÓRIO: sempre usar o event_bus passado
        self._event_bus = event_bus
        self._bridge_id = f"bridge_{id(self)}"

        # Tipos de eventos que NÃO devem ser propagados (loop prevention)
        self._local_only_types: Set[EventType] = {
            EventType.SYSTEM_HEALTH_CHECK,  # Evita tempestade de heartbeats
            # Adicione outros se necessário
        }

        # Buffer para eventos remotos recebidos antes do EventBus estar pronto
        from collections import deque

        self._pending_remote_events = deque(maxlen=256)  # small, bounded buffer

    def start(self):
        """Inicia a sincronização"""
        if self._running:
            return

        self._running = True

        # Capture the running loop for thread-safe operations
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning(
                "Starting IPC Bridge without active event loop - remote events may fail to publish locally"
            )
            self._loop = None

        # 1. Local -> Remote (Direct subscription on main loop)
        self._setup_local_subscription()

        # 1b. Parent → Child: encaminha VISION_ANALYZE do parent para o child
        async def forward_to_child(event):
            logger.debug(f"[BRIDGE PARENT→CHILD] Encaminhando {event.type} → child")
            try:
                # Serializa para dict simples (compatível com Queue)
                event_dict = {
                    "type": event.type.value,
                    "data": event.data,
                    "priority": event.priority.value,
                    "source": event.source or "parent",
                    "metadata": {**getattr(event, 'metadata', {}), "ipc_source": True},
                }
                self.outbox.put_nowait(event_dict)
            except Exception as e:
                logger.error(f"[BRIDGE PARENT→CHILD] Falha ao encaminhar: {e}")

        # Subscreve TODOS os eventos do parent bus e encaminha pro child
        self._event_bus.subscribe_all(forward_to_child)
        logger.info("[BRIDGE] Forward parent→child configurado (todos os eventos)")

        # 2. Remote -> Local (Thread to blocking read from Queue)
        t2 = threading.Thread(
            target=self._remote_to_local_loop, daemon=True, name="IPC_RemoteToLocal"
        )
        t2.start()
        self._threads.append(t2)

        # Test/CI helper: if the environment requests a mock vision child but
        # the child didn't emit readiness (race), queue a synthetic readiness
        # so parent-side subscriptions won't miss it during bootstrap.
        try:
            import os
            if os.getenv("JARVIS_VISION_MOCK", "0") == "1":
                # Avoid duplicates
                if not any(ev.get("type") == "vision.ready" for ev in self._pending_remote_events):
                    self._pending_remote_events.append(
                        {
                            "type": "vision.ready",
                            "data": {"mock": True, "available": True},
                            "priority": "high",
                            "source": "ipc_bridge.synthetic",
                            "metadata": {"ipc_source": True},
                        }
                    )
                    logger.info("IPC Bridge: queued synthetic VISION_READY for mock-mode (env)")
        except Exception:
            pass

        logger.info("🌉 IPC Event Bridge started")

    def stop(self):
        """Para a sincronização"""
        self._running = False
        # Nota: Queues do multiprocessing podem travar se não forem drenadas
        logger.info("🌉 IPC Event Bridge stopped")

    def _setup_local_subscription(self):
        """Configura a subscrição de eventos locais"""

        # Callback para o subscriber local
        async def on_local_event(event: Event):
            if not self._running:
                return

            # Evita propagar eventos que vieram da ponte (loop) ou marcados
            # como locais
            if event.metadata.get("ipc_source") or event.type in self._local_only_types:
                return

            try:
                # Serializa o evento (DataClasses -> Dict)
                event_data = {
                    "type": event.type.value,
                    "data": event.data,
                    "priority": event.priority.value,
                    "source": event.source,
                    "metadata": {**event.metadata, "ipc_source": True},
                }

                logger.info(
                    f"IPC Bridge local->remote: sending event {event.type.value} source={event.source} metadata={event.metadata}"
                )

                # Non-blocking put works fine from main loop
                try:
                    self.outbox.put_nowait(event_data)
                except queue.Full:
                    # Drop silently if remote queue is full
                    logger.warning(
                        f"IPC Bridge local->remote: remote outbox full, dropping event {event.type.value}"
                    )

            except Exception as e:
                logger.error(f"Error in IPC local-to-remote: {e}")

        # Subscreve a TODOS os eventos locais
        # This MUST be called from the loop where EventBus runs
        try:
            self._event_bus.subscribe(list(EventType), on_local_event)
        except Exception as e:
            logger.error(f"Failed to subscribe to local events: {e}")

    def _remote_to_local_loop(self):
        """Escuta a inbox e publica eventos no barramento local

        Robust behaviour:
        - buffer remote events received before EventBus is started
        - wait briefly for EventBus readiness before dropping events
        - retry pending events when EventBus becomes available
        """
        import time
        logger.info(
            f"IPC Remote->Local loop started on thread {threading.current_thread().name}"
        )

        while self._running:
            try:
                # If we have pending remote events and the EventBus is now
                # running, try to flush them first.
                try:
                    bus_running = bool(getattr(self._event_bus, "_running", False))
                    pending = len(self._pending_remote_events) > 0
                except Exception:
                    bus_running = False
                    pending = False

                if pending and bus_running:
                    try:
                        item = self._pending_remote_events.popleft()
                        logger.info(
                            f"Draining pending remote event (bus ready): {item.get('type')}"
                        )
                        if self._loop and getattr(self._loop, "is_running", lambda: False)():
                            self._loop.call_soon_threadsafe(
                                self._publish_remote_event_safe, item
                            )
                        else:
                            # Use event_bus.publish with ipc metadata when possible
                            try:
                                evt_type = EventType(item["type"])
                                prio = EventPriority(item.get("priority", "normal"))
                                self._event_bus.publish(
                                    evt_type,
                                    item.get("data", {}),
                                    priority=prio,
                                    source=item.get("source", "remote"),
                                )
                            except Exception as _e:
                                logger.warning(
                                    f"Failed to drain pending remote event: {_e}"
                                )
                    except IndexError:
                        pass

                # Block with timeout to check for _running flag
                # Drene a fila com timeout para permitir parada limpa
                try:
                    remote_event_dict = self.inbox.get(timeout=0.5)
                except queue.Empty:
                    continue

                if not remote_event_dict or "type" not in remote_event_dict:
                    continue

                # If EventBus hasn't started yet, wait a short while for it to
                # become ready. This prevents events arriving during bootstrap
                # from being dropped by EventBus (which drops events before
                # initialization).
                try:
                    start_wait = time.time()
                    while not getattr(self._event_bus, "_running", False) and (
                        time.time() - start_wait
                    ) < 1.0:
                        time.sleep(0.01)
                except Exception:
                    pass

                # Publica no Barramento Local de forma Thread-Safe
                logger.info(f"IPC Bridge received remote event: type={remote_event_dict.get('type')} loop_captured={bool(self._loop)} bus_running={getattr(self._event_bus, '_running', False)}")

                # If EventBus still not ready, buffer the event and continue
                if not getattr(self._event_bus, "_running", False):
                    try:
                        self._pending_remote_events.append(remote_event_dict)
                        logger.info(
                            f"Buffered remote event until EventBus ready: {remote_event_dict.get('type')}"
                        )
                        continue
                    except Exception:
                        logger.warning(
                            f"Failed to buffer remote event: {remote_event_dict.get('type')}"
                        )


                # If we have the loop captured, publish on it (preferred)
                if self._loop and getattr(self._loop, "is_running", lambda: False)():
                    # Schedule publish on the captured loop thread
                    self._loop.call_soon_threadsafe(
                        self._publish_remote_event_safe, remote_event_dict
                    )
                else:
                    # Fallback: try to publish via event_bus.publish which is
                    # thread-safe (it will schedule on the dispatcher loop).
                    logger.info("IPC Bridge no event loop captured — using fallback publish to event_bus")
                    try:
                        evt_type = EventType(remote_event_dict["type"])
                        prio = EventPriority(remote_event_dict.get("priority", "normal"))

                        # Preserve ipc metadata so subscribers can detect origin
                        event_id = self._event_bus.publish(
                            evt_type,
                            remote_event_dict.get("data", {}),
                            priority=prio,
                            source=remote_event_dict.get("source", "remote"),
                            ipc_metadata=remote_event_dict.get("metadata", {}),
                        )
                        logger.info(f"[CHILD BRIDGE] Publicou evento {evt_type.value} no event bus local (event_id={event_id})")
                        logger.debug(f"IPC Bridge fallback publish succeeded: {evt_type.value}")
                    except Exception as _e:
                        logger.warning(
                            f"Cannot publish remote event (fallback failed): {_e}"
                        )

            except Exception as e:
                logger.error(f"Error in IPC remote-to-local loop: {e}")

    def _publish_remote_event_safe(self, remote_event_dict: Dict[str, Any]):
        """Helper executado dentro do loop principal para publicar evento com segurança"""
        try:
            # Reconstrói argumentos para publicação
            event_type = EventType(remote_event_dict["type"])
            data = remote_event_dict.get("data", {})
            priority = EventPriority(remote_event_dict.get("priority", "normal"))
            source = remote_event_dict.get("source") or "remote"
            # Defensive: ensure we have a string before calling startswith
            if not isinstance(source, str):
                source = str(source)

            # Adiciona prefixo se não tiver
            if not source.startswith("remote."):
                source = f"remote.{source}"

            metadata = remote_event_dict.get("metadata", {})

            logger.info(f"Publishing bridged event to event_bus: {event_type.value} source={source} metadata={metadata}")

            # Publish é síncrono (apenas coloca na queue async), mas deve rodar na thread do loop
            self._event_bus.publish(
                event_type,
                data=data,
                priority=priority,
                source=source,
                ipc_metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Error publishing bridged event: {e}")
