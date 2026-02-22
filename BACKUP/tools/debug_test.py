#!/usr/bin/env python3
"""
JARVIS Debug Test Script
Tests all critical modules and reports errors
"""
import sys
import os
import traceback
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

errors = []
warnings = []
successes = []

def test(name, fn):
    try:
        result = fn()
        successes.append(f"✅ {name}")
        return result
    except Exception as e:
        errors.append(f"❌ {name}: {e}")
        traceback.print_exc()
        return None

print("=" * 60)
print("JARVIS 5.0 - DEBUG DIAGNOSTICS")
print("=" * 60)

# Test 1: Core imports
print("\n[1] Testing Core Imports...")
test("async_event_bus", lambda: __import__('src.core.infrastructure.async_event_bus', fromlist=['AsyncEventBus']))
test("boot_manager", lambda: __import__('src.core.infrastructure.boot_manager', fromlist=['BootManager']))
test("bootstrapper", lambda: __import__('src.core.infrastructure.bootstrapper', fromlist=['SystemBootstrapper']))
test("priority_scheduler", lambda: __import__('src.core.infrastructure.priority_scheduler', fromlist=['PriorityScheduler']))
test("system_manifest", lambda: __import__('src.core.config.system_manifest', fromlist=['system_manifest']))
test("blackbox_logger", lambda: __import__('src.core.config.blackbox_logger', fromlist=['blackbox_logger']))

# Test 2: Event Bus
print("\n[2] Testing Event Bus...")
async def test_event_bus():
    from src.core.infrastructure.async_event_bus import AsyncEventBus, EventType
    bus = AsyncEventBus(enable_persistence=False)
    await bus.start()
    
    # Test subscribe
    sub_id = bus.subscribe(EventType.WAKE_WORD, lambda e: None)
    assert sub_id is not None, "Subscribe returned None"
    
    # Test publish
    event_id = bus.publish(EventType.WAKE_WORD, {"test": True})
    assert event_id is not None, "Publish returned None"
    
    await bus.stop()
    return True

try:
    result = asyncio.run(test_event_bus())
    successes.append("✅ Event Bus (subscribe + publish)")
except Exception as e:
    errors.append(f"❌ Event Bus: {e}")
    traceback.print_exc()

# Test 3: Memory Manager
print("\n[3] Testing Memory Manager...")
def test_memory():
    from src.core.intelligence.memory.unified_manager import UnifiedMemoryManager
    # Reset singleton for clean test
    UnifiedMemoryManager._instance = None
    mgr = UnifiedMemoryManager()
    stats = mgr.get_stats()
    return stats

test("UnifiedMemoryManager", test_memory)

# Test 4: AI Agent
print("\n[4] Testing AI Agent...")
test("ai_agent import", lambda: __import__('src.core.intelligence.ai_agent', fromlist=['AIAgent']))

# Test 5: Audio System
print("\n[5] Testing Audio System...")
test("enhanced_audio import", lambda: __import__('src.core.audio.enhanced_audio', fromlist=['EnhancedAudioSystem']))
test("voice_controller import", lambda: __import__('src.core.audio.voice_controller', fromlist=['VoiceController']))

# Test 6: Vision System
print("\n[6] Testing Vision System...")
test("vision_system import", lambda: __import__('src.core.vision.vision_system', fromlist=['VisionSystem']))

# Test 7: Learning Engine
print("\n[7] Testing Learning Engine...")
test("learning_engine import", lambda: __import__('src.learning.learning_engine', fromlist=['LearningEngine']))

# Test 8: Utils
print("\n[8] Testing Utils...")
test("config import", lambda: __import__('src.utils.config', fromlist=['config']))
test("env_manager import", lambda: __import__('src.utils.env_manager', fromlist=['get_config']))

# Test 9: Interface
print("\n[9] Testing Interface...")
test("ui_signals import", lambda: __import__('src.interface.ui_signals', fromlist=['ui_signals']))

# Test 10: Security
print("\n[10] Testing Security...")
test("security_manager import", lambda: __import__('src.core.security.security_manager_advanced', fromlist=['SecurityManager']))

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"\n✅ PASSED: {len(successes)}")
for s in successes:
    print(f"  {s}")

print(f"\n❌ FAILED: {len(errors)}")
for e in errors:
    print(f"  {e}")

print(f"\n⚠️  WARNINGS: {len(warnings)}")
for w in warnings:
    print(f"  {w}")

print("\n" + "=" * 60)
sys.exit(0 if not errors else 1)
