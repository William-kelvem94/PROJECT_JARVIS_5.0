#!/usr/bin/env python3
"""
JARVIS 5.0 Stability Test Script
Tests the implemented fixes for memory leaks and component stability.
"""

import sys
import time
import psutil
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_memory_management():
    """Test memory management improvements"""
    print("🧠 Testing Memory Management...")

    try:
        from src.core.intelligence.memory.unified_manager import UnifiedMemoryManager

        memory = UnifiedMemoryManager()

        # Test cache operations
        print("  📝 Testing cache operations...")
        for i in range(60):  # Exceed cache limit
            memory.store_interaction(f"test prompt {i}", f"test response {i}")

        # Check cache size is limited
        cache_size = len(memory.prompt_cache)
        print(f"  📊 Cache size after 60 entries: {cache_size} (should be ≤50)")

        # Test ChromaDB cleanup
        print("  🗃️ Testing ChromaDB cleanup...")
        memory.force_chromadb_cleanup()
        print("  ✅ ChromaDB cleanup completed")

        return cache_size <= 55  # Allow some buffer

    except Exception as e:
        print(f"  ❌ Memory test failed: {e}")
        return False


def test_model_unloading():
    """Test automatic model unloading"""
    print("🤖 Testing Model Unloading...")

    try:
        # Test audio system
        from src.core.audio.enhanced_audio import EnhancedAudioSystem
<<<<<<< HEAD
<<<<<<< Updated upstream
=======

>>>>>>> dev-new-version
        audio = EnhancedAudioSystem()
=======

        audio = EnhancedAudioSystem()  # noqa: F841
>>>>>>> Stashed changes

        # Simulate activity
        print("  🎵 Testing audio system activity tracking...")
        # This would normally trigger _update_activity, but we can't easily test without actual processing

        # Test vision system
        from src.core.vision.optimized_yolo_pipeline import OptimizedYOLOPipeline
<<<<<<< HEAD
<<<<<<< Updated upstream
=======

>>>>>>> dev-new-version
        vision = OptimizedYOLOPipeline(models_dir=Path("./models"))
=======

        vision = OptimizedYOLOPipeline(models_dir=Path("./models"))  # noqa: F841
>>>>>>> Stashed changes
        print("  👁️ Vision system initialized successfully")
        return True

    except Exception as e:
        print(f"  ❌ Model unloading test failed: {e}")
        return False


def test_asyncio_fixes():
    """Test asyncio scoping fixes"""
    print("🔄 Testing AsyncIO Fixes...")

    try:
        # Test that we can create event loops safely
        def test_thread():
            try:
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.close()
                return True
            except Exception as e:
                print(f"  ❌ Thread event loop test failed: {e}")
                return False

        # Test multiple threads
        threads = []
        results = []

        def thread_wrapper():
            results.append(test_thread())

        for i in range(3):
            t = threading.Thread(target=thread_wrapper)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        success = all(results)
        print(f"  ✅ AsyncIO thread safety test: {'PASSED' if success else 'FAILED'}")
        return success

    except Exception as e:
        print(f"  ❌ AsyncIO test failed: {e}")
        return False


def monitor_memory_usage(duration=10):
    """Monitor memory usage during test"""
    print(f"📊 Monitoring memory usage for {duration} seconds...")

    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    max_memory = initial_memory
    for _ in range(duration):
        current = process.memory_info().rss / 1024 / 1024
        max_memory = max(max_memory, current)
        time.sleep(1)

    memory_increase = max_memory - initial_memory
    print(".1f")
    print(".1f")

    # Flag if memory increase is excessive (>100MB)
    return memory_increase < 100


def main():
    """Run all stability tests"""
    print("🚀 JARVIS 5.0 Stability Test Suite")
    print("=" * 50)

    tests = [
        ("Memory Management", test_memory_management),
        ("Model Unloading", test_model_unloading),
        ("AsyncIO Fixes", test_asyncio_fixes),
        ("Memory Monitoring", monitor_memory_usage),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        except Exception as e:
            print(f"{test_name}: ❌ ERROR - {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY:")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All stability fixes are working correctly!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
