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

    def __init__(self, inbox: multiprocessing.Queue, outbox: multiprocessing.Queue):
        """
        Args:
            inbox: Queue de entrada (recebe eventos de outros processos)
            outbox: Queue de saída (envia eventos locais para outros processos)
        """
        self.inbox = inbox
        self.outbox = outbox
        self._running = False
        self._threads: List[threading.Thread] = []
        self._event_bus = get_event_bus()
        self._bridge_id = f"bridge_{id(self)}"

        # Tipos de eventos que NÃO devem ser propagados (loop prevention)
        self._local_only_types: Set[EventType] = {
            EventType.SYSTEM_HEALTH_CHECK,  # Evita tempestade de heartbeats
            # Adicione outros se necessário
        }

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

        # 2. Remote -> Local (Thread to blocking read from Queue)
        # We need a thread because Queue.get() is blocking and we can't block
        # the async loop
        t2 = threading.Thread(
            target=self._remote_to_local_loop, daemon=True, name="IPC_RemoteToLocal"
        )
        t2.start()
        self._threads.append(t2)

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
                # Non-blocking put works fine from main loop
                self.outbox.put_nowait(event_data)
            except queue.Full:
                pass
            except Exception as e:
                logger.error(f"Error in IPC local-to-remote: {e}")

        # Subscreve a TODOS os eventos locais
        # This MUST be called from the loop where EventBus runs
        try:
            self._event_bus.subscribe(list(EventType), on_local_event)
        except Exception as e:
            logger.error(f"Failed to subscribe to local events: {e}")

    def _remote_to_local_loop(self):
        """Escuta a inbox e publica eventos no barramento local"""
        logger.info(
            f"IPC Remote->Local loop started on thread {threading.current_thread().name}"
        )
        while self._running:
            try:
                # Block with timeout to check for _running flag
                # Drene a fila com timeout para permitir parada limpa
                try:
                    remote_event_dict = self.inbox.get(timeout=0.5)
                except queue.Empty:
                    continue

                if not remote_event_dict or "type" not in remote_event_dict:
                    continue

                # Publica no Barramento Local de forma Thread-Safe
                if self._loop and self._loop.is_running():
                    self._loop.call_soon_threadsafe(
                        self._publish_remote_event_safe, remote_event_dict
                    )
                else:
                    logger.warning(
                        "Cannot publish remote event: No active event loop captured"
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
            source = remote_event_dict.get("source", "remote")
            # Adiciona prefixo se não tiver
            if not source.startswith("remote."):
                source = f"remote.{source}"
            
            metadata = remote_event_dict.get("metadata", {})
            
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
