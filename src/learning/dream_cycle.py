"""
Dream Cycle for JARVIS AGI Machine Learning Core.

This module implements autonomous nighttime training through idle detection,
data consolidation, and automatic training scheduling. Runs in background
with resource management.
"""

import json
import logging
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict

from src.learning.gap_analyzer import KnowledgeGapAnalyzer

try:
    import schedule

    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


@dataclass
class IdleConditions:
    """Conditions for determining system idle state (relaxed for run-at-limit)."""

    # Set permissive defaults so DreamCycle can run even under heavy load
    max_cpu_percent: float = 100.0
    max_memory_percent: float = 100.0
    min_idle_duration_seconds: int = 0  # immediate eligibility
    night_start_hour: int = 22  # 10 PM
    night_end_hour: int = 6  # 6 AM
    check_interval_seconds: int = 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TrainingTask:
    """Represents a training task in the queue."""

    task_id: str
    dataset_path: Path
    model_name: str
    priority: int = 5  # 1-10, higher is more important
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, running, completed, failed
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["dataset_path"] = str(self.dataset_path)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingTask":
        """Create from dictionary."""
        data = data.copy()
        data["dataset_path"] = Path(data["dataset_path"])
        return cls(**data)


@dataclass
class DreamCycleStats:
    """Statistics for dream cycle operations."""

    total_cycles: int = 0
    successful_trainings: int = 0
    failed_trainings: int = 0
    total_training_time_seconds: float = 0.0
    last_cycle_start: Optional[str] = None
    last_cycle_end: Optional[str] = None
    tasks_completed: int = 0
    tasks_pending: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SystemMonitor:
    """Monitors system resources to determine idle state."""

    def __init__(self, conditions: IdleConditions):
        """
        Initialize system monitor.

        Args:
            conditions: Idle conditions to check
        """
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, using time-based idle detection only")

        self.conditions = conditions
        self.idle_start_time: Optional[float] = None
        self.last_check_time: Optional[float] = None

    def is_system_idle(self) -> bool:
        """
        Check if system is idle based on conditions.

        Returns:
            True if system is idle
        """
        current_time = time.time()

        # Check time of day (night hours)
        if not self._is_night_time():
            if self.idle_start_time is not None:
                logger.debug("Not night time, resetting idle timer")
                self.idle_start_time = None
            return False

        # Check system resources if psutil available
        if PSUTIL_AVAILABLE:
            if not self._check_resource_idle():
                if self.idle_start_time is not None:
                    logger.debug("System not resource-idle, resetting idle timer")
                    self.idle_start_time = None
                return False

        # Track idle duration
        if self.idle_start_time is None:
            self.idle_start_time = current_time
            logger.debug("System became idle")
            return False  # Need to wait for minimum duration

        idle_duration = current_time - self.idle_start_time

        if idle_duration >= self.conditions.min_idle_duration_seconds:
            logger.debug(
                f"System idle for {idle_duration:.0f}s (threshold: {self.conditions.min_idle_duration_seconds}s)"
            )
            return True

        return False

    def _is_night_time(self) -> bool:
        """Check if current time is within night hours."""
        now = datetime.now()
        current_hour = now.hour

        start_hour = self.conditions.night_start_hour
        end_hour = self.conditions.night_end_hour

        # Handle overnight periods (e.g., 22:00 to 06:00)
        if start_hour > end_hour:
            return current_hour >= start_hour or current_hour < end_hour
        else:
            return start_hour <= current_hour < end_hour

    def _check_resource_idle(self) -> bool:
        """Check if system resources indicate idle state."""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1.0)
            if cpu_percent > self.conditions.max_cpu_percent:
                logger.debug(f"CPU usage too high: {cpu_percent:.1f}%")
                return False

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.conditions.max_memory_percent:
                logger.debug(f"Memory usage too high: {memory.percent:.1f}%")
                return False

            # Check disk I/O (optional)
            # Commented out to avoid false positives
            # disk_io = psutil.disk_io_counters()

            return True

        except Exception as e:
            logger.error(f"Error checking resource idle: {e}")
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        if not PSUTIL_AVAILABLE:
            return {"status": "psutil_not_available"}

        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1.0),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "is_night_time": self._is_night_time(),
                "is_idle": self.is_system_idle(),
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}


class TrainingQueue:
    """Queue for managing training tasks."""

    def __init__(self, max_size: int = 100):
        """
        Initialize training queue.

        Args:
            max_size: Maximum queue size
        """
        self.queue: List[TrainingTask] = []
        self.max_size = max_size
        self.lock = threading.Lock()

    def add_task(self, task: TrainingTask) -> bool:
        """
        Add a task to the queue.

        Args:
            task: Training task to add

        Returns:
            True if task was added successfully
        """
        with self.lock:
            if len(self.queue) >= self.max_size:
                logger.warning(
                    f"Queue is full ({self.max_size} tasks), cannot add task"
                )
                return False

            self.queue.append(task)
            # Sort by priority (higher first) and creation time
            self.queue.sort(key=lambda t: (-t.priority, t.created_at))

            logger.info(f"Added task {task.task_id} (priority: {task.priority})")
            return True

    def get_next_task(self) -> Optional[TrainingTask]:
        """
        Get the next task from the queue.

        Returns:
            Next task or None if queue is empty
        """
        with self.lock:
            # Get pending tasks
            pending_tasks = [t for t in self.queue if t.status == "pending"]

            if not pending_tasks:
                return None

            # Return highest priority task
            task = pending_tasks[0]
            task.status = "running"
            return task

    def mark_completed(self, task_id: str, success: bool = True) -> None:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task
            success: Whether the task completed successfully
        """
        with self.lock:
            for task in self.queue:
                if task.task_id == task_id:
                    if success:
                        task.status = "completed"
                        logger.info(f"Task {task_id} completed successfully")
                    else:
                        task.retry_count += 1
                        if task.retry_count >= task.max_retries:
                            task.status = "failed"
                            logger.error(
                                f"Task {task_id} failed after {task.retry_count} retries"
                            )
                        else:
                            task.status = "pending"
                            logger.warning(
                                f"Task {task_id} failed, will retry ({task.retry_count}/{task.max_retries})"
                            )
                    break

    def remove_completed_tasks(self) -> int:
        """
        Remove completed tasks from the queue.

        Returns:
            Number of tasks removed
        """
        with self.lock:
            original_count = len(self.queue)
            self.queue = [
                t for t in self.queue if t.status not in ["completed", "failed"]
            ]
            removed_count = original_count - len(self.queue)

            if removed_count > 0:
                logger.info(f"Removed {removed_count} completed tasks from queue")

            return removed_count

    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of the queue."""
        with self.lock:
            status_counts = {}
            for task in self.queue:
                status_counts[task.status] = status_counts.get(task.status, 0) + 1

            return {
                "total_tasks": len(self.queue),
                "status_counts": status_counts,
                "tasks": [t.to_dict() for t in self.queue],
            }


class DreamCycle:
    """
    Dream Cycle - Autonomous nighttime training system.

    Monitors system idle state, consolidates training data,
    and runs training tasks during low-activity periods.
    """

    def __init__(
        self,
        data_dir: Path,
        idle_conditions: Optional[IdleConditions] = None,
        training_callback: Optional[Callable] = None,
    ):
        """
        Initialize the Dream Cycle.

        Args:
            data_dir: Directory for storing data and logs
            idle_conditions: Conditions for idle detection
            training_callback: Callback function for running training
                             Should accept (task: TrainingTask) -> bool
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.idle_conditions = idle_conditions or IdleConditions()
        self.system_monitor = SystemMonitor(self.idle_conditions)
        self.training_queue = TrainingQueue()

        self.training_callback = training_callback

        # State
        self.running = False
        self.in_training = False
        self.current_task: Optional[TrainingTask] = None

        # Statistics
        self.stats = DreamCycleStats()
        self._load_stats()

        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Gap Analyzer
        self.gap_analyzer = KnowledgeGapAnalyzer(self.data_dir)

        logger.info("DreamCycle initialized with Gap Analysis Support")

    def start(self) -> None:
        """Start the dream cycle in background thread."""
        if self.running:
            logger.warning("DreamCycle already running")
            return

        self.running = True
        self.stop_event.clear()

        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="DreamCycleMonitor"
        )
        self.monitor_thread.start()

        logger.info("DreamCycle started")

    def stop(self) -> None:
        """Stop the dream cycle."""
        if not self.running:
            logger.warning("DreamCycle not running")
            return

        logger.info("Stopping DreamCycle...")
        self.running = False
        self.stop_event.set()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=10.0)

        self._save_stats()
        logger.info("DreamCycle stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in background thread)."""
        logger.info("Monitor loop started")

        while not self.stop_event.is_set():
            try:
                # Check if system is idle
                is_idle = self.system_monitor.is_system_idle()

                if is_idle and not self.in_training:
                    logger.info("System idle detected, starting dream cycle")
                    self._run_dream_cycle()

                # Sleep before next check
                self.stop_event.wait(self.idle_conditions.check_interval_seconds)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}", exc_info=True)
                self.stop_event.wait(60)  # Wait a bit before retrying

        logger.info("Monitor loop ended")

    def _run_dream_cycle(self) -> None:
        """Run a dream cycle (process training queue)."""
        try:
            self.stats.total_cycles += 1
            self.stats.last_cycle_start = datetime.now().isoformat()

            logger.info(f"Starting dream cycle #{self.stats.total_cycles}")

            # Process tasks while system remains idle
            while self.system_monitor.is_system_idle() and not self.stop_event.is_set():
                # Get next task
                task = self.training_queue.get_next_task()

                if task is None:
                    logger.info("Queue empty. Initiating AUTONOMOUS SELF-IMPROVEMENT PHASE...")
                    
                    # 1. Code Doctor (Fix bugs)
                    try:
                        from src.core.evolution.code_doctor import code_doctor
                        code_doctor.heal_system()
                    except Exception as e:
                        logger.error(f"CodeDoctor failed: {e}")

                    # 2. Research (Fill knowledge gaps)
                    self._perform_autonomous_research()
                    break

                # Run training
                self.current_task = task
                self.in_training = True

                logger.info(f"Processing task: {task.task_id}")
                success = self._run_training_task(task)

                self.training_queue.mark_completed(task.task_id, success)

                if success:
                    self.stats.successful_trainings += 1
                    self.stats.tasks_completed += 1
                else:
                    self.stats.failed_trainings += 1

                self.in_training = False
                self.current_task = None

                # Clean up completed tasks periodically
                self.training_queue.remove_completed_tasks()

            self.stats.last_cycle_end = datetime.now().isoformat()
            self._save_stats()

            logger.info("Dream cycle completed")

        except Exception as e:
            logger.error(f"Error in dream cycle: {e}", exc_info=True)
            self.in_training = False

    def _perform_autonomous_research(self):
        """
        Scans for knowledge gaps and attempts to acquire new information
        from safe external sources (Hugging Face, Google, Official Docs).

        Also performs automated analysis of recent error logs and converts
        recurring failures into learning notes / training tasks.
        """
        from src.utils.logger_reflection import reflect_logger
        from src.utils.web_search_tool import web_search_tool

        reflect_logger.reflect(
            "Initiating SELF-EVOLUTION protocol...", layer="AGI-RESEARCH"
        )

        # First: analyze logs for actionable insights
        try:
            self._analyze_error_logs()
        except Exception:
            logger.debug("Log analysis failed during autonomous research", exc_info=True)

        gaps = self.gap_analyzer.analyze_gaps()
        if not gaps:
            reflect_logger.reflect(
                "âœ¨ Neural saturation complete. No gaps detected.",
                layer="AGI-RESEARCH",
            )
            return

        reflect_logger.reflect(
            f"Detected {len(gaps)} cognitive vacuums. Processing priority topics.",
            layer="AGI-RESEARCH",
        )

        for gap in gaps[:2]:  # Research top 2 gaps
            plan = self.gap_analyzer.generate_research_plan(gap)
            topic = plan["topic"]
            priority = gap["priority"]

            reflect_logger.reflect(
                f"ðŸ” TOPIC: {topic.upper()}\nPriority: {priority}/10",
                layer="RESEARCH-INIT",
            )

            # 1. HUB_DISCOVERY (Strict Source: Hugging Face)
            try:
                import requests

                reflect_logger.reflect(
                    f"Scanning Hugging Face Hub for verified datasets on '{topic}'...",
                    layer="HUB-DISCOVERY",
                )
                # Search specifically for datasets with high downloads to ensure quality/safety
                hf_url = f"https://huggingface.co/api/datasets?search={topic}&sort=downloads&direction=-1&limit=3&filter=safe"
                response = requests.get(hf_url, timeout=10)

                found_datasets = []
                if response.status_code == 200:
                    datasets = response.json()
                    if datasets:
                        found_datasets = [d["id"] for d in datasets]
                        reflect_logger.reflect(
                            f"Found {len(found_datasets)} verified resources: {found_datasets}",
                            layer="HUB-DISCOVERY",
                        )
                    else:
                        reflect_logger.reflect(
                            f"No specific datasets found on HF for '{topic}'",
                            layer="HUB-DISCOVERY",
                        )
            except Exception as e:
                logger.error(f"HF Search failed: {e}")

            # 2. WEB_DISCOVERY (Strict Source: Google -> Official Docs)
            web_context = ""
            try:
                reflect_logger.reflect(
                    f"Querying Google for official documentation on '{topic}'...",
                    layer="WEB-RESEARCH",
                )
                # Force "official documentation" or "tutorial" in query
                search_query = f"{topic} official documentation OR tutorial site:github.com OR site:huggingface.co OR site:.org"
                results = web_search_tool.search_google(search_query, num_results=2)

                if results:
                    reflect_logger.reflect(
                        f"Found {len(results)} official sources.", layer="WEB-RESEARCH"
                    )
                    web_context = "\n".join(results)
                else:
                    reflect_logger.reflect(
                        "No verified official docs found.", layer="WEB-RESEARCH"
                    )
            except Exception as e:
                logger.error(f"Web Search failed: {e}")

            # 3. TEACHER_DISTILL (Synthesis using Ollama)
            try:

                teacher_model = "llama3.1:8b"  # Modelo superior para sÃ­ntese
                reflect_logger.reflect(
                    f"Requesting Knowledge Distillation from {teacher_model.upper()} (Ollama)...",
                    layer="TEACHER-DISTILL",
                )

                # Gera dados sintÃ©ticos usando o agente local
                self._generate_synthetic_data(
                    topic, context=web_context, teacher_model=teacher_model
                )

            except Exception as e:
                logger.error(f"Distillation failed: {e}")

            logger.info(f"âœ… Research for '{topic}' completed. Knowledge synthesized.")

    def _generate_synthetic_data(
        self, topic: str, context: str = "", teacher_model: str = "llama3.1:8b"
    ):
        """Generates synthetic preference pairs for the local brain using gathered context"""
        from src.utils.logger_reflection import reflect_logger
        from src.core.intelligence.ai_agent import ai_agent

        reflect_logger.reflect(
            f"Synthesizing Neural Preference Pairs (DPO) for '{topic}'...",
            layer="BRAIN-SYNTHESIS",
        )

        ds_dir = self.data_dir / "training_datasets" / "autonomous"
        ds_dir.mkdir(parents=True, exist_ok=True)
        ds_path = ds_dir / f"{topic}_synthetic.jsonl"

        # Chamada real ao Ollama via AI Agent para gerar par CHOSEN/REJECTED
        prompt = f'Com base no seguinte contexto sobre {topic}: \'{context}\', gere um par DPO (Chosen/Rejected) para treinamento de uma IA. Retorne apenas JSON no formato: {{"chosen": "...", "rejected": "..."}}'

        try:
            # Use async Ollama call from ai_agent but run it synchronously inside this thread
            try:
                from src.core.intelligence.ai_agent import ai_agent
                import asyncio

                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    raw_response = loop.run_until_complete(
                        ai_agent._call_ollama_async(
                            prompt,
                            image_data=None,
                            model=teacher_model,
                            system_prompt="Voc\u00ea \u00e9 um Professor de IA especializado em Synthetic Data Generation.",
                        )
                    )
                finally:
                    try:
                        loop.close()
                    except Exception:
                        pass
            except Exception:
                # Fallback: keep raw_response empty to proceed safely
                raw_response = ""

            # Limpar resposta para JSON se necessÃ¡rio
            import re

            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                distilled_data = json.loads(json_match.group(0))
            else:
                distilled_data = {
                    "chosen": raw_response or f"Explicacao sintetica sobre {topic}",
                    "rejected": f"Eu acho que {topic} \u00e9 algo irrelevante.",
                }

            dummy_data = {
                "prompt": f"Explique o conceito de {topic} com base na documentaÃ§Ã£o oficial.",
                "chosen": distilled_data.get("chosen", ""),
                "rejected": distilled_data.get("rejected", ""),
            }

            with open(ds_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(dummy_data, ensure_ascii=False) + "\n")

            reflect_logger.reflect(
                f"Dataset generated: {ds_path.relative_to(self.data_dir)}",
                layer="BRAIN-SYNTHESIS",
            )

            # Queue for training
            self.add_training_task(
                task_id=f"auto_{topic}_{int(time.time())}",
                dataset_path=ds_path,
                model_name="jarvis-local-v1",
                priority=min(10, 5 + int(time.time()) % 5),
            )
        except Exception as e:
            logger.error(f"Failed to generate synthetic data: {e}")

    def _run_training_task(self, task: TrainingTask) -> bool:
        """
        Run a training task.

        Args:
            task: Training task to run

        Returns:
            True if training succeeded
        """
        try:
            start_time = time.time()

            logger.info(
                f"Starting training: {task.model_name} with {task.dataset_path}"
            )

            # Use callback if provided
            if self.training_callback:
                success = self.training_callback(task)
            else:
                # Default: just log (no actual training)
                logger.warning("No training callback provided, simulating training")
                time.sleep(5)  # Simulate training time
                success = True

            training_time = time.time() - start_time
            self.stats.total_training_time_seconds += training_time

            logger.info(
                f"Training {'succeeded' if success else 'failed'} in {training_time:.1f}s"
            )

            return success

        except Exception as e:
            logger.error(f"Error running training task: {e}", exc_info=True)
            return False

    def add_training_task(
        self,
        task_id: str,
        dataset_path: Path,
        model_name: str,
        priority: int = 5,
        config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a training task to the queue.

        Args:
            task_id: Unique task ID
            dataset_path: Path to training dataset
            model_name: Name of model to train
            priority: Task priority (1-10, higher is more important)
            config: Optional training configuration

        Returns:
            True if task was added successfully
        """
        task = TrainingTask(
            task_id=task_id,
            dataset_path=dataset_path,
            model_name=model_name,
            priority=priority,
            config=config or {},
        )

        return self.training_queue.add_task(task)

    def schedule_daily_consolidation(self, hour: int = 23) -> None:
        """
        Schedule daily data consolidation.

        Args:
            hour: Hour of day to run consolidation (0-23)
        """
        schedule_time = f"{hour:02d}:00"
        schedule.every().day.at(schedule_time).do(self._consolidate_data)
        logger.info(f"Scheduled daily consolidation at {schedule_time}")

    def _consolidate_data(self) -> None:
        """Consolidate training data from daily interactions."""
        try:
            logger.info("Running data consolidation")

            # This would integrate with DatasetBuilder
            # For now, just log
            consolidation_time = datetime.now().isoformat()

            consolidation_log = self.data_dir / "consolidation_log.json"
            logs = []

            if consolidation_log.exists():
                with open(consolidation_log, "r", encoding="utf-8") as f:
                    logs = json.load(f)

            logs.append({"timestamp": consolidation_time, "status": "completed"})

            with open(consolidation_log, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

            # Also analyze recent error logs as part of consolidation
            try:
                self._analyze_error_logs()
            except Exception:
                logger.debug("_analyze_error_logs failed during consolidation", exc_info=True)

            logger.info("Data consolidation completed")

        except Exception as e:
            logger.error(f"Error consolidating data: {e}", exc_info=True)

    def _analyze_error_logs(self, max_files: int = 6, tail_lines: int = 500) -> int:
        """Scan recent log files for ERROR/Exception occurrences and convert
        recurring failures into learning `insights` and (where appropriate)
        training tasks.

        Returns the number of insights created.
        """
        try:
            search_paths = [
                self.data_dir / "logs",
                Path.cwd() / "logs",
                Path("logs"),
                Path("src") / "logs",
            ]

            error_signatures = {}

            files_checked = 0
            for p in search_paths:
                if files_checked >= max_files:
                    break
                if not p.exists() or not p.is_dir():
                    continue

                for f in sorted(p.glob("**/*.*")):
                    if files_checked >= max_files:
                        break
                    if f.suffix.lower() not in [".log", ".txt", ".jsonl", ".out"]:
                        continue

                    try:
                        lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
                        tail = lines[-tail_lines:]
                    except Exception:
                        continue

                    files_checked += 1

                    for ln in tail:
                        if ("error" in ln.lower()) or ("exception" in ln.lower()) or ("traceback" in ln.lower()):
                            # Normalize signature: remove file paths and timestamps
                            sig = ln
                            sig = sig.replace("\\", "/")
                            # remove absolute paths
                            import re

                            sig = re.sub(r"[A-Za-z]:/[^\s]+", "<PATH>", sig)
                            sig = re.sub(r"/[^\s]+/[^\s]+", "<PATH>", sig)
                            sig_key = re.sub(r"\d+", "#", sig)[:200]

                            error_signatures.setdefault(sig_key, []).append({"line": ln, "file": str(f)})

            insights_dir = self.data_dir / "learning"
            insights_dir.mkdir(parents=True, exist_ok=True)
            insights_file = insights_dir / "insights.jsonl"

            created = 0
            for sig, samples in list(error_signatures.items()):
                count = len(samples)
                # Heuristic topic extraction
                topic = " ".join([w for w in re.findall(r"\b[a-zA-Z_]{4,}\b", sig.lower())[:3]])

                # Determine suggested actions
                suggestion = "Create a corrective note and add tests / exception handling."
                if any(k in sig.lower() for k in ["model", "inference", "cuda", "vram", "memory"]):
                    suggestion = "Schedule model robustness tests; check model loading and consider keep-alive or memory-guard."
                elif any(k in sig.lower() for k in ["importerror", "module", "filenotfounderror"]):
                    suggestion = "Add dependency / path validation and fallback; update installer scripts."

                insight = {
                    "timestamp": datetime.now().isoformat(),
                    "signature": sig,
                    "sample_count": count,
                    "example": samples[0],
                    "topic": topic,
                    "suggestion": suggestion,
                }

                # Append to insights file
                try:
                    with open(insights_file, "a", encoding="utf-8") as out:
                        out.write(json.dumps(insight, ensure_ascii=False) + "\n")
                    created += 1
                except Exception:
                    logger.debug("Failed to write insight", exc_info=True)

                # Convert some insights into training / research tasks
                try:
                    if any(k in sig.lower() for k in ["model", "train", "inference"]):
                        ds_dir = self.data_dir / "training_datasets" / "from_logs"
                        ds_dir.mkdir(parents=True, exist_ok=True)
                        ds_path = ds_dir / (f"log_{abs(hash(sig)) % 10000}.jsonl")
                        sample_obj = {
                            "prompt": f"Describe the failure observed in logs: {sig}",
                            "chosen": suggestion,
                            "rejected": "Ignore the error",
                        }
                        with open(ds_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(sample_obj, ensure_ascii=False) + "\n")

                        self.add_training_task(
                            task_id=f"logfix_{abs(hash(sig)) % 10000}_{int(time.time())}",
                            dataset_path=ds_path,
                            model_name="jarvis-local-v1",
                            priority=7,
                        )

                    # Heuristic: attempt automatic patch for simple runtime errors (safe-by-default)
                    if any(k in sig.lower() for k in ["modulenotfounderror", "importerror", "indexerror", "typeerror"]):
                        try:
                            from src.core.evolution.auto_patcher import auto_patcher

                            # Run patch attempt in background (non-blocking).
                            import threading

                            threading.Thread(
                                target=lambda ins=insight: auto_patcher.attempt_patch_from_insight(ins),
                                daemon=True,
                            ).start()
                        except Exception:
                            logger.debug("AutoPatcher not available or failed to start", exc_info=True)
                except Exception:
                    logger.debug("Failed to create training task from insight", exc_info=True)

            logger.info(f"Log analysis created {created} insights from {files_checked} files")
            return created

        except Exception as e:
            logger.error(f"Error analyzing logs: {e}", exc_info=True)
            return 0

    def get_status(self) -> Dict[str, Any]:
        """
        Get current dream cycle status.

        Returns:
            Dictionary with status information
        """
        system_stats = self.system_monitor.get_system_stats()
        queue_status = self.training_queue.get_queue_status()

        status = {
            "running": self.running,
            "in_training": self.in_training,
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "system": system_stats,
            "queue": queue_status,
            "statistics": self.stats.to_dict(),
        }

        return status

    def _load_stats(self) -> None:
        """Load statistics from disk."""
        stats_file = self.data_dir / "dream_cycle_stats.json"

        if not stats_file.exists():
            return

        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.stats = DreamCycleStats(**data)
            logger.info("Loaded dream cycle statistics")
        except Exception as e:
            logger.error(f"Error loading stats: {e}")

    def _save_stats(self) -> None:
        """Save statistics to disk."""
        stats_file = self.data_dir / "dream_cycle_stats.json"

        try:
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")

    def force_cycle(self) -> bool:
        """
        Force a dream cycle to run immediately (for testing).

        Returns:
            True if cycle was run
        """
        if self.in_training:
            logger.warning("Already in training, cannot force cycle")
            return False

        logger.info("Forcing dream cycle")
        self._run_dream_cycle()
        return True


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create dream cycle
    def training_callback(task: TrainingTask) -> bool:
        """Example training callback."""
        print(f"Training {task.model_name} with {task.dataset_path}")
        time.sleep(2)  # Simulate training
        return True

    dream_cycle = DreamCycle(
        data_dir=Path("./data/dream_cycle"),
        idle_conditions=IdleConditions(
            max_cpu_percent=30.0,
            night_start_hour=22,
            night_end_hour=6,
            min_idle_duration_seconds=60,  # Short for testing
            check_interval_seconds=30,
        ),
        training_callback=training_callback,
    )

    # Add some tasks
    dream_cycle.add_training_task(
        task_id="task_001",
        dataset_path=Path("./data/training_data/dataset1.jsonl"),
        model_name="phi-2",
        priority=8,
    )

    dream_cycle.add_training_task(
        task_id="task_002",
        dataset_path=Path("./data/training_data/dataset2.jsonl"),
        model_name="llama-3-8b",
        priority=5,
    )

    # Get status
    status = dream_cycle.get_status()
    print("\nDream Cycle Status:")
    print(f"Running: {status['running']}")
    print(f"Queue: {status['queue']['total_tasks']} tasks")
    print(f"Statistics: {status['statistics']}")

    # Start dream cycle
    # dream_cycle.start()

    # Force a cycle for testing
    # dream_cycle.force_cycle()

    print("\nDreamCycle example completed!")
