#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Vision Service Process
===================================
FASE 1.5: Processo independente para o sistema de visão.
Elimina o bloqueio do GIL e permite processamento paralelo real.
"""

import sys
import os
import asyncio
import logging
import multiprocessing
import signal
from pathlib import Path

# Adiciona o diretório raiz ao path se necessário
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.core.infrastructure.async_event_bus import get_event_bus, EventType, EventPriority
from src.core.infrastructure.ipc_event_bridge import IPCEventBridge
from src.core.vision.vision_system import VisionSystem
from src.core.config.system_manifest import system_manifest

# Configuração de Logs para o processo filho
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VisionProcess")

class VisionService:
    """
    Controlador do Serviço de Visão rodando em seu próprio processo.
    """
    
    def __init__(self, inbox: multiprocessing.Queue, outbox: multiprocessing.Queue):
        self.inbox = inbox
        self.outbox = outbox
        self.event_bus = get_event_bus()
        self.vision_system = None
        self.bridge = None
        self._running = False

    async def start(self):
        """Inicia o serviço"""
        logger.info("👁️ Starting Vision Service Process...")
        self._running = True
        
        # 1. Inicia o Barramento de Eventos Local
        await self.event_bus.start()
        
        # 2. Inicia a Ponte IPC
        self.bridge = IPCEventBridge(self.inbox, self.outbox)
        self.bridge.start()
        
        # 3. Inicia o Vision System (dentro deste processo)
        self.vision_system = VisionSystem(event_bus=self.event_bus, use_multiprocessing=False)
        
        # Handler para teste de latência (RTT)
        async def on_ping(event):
            # Echo back
            request_ts = event.data.get("ts", 0)
            self.event_bus.publish(
                EventType.VISION_SCREEN_ANALYSIS,
                {
                    "echo": event.data.get("payload"), 
                    "request_ts": request_ts,
                    "response_ts": asyncio.get_event_loop().time()
                },
                priority=EventPriority.HIGH
            )
            
        self.event_bus.subscribe([EventType.VISION_ANALYZE], on_ping)
        
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

        threading.Thread(
            target=_deferred_start, daemon=True, name="VisionMonitorStarter"
        ).start()
        
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
