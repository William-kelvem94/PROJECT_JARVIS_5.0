#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Boot Diagnostics (ASCII-safe)
"""
import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

import logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")

TIMEOUT = 20

def run_with_timeout(fn, timeout=TIMEOUT):
    result = {"ok": False, "error": None, "value": None}
    def _run():
        try:
            result["value"] = fn()
            result["ok"] = True
        except Exception as e:
            result["error"] = repr(e)
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False, f"TIMEOUT after {timeout}s"
    if result["ok"]:
        return True, result["value"]
    return False, result["error"]

results = []

def test(name, fn, timeout=TIMEOUT):
    print(f"  [{name}]...", end="", flush=True)
    ok, val = run_with_timeout(fn, timeout)
    status = "PASS" if ok else ("TIMEOUT" if "TIMEOUT" in str(val) else "FAIL")
    print(f" {status}" + (f" -- {val}" if not ok else ""))
    results.append((name, ok, val if not ok else None))
    return ok

print("\n" + "="*60)
print("JARVIS 5.0 - BOOT DIAGNOSTICS")
print("="*60)

# 1. Basic imports
print("\n[1] Basic Imports")
test("system_manifest", lambda: __import__("src.core.config.system_manifest", fromlist=["system_manifest"]))
test("async_event_bus", lambda: __import__("src.core.infrastructure.async_event_bus", fromlist=["AsyncEventBus"]))
test("boot_manager_module", lambda: __import__("src.core.infrastructure.boot_manager", fromlist=["BootManager"]))
test("bootstrapper", lambda: __import__("src.core.infrastructure.bootstrapper", fromlist=["SystemBootstrapper"]))
test("priority_scheduler", lambda: __import__("src.core.infrastructure.priority_scheduler", fromlist=["PriorityScheduler"]))

# 2. Event Bus
print("\n[2] Event Bus")
import asyncio
from src.core.infrastructure.async_event_bus import AsyncEventBus, EventType

def test_event_bus():
    bus = AsyncEventBus(enable_persistence=False)
    sid = bus.subscribe(EventType.WAKE_WORD, lambda e: None)
    assert sid is not None, "subscribe returned None"
    async def _run():
        await bus.start()
        await asyncio.sleep(0.1)
        await bus.stop()
    asyncio.run(_run())
    return "OK"

test("event_bus_lifecycle", test_event_bus)

# 3. Qt
print("\n[3] Qt Interface")
def test_qt():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return "QApplication OK"

qt_ok = test("PyQt6", test_qt)

def test_ui_signals():
    from src.interface.ui_signals import ui_signals
    return type(ui_signals).__name__

if qt_ok:
    test("ui_signals", test_ui_signals)

# 4. Audio
print("\n[4] Audio System")
def test_audio_import():
    from src.core.audio.enhanced_audio import get_audio_system
    return "import OK"

def test_audio_init():
    from src.core.audio.enhanced_audio import get_audio_system
    from pathlib import Path
    audio = get_audio_system(Path("data"))
    return type(audio).__name__

test("audio_import", test_audio_import)
test("audio_init", test_audio_init, timeout=40)

# 5. Vision
print("\n[5] Vision System")
def test_vision_import():
    from src.core.vision.vision_system import get_vision_system
    return "import OK"

def test_vision_init():
    from src.core.vision.vision_system import get_vision_system
    from pathlib import Path
    v = get_vision_system(Path("data"))
    return type(v).__name__

test("vision_import", test_vision_import)
test("vision_init", test_vision_init, timeout=40)

# 6. AI Agent
print("\n[6] AI Agent")
def test_ai():
    from src.core.intelligence.ai_agent import ai_agent
    return type(ai_agent).__name__

test("ai_agent", test_ai, timeout=45)

# 7. System Integrator
print("\n[7] System Integrator")
def test_integrator():
    from src.core.actions.system_integrator import get_system_integrator
    return type(get_system_integrator()).__name__

test("system_integrator", test_integrator)

# 8. Full headless boot
print("\n[8] Full Headless Boot")
def test_full_boot():
    import asyncio
    # Reset BootManager singleton for clean test
    from src.core.infrastructure import boot_manager as bm_mod
    bm_mod.BootManager._instance = None

    from src.core.infrastructure.bootstrapper import SystemBootstrapper
    bs = SystemBootstrapper(app_instance=None)
    result = {}
    async def _boot():
        result["instances"] = await bs.bootstrap()
    asyncio.run(_boot())
    return list(result.get("instances", {}).keys())

test("full_headless_boot", test_full_boot, timeout=120)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
passed = [r for r in results if r[1]]
failed = [r for r in results if not r[1]]
print(f"  PASSED: {len(passed)}/{len(results)}")
print(f"  FAILED: {len(failed)}/{len(results)}")
if failed:
    print("\nFailures:")
    for name, ok, err in failed:
        print(f"  FAIL [{name}]: {err}")

sys.exit(0 if not failed else 1)
