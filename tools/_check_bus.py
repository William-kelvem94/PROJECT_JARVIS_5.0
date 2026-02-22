import sys
import os
sys.path.insert(0, os.getcwd())
import asyncio
try:
    print("Importing AsyncEventBus...")
    from src.core.infrastructure.async_event_bus import AsyncEventBus, get_event_bus
    print("Initializing Bus...")
    bus = AsyncEventBus()
    print("Bus initialized. Starting...")
    async def run():
        await bus.start()
        print("Bus started.")
        await bus.stop()
        print("Bus stopped.")
    
    asyncio.run(run())
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
