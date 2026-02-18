#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Service Process
---------------------
Runs `EnhancedAudioSystem` in a separate process and bridges events to the
main process using `IPCEventBridge`.

Behavior:
- Starts local EventBus inside child process
- Instantiates `EnhancedAudioSystem(event_bus=child_event_bus)` when available
- Publishes `EventType.AUDIO_READY` (available: True/False, mock: False)
- Keeps running until terminated
"""

import asyncio
import logging
import multiprocessing
import threading
import time
from pathlib import Path

from src.core.infrastructure.async_event_bus import (
    get_event_bus,
    EventType,
    EventPriority,
)
from src.core.infrastructure.ipc_event_bridge import IPCEventBridge

logger = logging.getLogger("AudioProcess")


class AudioService:
    def __init__(self, inbox: multiprocessing.Queue, outbox: multiprocessing.Queue):
        self.inbox = inbox
        self.outbox = outbox
        self.event_bus = get_event_bus()
        self.bridge = IPCEventBridge(self.inbox, self.outbox)
        self.audio = None
        self._running = False

    async def start(self):
        logger.info("🔊 Starting Audio Service Process...")
        self._running = True

        # Start IPC bridge (in child it will bridge this process' event bus)
        self.bridge.start()

        # Try to instantiate EnhancedAudioSystem (may degrade if deps missing)
        try:
            from src.core.audio.enhanced_audio import EnhancedAudioSystem

            self.audio = EnhancedAudioSystem(Path("data"), event_bus=self.event_bus)
            # When available, EnhancedAudioSystem already publishes transcription events
            # Start listening if supported
            try:
                self.audio.start_listening()
            except Exception as e:
                logger.warning(f"Audio start_listening failed (child): {e}")

            available = True
        except Exception as e:
            logger.warning(f"EnhancedAudioSystem not available in child: {e}")
            self.audio = None
            available = False

        # Publish readiness
        try:
            self.event_bus.publish(
                EventType.AUDIO_READY,
                {"available": available, "mock": False},
                priority=EventPriority.HIGH,
            )
        except Exception as e:
            logger.debug(f"Failed to publish AUDIO_READY: {e}")

        # Keep process alive
        try:
            while self._running:
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def stop(self):
        logger.info("🛑 Stopping Audio Service Process...")
        self._running = False
        try:
            if self.audio:
                try:
                    self.audio.stop_listening()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.bridge.stop()
        except Exception:
            pass
        try:
            await self.event_bus.stop()
        except Exception:
            pass
        logger.info("✅ Audio Service Process stopped")


def run_audio_service(inbox, outbox):
    """Entry point used by multiprocessing.Process"""
    service = AudioService(inbox, outbox)

    # Setup asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(service.start())
    except KeyboardInterrupt:
        pass
    finally:
        try:
            loop.run_until_complete(service.stop())
        except Exception:
            pass
        loop.close()


if __name__ == "__main__":
    # Manual test (requires environment with event bus)
    pass
