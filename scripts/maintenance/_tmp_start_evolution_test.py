import asyncio
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.evolution import evolution_manager

async def main():
    await evolution_manager.start(observer_interval=60, auto_heal=True, initial_scan=True, enable_module_generation=False, enable_voice_commands=False)
    print('STATUS AFTER START:', evolution_manager.get_status())
    # keep running for a short time to let background tasks initialize
    await asyncio.sleep(6)
    print('STATUS BEFORE STOP:', evolution_manager.get_status())
    await evolution_manager.stop()
    print('STATUS AFTER STOP:', evolution_manager.get_status())

if __name__ == '__main__':
    asyncio.run(main())
