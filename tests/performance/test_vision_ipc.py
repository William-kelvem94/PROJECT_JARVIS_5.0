#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Vision IPC Performance Test
========================================
Benchmarks the Round Trip Time (RTT) of the Vision Service IPC Bridge.
"""

import time
import multiprocessing
import logging
import asyncio
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.core.infrastructure.ipc_event_bridge import IPCEventBridge
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority
from src.core.vision.vision_process import run_vision_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IPC_Test")

def main():
    """Run IPC Latency Test"""
    multiprocessing.freeze_support()
    logger.info("🚀 Starting Vision IPC Performance Test")

    # 1. Create Queues
    # queue_to_vision: Main writes, Vision reads
    # queue_from_vision: Vision writes, Main reads
    queue_to_vision = multiprocessing.Queue()
    queue_from_vision = multiprocessing.Queue()

    # 2. Start Vision Process
    # VisionService expects (inbox, outbox) -> reads from first, writes to second
    vision_process = multiprocessing.Process(
        target=run_vision_service,
        args=(queue_to_vision, queue_from_vision),
        name="VisionTestProcess",
        daemon=True
    )
    vision_process.start()
    logger.info(f"✅ Vision Process started (PID: {vision_process.pid})")

    # 4. Start Event Bus
    async def run_test():
        # Start Local Bridge (Main Process) inside the loop
        # Bridge reads from queue_from_vision (inbox), writes to queue_to_vision (outbox)
        local_bridge = IPCEventBridge(queue_from_vision, queue_to_vision)
        local_bridge.start()

        await event_bus.start()
        
        results = []
        pending_requests = {}
        
        # Subscriber for echoes
        async def on_echo(event):
            request_ts = event.data.get("request_ts")
            if request_ts:
                rtt = (asyncio.get_event_loop().time() - request_ts) * 1000 # ms
                results.append(rtt)
                if request_ts in pending_requests:
                    del pending_requests[request_ts]
                # logging.info(f"Received echo in {rtt:.2f}ms")

        event_bus.subscribe([EventType.VISION_SCREEN_ANALYSIS], on_echo)

        # Allow service to boot
        logger.info("⏳ Waiting for service boot (3s)...")
        await asyncio.sleep(3)

        logger.info("🔥 Starting 100 ping requests...")
        start_time = time.time()
        
        count = 100
        for i in range(count):
            ts = asyncio.get_event_loop().time()
            pending_requests[ts] = True
            
            event_bus.publish(
                EventType.VISION_ANALYZE,
                {"payload": f"ping_{i}", "ts": ts},
                priority=EventPriority.HIGH
            )
            
            # Small delay to prevent queue flooding (simulating real usage)
            # await asyncio.sleep(0.01) 
            # Actually, let's flood it to test throughput too
            if i % 10 == 0:
                await asyncio.sleep(0.01)

        # Wait for results
        wait_start = time.time()
        while len(results) < count and (time.time() - wait_start) < 5:
            await asyncio.sleep(0.1)

        total_time = time.time() - start_time
        
        # Stats
        if results:
            avg_rtt = sum(results) / len(results)
            min_rtt = min(results)
            max_rtt = max(results)
            logger.info("=" * 40)
            logger.info(f"📊 IPC Performance Results ({len(results)}/{count} received)")
            logger.info(f"Avg RTT: {avg_rtt:.2f}ms")
            logger.info(f"Min RTT: {min_rtt:.2f}ms")
            logger.info(f"Max RTT: {max_rtt:.2f}ms")
            logger.info(f"Total Time: {total_time:.2f}s")
            logger.info("=" * 40)
        else:
            logger.error("❌ No echoes received! IPC Bridge might be broken.")

        # Cleanup
        local_bridge.stop()
        await event_bus.stop()
        vision_process.terminate()
        vision_process.join()

    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
