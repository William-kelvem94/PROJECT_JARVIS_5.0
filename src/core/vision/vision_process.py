#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Vision Service Process
===================================
FASE 1.5: Processo independente para o sistema de visão.
Elimina o bloqueio do GIL e permite processamento paralelo real.
"""

from src.core.config.system_manifest import system_manifest
from src.core.vision.vision_system import VisionSystem
from src.core.infrastructure.ipc_event_bridge import IPCEventBridge
from src.core.infrastructure.async_event_bus import (
    get_event_bus,
    EventType,
    EventPriority,
)

import sys
import os
import asyncio
import logging
import multiprocessing
import signal
from pathlib import Path
import time

# Adiciona o diretório raiz ao path se necessário
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))



logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VisionProcess")

# GLOBAL event_bus para o processo filho
event_bus = None


class VisionService:
    """
    Controlador do Serviço de Visão rodando em seu próprio processo.
    """

    def __init__(self, inbox: multiprocessing.Queue, outbox: multiprocessing.Queue):
        self.inbox = inbox
        self.outbox = outbox
        # Crie o event_bus UMA VEZ e garanta que seja global/único
        from src.core.infrastructure.async_event_bus import AsyncEventBus
        self.event_bus = AsyncEventBus()
        self.vision_system = None
        self.bridge = None
        self._running = False

    async def start(self):
        """Inicia o serviço"""
        logger.info("👁️ Starting Vision Service Process...")
        self._running = True


        global event_bus
        event_bus = AsyncEventBus()

        def run_bus_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(event_bus.start())
                logger.info("[CHILD] Event bus start() completado")
                loop.run_forever()
            except Exception as e:
                logger.error(f"[CHILD] Erro no loop do event_bus: {e}")

        event_thread = threading.Thread(target=run_bus_loop, daemon=True, name="EventBusLoop")
        event_thread.start()
        time.sleep(1.0)  # Dá tempo pro loop iniciar e start() completar

        logger.info("[CHILD] Event bus único criado e loop rodando em thread")

        def handler(event):
            logger.info("[CHILD] *** HANDLER EXECUTANDO *** Recebido VISION_ANALYZE: %s", event.data)
            payload = event.data.get("payload", "unknown")
            response = {
                "echo": f"echo_{payload}",
                "original_ts": event.data.get("ts"),
                "received_ts": time.time(),
                "mock": True
            }
            logger.info("[CHILD] Enviando echo: %s", response)
            event_bus.publish(EventType.VISION_SCREEN_ANALYSIS, response)
            logger.info("[CHILD] Echo enviado com sucesso")

        event_bus.subscribe([EventType.VISION_ANALYZE], handler)
        logger.info("[CHILD] Handler registrado no event_bus principal")

        # Passe o MESMO event_bus pro bridge e VisionSystem
        self.bridge = IPCEventBridge(self.inbox, self.outbox, event_bus=event_bus)
        self.bridge.start()
        self.vision_system = VisionSystem(event_bus=event_bus, use_multiprocessing=False)

        # 2. Inicia a Ponte IPC
        self.bridge = IPCEventBridge(self.inbox, self.outbox)
        self.bridge.start()

        # Immediate env-driven probe for CI/test runs (helps parent detect readiness)
        try:
            import os
            if os.getenv("JARVIS_VISION_MOCK", "0") == "1" and self.outbox:
                probe = {
                    "type": EventType.VISION_READY.value,
                    "data": {"camera_index": 0, "mock": True, "available": True},
                    "priority": EventPriority.HIGH.value,
                    "source": "vision_service.probe",
                    "metadata": {"ipc_source": True},
                }
                try:
                    self.outbox.put_nowait(probe)
                    logger.info("VisionService: env-driven VISION_READY probe written to outbox")
                except Exception:
                    pass
        except Exception:
            pass

        # 3. Inicia o Vision System (dentro deste processo) usando o MESMO event_bus
        # já inicializado acima



        # O VisionSystem original inicia threads (_monitor_loop).
        # Como estamos em um processo exclusivo, isso é perfeito.
        # Start monitoring and background loading in a separate thread to
        # prevent any blocking camera initialization (cv2.VideoCapture can
        # block the process on some drivers). This ensures IPC/event loop
        # stays responsive immediately.
        import threading

        def _deferred_start():
            try:
                self.vision_system.start_monitoring()
                self.vision_system.start_background_loading()
            except Exception as e:
                logger.error(f"Vision monitor failed to start in background: {e}")

        starter_thread = threading.Thread(
            target=_deferred_start, daemon=True, name="VisionMonitorStarter"
        )
        starter_thread.start()

        # Fast-path: if we're running with the mock camera, signal readiness
        # immediately so IPC-based tests don't time out waiting for physical
        # devices to initialize. Wait briefly and retry to avoid bootstrap races
        # where the parent bridge/event-bus isn't yet fully started.
        try:
            logger.info(f"VisionService bootstrap: mock_camera={system_manifest.vision.mock_camera} event_bus_present={bool(self.event_bus)}")
            if system_manifest.vision.mock_camera and self.event_bus:
                # Small grace period to reduce race with parent-side bridge/startup
                await asyncio.sleep(0.05)

                payload = {
                    "camera_index": self.vision_system.camera_index,
                    "mock": True,
                    "available": True,
                }

                # Try a few times to publish + write to outbox to ensure parent
                # receives the readiness even under timing races.
                for attempt in range(5):
                    try:
                        self.event_bus.publish(
                            EventType.VISION_READY, payload, priority=EventPriority.HIGH
                        )

                        # Also write a raw IPC message to the outbox queue so parent-side
                        # IPC bridges that rely on `inbox.get()` receive the readiness
                        # event even if local subscription propagation is delayed.
                        if self.outbox:
                            raw = {
                                "type": EventType.VISION_READY.value,
                                "data": payload,
                                "priority": EventPriority.HIGH.value,
                                "source": "vision_service",
                                "metadata": {"ipc_source": True},
                            }
                            try:
                                logger.info("VisionService: writing VISION_READY to outbox")
                                self.outbox.put_nowait(raw)
                                logger.info("VisionService: outbox write succeeded")
                            except Exception as _e:
                                logger.warning(f"VisionService: failed to write outbox: {_e}")

                        break
                    except Exception as e:
                        logger.debug(f"VISION_READY publish attempt {attempt} failed: {e}")
                        await asyncio.sleep(0.05)
        except Exception:
            pass

        logger.info("✅ Vision Service is now running in independent process")

        # Mantém o processo vivo e processando eventos
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.stop()

    async def stop(self):
        """Para o serviço"""
        logger.info("🛑 Stopping Vision Service Process...")
        self._running = False
        if self.vision_system:
            self.vision_system.stop_monitoring()
        if self.bridge:
            self.bridge.stop()
        await self.event_bus.stop()
        logger.info("✅ Vision Service Process stopped")


def run_vision_service(inbox, outbox):
    """Entry point para multiprocessing.Process"""
    logger.info("run_vision_service() invoked in child process")
    service = VisionService(inbox, outbox)

    # Setup asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(service.start())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(service.stop())
        loop.close()


if __name__ == "__main__":
    # Teste isolado (precisaria de queues fakes)
    pass
