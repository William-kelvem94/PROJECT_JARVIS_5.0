# -*- coding: utf-8 -*-
"""
Integration Test: Learning Engine + Config Schema
=================================================
Validates the full Phase 1 & 2 refactoring pipeline.

Run from project root:
    python tools/test_learning_integration.py
"""

import sys
import os
import time
import traceback

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []

def test(name: str, fn):
    """Run a single test and record result."""
    try:
        fn()
        results.append((PASS, name))
        print(f"  {PASS} {name}")
    except Exception as e:
        results.append((FAIL, name, str(e)))
        print(f"  {FAIL} {name}")
        print(f"      → {e}")


print("\n" + "=" * 60)
print("  JARVIS 5.0 - Learning System Integration Tests")
print("=" * 60)

# ── 1. Config Schema ──────────────────────────────────────────
print("\n[1] Config Schema")

def test_config_defaults():
    from src.learning.config_schema import LearningConfig
    cfg = LearningConfig()
    assert cfg.general.enabled is True
    assert cfg.dream_cycle.enabled is True
    assert cfg.dream_cycle.idle_conditions.max_cpu_percent == 20.0
    assert cfg.training.model_tier == "pro"
    assert cfg.database.backend == "sqlite"

def test_config_from_dict():
    from src.learning.config_schema import LearningConfig
    data = {
        "general": {"enabled": False, "log_level": "DEBUG"},
        "dream_cycle": {
            "enabled": True,
            "idle_conditions": {"max_cpu_percent": 35.0, "night_start_hour": 23},
            "max_research_topics_per_cycle": 5
        },
        "training": {"model_tier": "ultra", "batch_size": 8}
    }
    cfg = LearningConfig.from_dict(data)
    assert cfg.general.enabled is False
    assert cfg.general.log_level == "DEBUG"
    assert cfg.dream_cycle.idle_conditions.max_cpu_percent == 35.0
    assert cfg.dream_cycle.idle_conditions.night_start_hour == 23
    assert cfg.dream_cycle.max_research_topics_per_cycle == 5
    assert cfg.training.model_tier == "ultra"
    assert cfg.training.batch_size == 8
    # Defaults preserved for unspecified fields
    assert cfg.database.backend == "sqlite"

def test_config_from_yaml():
    from src.learning.config_schema import LearningConfig
    import yaml
    yaml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "ai_config.yaml")
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"ai_config.yaml not found at {yaml_path}")
    with open(yaml_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    section = raw.get("continual_learning", {})
    assert section, "continual_learning section missing from ai_config.yaml"
    cfg = LearningConfig.from_dict(section)
    assert cfg.dream_cycle.idle_conditions.max_cpu_percent == 20.0
    assert cfg.training.model_tier == "pro"

test("Config defaults are correct", test_config_defaults)
test("Config.from_dict() works with partial data", test_config_from_dict)
test("Config loads from ai_config.yaml", test_config_from_yaml)

# ── 2. safe_execute Decorator ─────────────────────────────────
print("\n[2] safe_execute Decorator")

def test_safe_execute_normal():
    from src.utils.safe_execute import safe_execute
    @safe_execute(default=-1)
    def good():
        return 42
    assert good() == 42

def test_safe_execute_on_error():
    from src.utils.safe_execute import safe_execute
    @safe_execute(default="fallback", log_error=False)
    def bad():
        raise ValueError("boom")
    assert bad() == "fallback"

def test_safe_context():
    from src.utils.safe_execute import safe_context
    with safe_context("test_op", log_error=False):
        x = 1 + 1
    assert x == 2

def test_safe_import():
    from src.utils.safe_execute import safe_import
    mod = safe_import("json")
    assert mod is not None
    missing = safe_import("nonexistent_module_xyz", fallback="MISSING", log=False)
    assert missing == "MISSING"

test("@safe_execute returns value on success", test_safe_execute_normal)
test("@safe_execute returns default on error", test_safe_execute_on_error)
test("safe_context() works correctly", test_safe_context)
test("safe_import() handles missing modules", test_safe_import)

# ── 3. IdleDetector ───────────────────────────────────────────
print("\n[3] IdleDetector")

def test_idle_detector_imports():
    from src.learning.idle_detector import IdleDetector
    from src.learning.config_schema import IdleConditions
    cond = IdleConditions(max_cpu_percent=99.0, min_idle_duration_seconds=1)
    det = IdleDetector(cond)
    assert det.conditions.max_cpu_percent == 99.0

def test_idle_detector_night_check():
    from src.learning.idle_detector import IdleDetector
    from src.learning.config_schema import IdleConditions
    # Force night window to cover all hours
    cond = IdleConditions(night_start_hour=0, night_end_hour=23)
    det = IdleDetector(cond)
    # Should be night time (0:00 to 23:00 covers almost everything)
    result = det._is_night_time()
    assert isinstance(result, bool)

def test_idle_detector_stats():
    from src.learning.idle_detector import IdleDetector
    from src.learning.config_schema import IdleConditions
    det = IdleDetector(IdleConditions())
    stats = det.get_system_stats()
    assert isinstance(stats, dict)
    assert "timestamp" in stats

test("IdleDetector uses IdleConditions from config_schema", test_idle_detector_imports)
test("IdleDetector._is_night_time() returns bool", test_idle_detector_night_check)
test("IdleDetector.get_system_stats() returns dict", test_idle_detector_stats)

# ── 4. TrainingScheduler ──────────────────────────────────────
print("\n[4] TrainingScheduler")

def test_training_queue_add():
    from src.learning.training_scheduler import TrainingQueue, TrainingTask
    from pathlib import Path
    q = TrainingQueue(max_size=5)
    task = TrainingTask(task_id="t1", dataset_path=Path("data/test.jsonl"), model_name="jarvis-v1", priority=8)
    ok = q.add_task(task)
    assert ok is True
    assert len(q.tasks) == 1

def test_training_queue_priority():
    from src.learning.training_scheduler import TrainingQueue, TrainingTask
    from pathlib import Path
    q = TrainingQueue()
    q.add_task(TrainingTask("low",  Path("a"), "m", priority=2))
    q.add_task(TrainingTask("high", Path("b"), "m", priority=9))
    q.add_task(TrainingTask("mid",  Path("c"), "m", priority=5))
    # Highest priority should be first
    assert q.tasks[0].task_id == "high"

def test_training_scheduler_schedule():
    from src.learning.training_scheduler import TrainingScheduler
    sched = TrainingScheduler()
    ok = sched.schedule_training({
        "dataset_path": "data/test.jsonl",
        "model_name": "jarvis-v1",
        "priority": 7
    })
    assert ok is True
    status = sched.get_queue_status()
    assert status["total_tasks"] == 1

test("TrainingQueue.add_task() works", test_training_queue_add)
test("TrainingQueue respects priority ordering", test_training_queue_priority)
test("TrainingScheduler.schedule_training() enqueues task", test_training_scheduler_schedule)

# ── 5. HealthMonitor ──────────────────────────────────────────
print("\n[5] HealthMonitor")

def test_health_monitor_register():
    from src.learning.health_monitor import HealthMonitor
    hm = HealthMonitor(check_interval=999)
    hm.register_component("db")
    hm.register_component("trainer")
    assert "db" in hm._components
    assert "trainer" in hm._components

def test_health_monitor_mark():
    from src.learning.health_monitor import HealthMonitor
    hm = HealthMonitor(check_interval=999)
    hm.register_component("db")
    hm.mark_unhealthy("db", "Connection refused")
    assert hm._components["db"].healthy is False
    hm.mark_healthy("db")
    assert hm._components["db"].healthy is True

def test_health_monitor_report():
    from src.learning.health_monitor import HealthMonitor
    hm = HealthMonitor(check_interval=999)
    hm.register_component("a")
    hm.register_component("b")
    hm.mark_unhealthy("b", "timeout")
    report = hm.run_health_check()
    assert report.total_score == 0.5
    assert not report.overall_healthy

test("HealthMonitor.register_component() works", test_health_monitor_register)
test("HealthMonitor mark_healthy/unhealthy works", test_health_monitor_mark)
test("HealthMonitor.run_health_check() calculates score", test_health_monitor_report)

# ── 6. TrainingOrchestrator ───────────────────────────────────
print("\n[6] TrainingOrchestrator")

def test_orchestrator_create_job():
    from src.learning.training_orchestrator import TrainingOrchestrator
    orch = TrainingOrchestrator()
    job_id = orch.create_job(model_config={"name": "test"}, dataset_path="data/test.jsonl")
    assert job_id is not None
    assert job_id.startswith("train_")

def test_orchestrator_list_jobs():
    from src.learning.training_orchestrator import TrainingOrchestrator
    orch = TrainingOrchestrator()
    orch.create_job(model_config={}, dataset_path="data/a.jsonl")
    orch.create_job(model_config={}, dataset_path="data/b.jsonl")
    jobs = orch.list_jobs()
    assert len(jobs) == 2

def test_orchestrator_cancel_job():
    from src.learning.training_orchestrator import TrainingOrchestrator
    orch = TrainingOrchestrator()
    job_id = orch.create_job(model_config={}, dataset_path="data/test.jsonl")
    ok = orch.cancel_job(job_id)
    assert ok is True
    status = orch.get_job_status(job_id)
    assert status["status"] == "cancelled"

test("TrainingOrchestrator.create_job() returns job_id", test_orchestrator_create_job)
test("TrainingOrchestrator.list_jobs() returns all jobs", test_orchestrator_list_jobs)
test("TrainingOrchestrator.cancel_job() works", test_orchestrator_cancel_job)

# ── 7. ModelRegistryManager ───────────────────────────────────
print("\n[7] ModelRegistryManager")

def test_model_registry_no_backend():
    from src.learning.model_registry_manager import ModelRegistryManager
    mgr = ModelRegistryManager()
    # Without a registry backend, should return safe defaults
    models = mgr.list_models()
    assert models == []
    deployed = mgr.list_deployed_models()
    assert deployed == []

def test_model_registry_manage_models():
    from src.learning.model_registry_manager import ModelRegistryManager
    mgr = ModelRegistryManager()
    summary = mgr.manage_models()
    assert "total_models" in summary
    assert "timestamp" in summary

test("ModelRegistryManager works without backend", test_model_registry_no_backend)
test("ModelRegistryManager.manage_models() returns summary", test_model_registry_manage_models)

# ── 8. DreamCycle ─────────────────────────────────────────────
print("\n[8] DreamCycle (disabled mode)")

def test_dream_cycle_disabled():
    from src.learning.dream_cycle import DreamCycle
    from src.learning.config_schema import DreamCycleConfig
    cfg = DreamCycleConfig(enabled=False)
    dc = DreamCycle(data_dir="data", config=cfg)
    started = dc.start()
    assert started is False
    assert dc.is_running is False

def test_dream_cycle_status():
    from src.learning.dream_cycle import DreamCycle
    from src.learning.config_schema import DreamCycleConfig
    cfg = DreamCycleConfig(enabled=False)
    dc = DreamCycle(data_dir="data", config=cfg)
    status = dc.get_status()
    assert "enabled" in status
    assert "is_running" in status
    assert "queue_status" in status

test("DreamCycle respects enabled=False", test_dream_cycle_disabled)
test("DreamCycle.get_status() returns full dict", test_dream_cycle_status)

# ── Summary ───────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
total  = len(results)

print(f"  Results: {passed}/{total} passed  |  {failed} failed")

if failed:
    print("\n  Failed tests:")
    for r in results:
        if r[0] == FAIL:
            print(f"    {FAIL} {r[1]}: {r[2] if len(r) > 2 else ''}")
    sys.exit(1)
else:
    print("\n  🎉 All tests passed! Refactoring is complete and verified.")
    sys.exit(0)
