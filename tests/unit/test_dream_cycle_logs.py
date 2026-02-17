import json
import asyncio
from pathlib import Path
from unittest.mock import patch

from src.learning.dream_cycle import DreamCycle


def test_analyze_error_logs_creates_insights_and_tasks(tmp_path):
    data_dir = tmp_path / "dream_data"
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(parents=True)

    # Create sample log with ERROR and Exception lines
    log_file = logs_dir / "app.log"
    log_content = """
2026-02-17 12:00:00 INFO Starting system
2026-02-17 12:01:00 ERROR Traceback (most recent call last):
  File \"src/core/intelligence/local_brain.py\", line 45, in infer
    raise ModelInferenceError('CUDA out of memory')
ModelInferenceError: CUDA out of memory

2026-02-17 12:02:00 ERROR ModuleNotFoundError: No module named 'nonexistent_pkg'
"""
    log_file.write_text(log_content, encoding="utf-8")

    dc = DreamCycle(data_dir=data_dir)

    created = dc._analyze_error_logs(max_files=4, tail_lines=200)

    # insights file should be created
    insights_file = data_dir / "learning" / "insights.jsonl"
    assert insights_file.exists()

    lines = insights_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 2

    # At least one training task should be queued (for model-related error)
    queue_status = dc.training_queue.get_queue_status()
    assert queue_status["total_tasks"] >= 1


def test_generate_synthetic_data_queues_task(tmp_path):
    data_dir = tmp_path / "dream_data2"
    dc = DreamCycle(data_dir=data_dir)

    # Patch ai_agent._call_ollama_async to return JSON-like string
    async def fake_ollama(*args, **kwargs):
        return '{"chosen": "Good answer", "rejected": "Bad answer"}'

    with patch("src.core.intelligence.ai_agent.ai_agent._call_ollama_async", new=fake_ollama):
        dc._generate_synthetic_data("unit_topic", context="docs", teacher_model="gemma2:2b")

    # After generation, a dataset file should exist and a training task queued
    ds_dir = data_dir / "training_datasets" / "autonomous"
    files = list(ds_dir.glob("*.jsonl"))
    assert len(files) >= 1

    queue_status = dc.training_queue.get_queue_status()
    assert queue_status["total_tasks"] >= 1