from src.core.infrastructure.watchdog import watchdog_system
from src.core.infrastructure.priority_scheduler import (
    priority_scheduler,
    TaskPriority,
    TaskType,
)
import asyncio
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Garantir output UTF-8 para emojis no Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

# Root path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def test_priority_scheduler():
    print("\n\U0001f3bc JARVIS 5.0 - PHASE 1: SCHEDULER DIAGNOSTIC")
    print("=" * 60)

    # 1. Start Scheduler
    print("\u25b6\ufe0f Starting Priority Scheduler...")
    await priority_scheduler.start()

    # 2. Register with Watchdog (Simulate boot manager)
    print("\ud83d\udc36 Registering with Watchdog...")
    watchdog_system.register_component("priority_scheduler", heartbeat_interval=2.0)
    watchdog_system.start()

    # 3. Schedule Background Tasks (Indexation)
    async def index_files():
        print("[\u2699\ufe0f] BACKGROUND: Indexing files (running...)")
        await asyncio.sleep(5)
        print("[\u2705] BACKGROUND: Indexing complete")

    print("\u23f3 Scheduling BACKGROUND task...")
    priority_scheduler.schedule_task(
        "file_indexing", index_files, priority=TaskPriority.LOW
    )

    # 4. Wait for background task to start
    await asyncio.sleep(0.5)

    # 5. Schedule CRITICAL Task (Voice processing) to trigger PREEMPTION
    # We will temporarily lower max_concurrent_tasks to force preemption
    priority_scheduler.max_concurrent_tasks = 1

    async def process_voice():
        print("[\ud83d\udd25] CRITICAL: Processing user voice (URGENT!)")
        await asyncio.sleep(2)
        print("[\ud83d\udd25] CRITICAL: Voice processed")

    print("\ud83d\udea8 Scheduling CRITICAL task (should trigger preemption)...")
    priority_scheduler.schedule_task(
        "voice_processing", process_voice, priority=TaskPriority.CRITICAL
    )

    # 6. Monitor
    start_time = time.time()
    while time.time() - start_time < 10:
        metrics = priority_scheduler.get_scheduler_metrics()
        running = metrics["scheduler"]["running_tasks"]
        load = metrics["system_load"]["overall_load"]
        print(f"   Scheduler Status: Running={running} | Load={load:.2f}")

        # Check if watchdog is seeing heartbeats
        with watchdog_system._lock:
            status = watchdog_system._components.get("priority_scheduler").status.value
            print(f"   Watchdog Status: {status}")

        await asyncio.sleep(2)

    # 7. Stop everything
    print("\n\u23f1\ufe0f Stopping diagnostics...")
    await priority_scheduler.stop()
    watchdog_system.stop()
    print("\u2705 Diagnostic completed")


if __name__ == "__main__":
    asyncio.run(test_priority_scheduler())
