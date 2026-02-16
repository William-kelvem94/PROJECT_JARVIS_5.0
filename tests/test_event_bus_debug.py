#!/usr/bin/env python3
import asyncio
import sys
import traceback
import os

# Add project root to path so we can import src modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

async def test_event_bus_connections():
    """Test Event Bus connections with detailed error reporting"""
    print("Testing Event Bus connections...")

    try:
        from src.core.infrastructure.async_event_bus import AsyncEventBus
        event_bus = AsyncEventBus()
        print("✅ Event Bus created successfully")

        # Test memory_manager connection
        print("\n--- Testing memory_manager ---")
        try:
            # Import directly to avoid heavy dependencies
            from src.core.intelligence.memory.unified_manager import UnifiedMemoryManager
            memory_manager = UnifiedMemoryManager()
            print(f"memory_manager type: {type(memory_manager)}")
            print(f"memory_manager is None: {memory_manager is None}")
            if memory_manager:
                print(f"Has connect_event_bus: {hasattr(memory_manager, 'connect_event_bus')}")
                if hasattr(memory_manager, 'connect_event_bus'):
                    memory_manager.connect_event_bus(event_bus)
                    print("✅ Memory Manager connected successfully")
                else:
                    print("❌ Memory Manager missing connect_event_bus method")
            else:
                print("❌ Memory Manager is None")
        except Exception as e:
            print(f"❌ Memory Manager connection failed: {e}")
            import traceback
            traceback.print_exc()

        # Test ai_agent connection - SKIP due to heavy dependencies
        print("\n--- Skipping ai_agent (heavy dependencies) ---")

        # Test proactive_monitor connection
        print("\n--- Testing proactive_monitor ---")
        try:
            # Import directly to avoid heavy dependencies
            from src.core.intelligence.proactive_monitor import ProactiveMonitor
            proactive_monitor = ProactiveMonitor()
            print(f"proactive_monitor type: {type(proactive_monitor)}")
            print(f"proactive_monitor is None: {proactive_monitor is None}")
            if proactive_monitor:
                print(f"Has connect_event_bus: {hasattr(proactive_monitor, 'connect_event_bus')}")
                if hasattr(proactive_monitor, 'connect_event_bus'):
                    proactive_monitor.connect_event_bus(event_bus)
                    print("✅ Proactive Monitor connected to event bus")
                    # This is the line that might fail
                    if hasattr(proactive_monitor, 'event_bus') and proactive_monitor.event_bus:
                        try:
                            proactive_monitor.event_bus.loop = asyncio.get_running_loop()
                            print("✅ Proactive Monitor loop set successfully")
                        except Exception as e:
                            print(f"❌ Setting proactive_monitor loop failed: {e}")
                            print(f"proactive_monitor.event_bus type: {type(proactive_monitor.event_bus)}")
                            print(f"proactive_monitor.event_bus value: {repr(proactive_monitor.event_bus)}")
                            traceback.print_exc()
                    else:
                        print("❌ Proactive Monitor event_bus not set after connection")
                else:
                    print("❌ Proactive Monitor missing connect_event_bus method")
            else:
                print("❌ Proactive Monitor is None")
        except Exception as e:
            print(f"❌ Proactive Monitor connection failed: {e}")
            traceback.print_exc()

        print("\n✅ All Event Bus connections completed")

    except Exception as e:
        print(f"❌ Event Bus creation failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_event_bus_connections())