"""JARVIS 5.0 - Process Worker Factory.

Stability-first implementation with a lightweight worker abstraction.
"""

<<<<<<< Updated upstream
import asyncio
import logging
import multiprocessing
import threading
import time
import queue
import pickle
import signal
import os
import sys
import psutil
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from collections import deque, defaultdict
from concurrent.futures import ProcessPoolExecutor, Future, as_completed
import uuid
import socket
import json
import traceback
=======
from __future__ import annotations

import logging
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional
>>>>>>> Stashed changes

logger = logging.getLogger(__name__)

class WorkerState(Enum):
<<<<<<< Updated upstream
    """Estados de um worker process"""
=======
>>>>>>> Stashed changes
    STARTING = "starting"
    IDLE = "idle"
    BUSY = "busy"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    STOPPED = "stopped"

class WorkerType(Enum):
<<<<<<< Updated upstream
    """Tipos de workers especializados"""
    AI_PROCESSOR = "ai_processor"           # Processamento de IA/ML
    VISION_ANALYZER = "vision_analyzer"     # Análise de imagens/vídeo
    AUDIO_PROCESSOR = "audio_processor"     # Processamento de áudio
    DATA_TRANSFORMER = "data_transformer"  # Transformação de dados
    IO_WORKER = "io_worker"                # Operações I/O intensivas
    GENERAL_COMPUTE = "general_compute"     # Computação geral

class TaskPriority(Enum):
    """Prioridades de tarefas"""
=======
    AI_PROCESSOR = "ai_processor"
    VISION_ANALYZER = "vision_analyzer"
    AUDIO_PROCESSOR = "audio_processor"
    DATA_TRANSFORMER = "data_transformer"
    IO_WORKER = "io_worker"
    GENERAL_COMPUTE = "general_compute"


class TaskPriority(Enum):
>>>>>>> Stashed changes
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

@dataclass
class WorkerConfig:
<<<<<<< Updated upstream
    """Configuração de um worker process"""
    worker_type: WorkerType
    worker_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Process configuration
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    max_tasks_per_worker: int = 100
    worker_timeout_seconds: float = 300   # 5 minutes
    
    # Task configuration
    task_timeout_seconds: float = 60
    max_concurrent_tasks: int = 1         # Most workers handle one task at a time
    queue_size: int = 10
    
    # Health monitoring
    health_check_interval_seconds: float = 30
    max_consecutive_failures: int = 3
    restart_on_memory_limit: bool = True
    restart_on_cpu_limit: bool = True
    
    # IPC configuration
    use_shared_memory: bool = True
    shared_memory_size_mb: int = 10

@dataclass
class WorkerMetrics:
    """Métricas de um worker"""
    started_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_task_time: float = 0.0
    avg_task_time: float = 0.0
    current_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    current_cpu_percent: float = 0.0
    restarts: int = 0
    consecutive_failures: int = 0
    
    def record_task_completion(self, duration_seconds: float, success: bool):
        """Record task completion"""
        if success:
            self.tasks_completed += 1
            self.total_task_time += duration_seconds
            self.avg_task_time = self.total_task_time / self.tasks_completed
            self.consecutive_failures = 0
        else:
            self.tasks_failed += 1
            self.consecutive_failures += 1
    
    @property
    def uptime_seconds(self) -> float:
        """Worker uptime in seconds"""
        return (datetime.now() - self.started_at).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Task success rate (0.0 to 1.0)"""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks == 0:
            return 1.0
        return self.tasks_completed / total_tasks
    
    @property
    def last_heartbeat_age(self) -> float:
        """Seconds since last heartbeat"""
        if not self.last_heartbeat:
            return float('inf')
        return (datetime.now() - self.last_heartbeat).total_seconds()

@dataclass
class WorkerTask:
    """Task para execução em worker process"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    function_name: str = ""
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for IPC"""
        return {
            'task_id': self.task_id,
            'function_name': self.function_name,
            'args': self.args,
            'kwargs': self.kwargs,
            'priority': self.priority.value,
            'timeout_seconds': self.timeout_seconds,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkerTask':
        """Create from dictionary"""
        task_data = data.copy()
        task_data['priority'] = TaskPriority(task_data['priority'])
        task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
        return cls(**task_data)

class WorkerProcess:
    """Individual worker process wrapper"""
    
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.state = WorkerState.STARTING
        self.metrics = WorkerMetrics()
        
        # Process management
        self.process: Optional[multiprocessing.Process] = None
        self.pid: Optional[int] = None
        self.psutil_process: Optional[psutil.Process] = None
        
        # IPC
        self.task_queue: multiprocessing.Queue = multiprocessing.Queue(config.queue_size)
        self.result_queue: multiprocessing.Queue = multiprocessing.Queue()
        self.control_queue: multiprocessing.Queue = multiprocessing.Queue()
        
        # Tracking
        self._current_tasks: Set[str] = set()
        self._start_time = datetime.now()
        
        logger.debug(f"🏭 Worker {self.config.worker_id[:8]} ({self.config.worker_type.value}) created")
    
    def start(self):
        """Start the worker process"""
        if self.process and self.process.is_alive():
            return
        
        try:
            # Create and start process
            self.process = multiprocessing.Process(
                target=self._worker_main,
                name=f"worker_{self.config.worker_type.value}_{self.config.worker_id[:8]}"
            )
            self.process.start()
            self.pid = self.process.pid
            
            # Get psutil process for monitoring
            self.psutil_process = psutil.Process(self.pid)
            
            self.state = WorkerState.IDLE
            self.metrics.started_at = datetime.now()
            
            logger.info(f"🚀 Started worker {self.config.worker_id[:8]} (PID: {self.pid})")
            
        except Exception as e:
            logger.error(f"Failed to start worker {self.config.worker_id[:8]}: {e}")
            self.state = WorkerState.CRASHED
    
    def stop(self, timeout: float = 10.0):
        """Stop the worker process"""
        if not self.process:
            return
        
        logger.info(f"🛑 Stopping worker {self.config.worker_id[:8]}")
        self.state = WorkerState.STOPPING
        
        try:
            # Send stop signal
            self.control_queue.put({"command": "stop"})
            
            # Wait for graceful shutdown
            self.process.join(timeout=timeout)
            
            # Force kill if still alive
            if self.process.is_alive():
                logger.warning(f"Force killing worker {self.config.worker_id[:8]}")
                self.process.terminate()
                self.process.join(timeout=5.0)
                
                if self.process.is_alive():
                    self.process.kill()
                    self.process.join()
            
            self.state = WorkerState.STOPPED
            logger.info(f"✅ Worker {self.config.worker_id[:8]} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping worker {self.config.worker_id[:8]}: {e}")
            self.state = WorkerState.CRASHED
    
    def restart(self):
        """Restart the worker process"""
        logger.info(f"🔄 Restarting worker {self.config.worker_id[:8]}")
        self.stop()
        self.metrics.restarts += 1
        self.start()
    
    def submit_task(self, task: WorkerTask) -> bool:
        """Submit task to worker"""
        if self.state not in [WorkerState.IDLE, WorkerState.BUSY]:
            return False
        
        if len(self._current_tasks) >= self.config.max_concurrent_tasks:
            return False
        
        try:
            self.task_queue.put_nowait(task.to_dict())
            self._current_tasks.add(task.task_id)
            
            if len(self._current_tasks) >= self.config.max_concurrent_tasks:
                self.state = WorkerState.BUSY
            
            logger.debug(f"📤 Submitted task {task.task_id[:8]} to worker {self.config.worker_id[:8]}")
            return True
            
        except queue.Full:
            logger.warning(f"Task queue full for worker {self.config.worker_id[:8]}")
            return False
    
    def get_result(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """Get result from worker (non-blocking)"""
        try:
            result = self.result_queue.get_nowait()
            
            # Update tracking
            task_id = result.get('task_id')
            if task_id and task_id in self._current_tasks:
                self._current_tasks.remove(task_id)
                
                # Update metrics
                success = result.get('success', False)
                duration = result.get('duration_seconds', 0.0)
                self.metrics.record_task_completion(duration, success)
                
                # Update state
                if len(self._current_tasks) == 0:
                    self.state = WorkerState.IDLE
            
            logger.debug(f"📥 Got result for task {task_id[:8] if task_id else 'unknown'} from worker {self.config.worker_id[:8]}")
            return result
            
        except queue.Empty:
            return None
    
    def update_health_metrics(self):
        """Update health metrics from process"""
        if not self.psutil_process:
            return
        
        try:
            # Update memory usage
            memory_info = self.psutil_process.memory_info()
            self.metrics.current_memory_mb = memory_info.rss / (1024 * 1024)
            self.metrics.peak_memory_mb = max(self.metrics.peak_memory_mb, self.metrics.current_memory_mb)
            
            # Update CPU usage
            self.metrics.current_cpu_percent = self.psutil_process.cpu_percent()
            
            # Update heartbeat
            self.metrics.last_heartbeat = datetime.now()
            
            # Check health limits
            if (self.config.restart_on_memory_limit and 
                self.metrics.current_memory_mb > self.config.max_memory_mb):
                logger.warning(f"Worker {self.config.worker_id[:8]} exceeded memory limit ({self.metrics.current_memory_mb:.1f}MB > {self.config.max_memory_mb}MB)")
                self.state = WorkerState.OVERLOADED
                
            elif (self.config.restart_on_cpu_limit and 
                  self.metrics.current_cpu_percent > self.config.max_cpu_percent):
                logger.warning(f"Worker {self.config.worker_id[:8]} exceeded CPU limit ({self.metrics.current_cpu_percent:.1f}% > {self.config.max_cpu_percent}%)")
                self.state = WorkerState.OVERLOADED
            
            elif self.state == WorkerState.OVERLOADED:
                # Recovery from overload
                self.state = WorkerState.IDLE if len(self._current_tasks) == 0 else WorkerState.BUSY
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error updating health metrics for worker {self.config.worker_id[:8]}: {e}")
            self.state = WorkerState.CRASHED
    
    def is_healthy(self) -> bool:
        """Check if worker is healthy"""
        if not self.process or not self.process.is_alive():
            return False
        
        if self.state in [WorkerState.CRASHED, WorkerState.STOPPED]:
            return False
        
        if self.metrics.consecutive_failures >= self.config.max_consecutive_failures:
            return False
        
        if self.metrics.last_heartbeat_age > self.config.health_check_interval_seconds * 2:
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        return {
            "worker_id": self.config.worker_id,
            "worker_type": self.config.worker_type.value,
            "state": self.state.value,
            "pid": self.pid,
            "uptime_seconds": self.metrics.uptime_seconds,
            "tasks_completed": self.metrics.tasks_completed,
            "tasks_failed": self.metrics.tasks_failed,
            "success_rate": self.metrics.success_rate,
            "avg_task_time": self.metrics.avg_task_time,
            "current_memory_mb": self.metrics.current_memory_mb,
            "peak_memory_mb": self.metrics.peak_memory_mb,
            "current_cpu_percent": self.metrics.current_cpu_percent,
            "current_tasks": len(self._current_tasks),
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
            "queue_size": self.task_queue.qsize() if self.task_queue else 0,
            "restarts": self.metrics.restarts,
            "consecutive_failures": self.metrics.consecutive_failures,
            "last_heartbeat_age": self.metrics.last_heartbeat_age,
            "is_healthy": self.is_healthy()
        }
    
    def _worker_main(self):
        """Main function that runs in the worker process"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"🏃 Worker {self.config.worker_id[:8]} started in process {os.getpid()}")
        
        # Import worker functions based on type
        worker_functions = self._get_worker_functions()
        
        running = True
        while running:
            try:
                # Check for control commands
                try:
                    control_msg = self.control_queue.get_nowait()
                    if control_msg.get('command') == 'stop':
                        logger.info(f"🛑 Worker {self.config.worker_id[:8]} received stop command")
                        running = False
                        break
                except queue.Empty:
                    pass
                
                # Process tasks
                try:
                    task_dict = self.task_queue.get(timeout=1.0)
                    task = WorkerTask.from_dict(task_dict)
                    
                    start_time = time.time()
                    result = None
                    error = None
                    
                    try:
                        # Execute task
                        function_name = task.function_name
                        if function_name in worker_functions:
                            func = worker_functions[function_name]
                            result = func(*task.args, **task.kwargs)
                        else:
                            raise ValueError(f"Unknown function: {function_name}")
                        
                        success = True
                        
                    except Exception as e:
                        error = str(e)
                        success = False
                        logger.error(f"Task {task.task_id[:8]} failed: {e}")
                    
                    duration = time.time() - start_time
                    
                    # Send result back
                    result_msg = {
                        'task_id': task.task_id,
                        'result': result,
                        'error': error,
                        'success': success,
                        'duration_seconds': duration,
                        'worker_id': self.config.worker_id
                    }
                    
                    self.result_queue.put(result_msg)
                    
                except queue.Empty:
                    # No tasks available, continue
                    pass
                    
            except Exception as e:
                logger.error(f"Worker {self.config.worker_id[:8]} error: {e}")
                time.sleep(1.0)
        
        logger.info(f"✅ Worker {self.config.worker_id[:8]} process ending")
    
    def _signal_handler(self, signum, frame):
        """Handle process signals"""
        logger.info(f"Worker {self.config.worker_id[:8]} received signal {signum}")
        # Graceful shutdown would go here
    
    def _get_worker_functions(self) -> Dict[str, Callable]:
        """Get available functions for this worker type"""
        # This would be expanded with actual worker functions
        common_functions = {
            'test_function': lambda x, y=10: x + y,
            'compute_square': lambda x: x * x,
            'process_text': lambda text: text.upper(),
        }
        
        # Type-specific functions would be added here
        if self.config.worker_type == WorkerType.AI_PROCESSOR:
            common_functions.update({
                'ai_inference': self._mock_ai_inference,
                'train_model': self._mock_train_model,
            })
        elif self.config.worker_type == WorkerType.VISION_ANALYZER:
            common_functions.update({
                'analyze_image': self._mock_analyze_image,
                'detect_objects': self._mock_detect_objects,
            })
        elif self.config.worker_type == WorkerType.AUDIO_PROCESSOR:
            common_functions.update({
                'process_audio': self._mock_process_audio,
                'speech_to_text': self._mock_speech_to_text,
            })
        
        return common_functions
    
    def _mock_ai_inference(self, data, model="default"):
        """Mock AI inference function"""
        time.sleep(0.1)  # Simulate compute time
        return {"prediction": f"AI result for {model}", "confidence": 0.95}
    
    def _mock_train_model(self, dataset, epochs=10):
        """Mock model training function"""
        time.sleep(0.2)  # Simulate training time
        return {"status": "trained", "epochs": epochs, "accuracy": 0.92}
    
    def _mock_analyze_image(self, image_path):
        """Mock image analysis function"""
        time.sleep(0.05)  # Simulate processing time
        return {"objects": ["person", "car"], "confidence": 0.88}
    
    def _mock_detect_objects(self, image_data):
        """Mock object detection function"""
        time.sleep(0.08)  # Simulate detection time
        return {"detections": [{"class": "person", "bbox": [10, 20, 100, 200]}]}
    
    def _mock_process_audio(self, audio_data):
        """Mock audio processing function"""
        time.sleep(0.03)  # Simulate processing time
        return {"processed": True, "duration": 3.5}
    
    def _mock_speech_to_text(self, audio_file):
        """Mock speech-to-text function"""
        time.sleep(0.15)  # Simulate transcription time
        return {"text": "Hello, this is mock transcription", "confidence": 0.91}
=======
    worker_type: WorkerType
    worker_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    max_tasks_per_worker: int = 100
    worker_timeout_seconds: float = 300.0
    task_timeout_seconds: float = 60.0
    max_concurrent_tasks: int = 1
    queue_size: int = 10


@dataclass
class WorkerTask:
    task_id: str
    worker_type: WorkerType
    function_name: str
    args: tuple
    kwargs: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
>>>>>>> Stashed changes

class ProcessWorkerFactory:
<<<<<<< Updated upstream
    """
    Factory para gerenciar workers em processos separados
    
    Elimina limitações do GIL através de multiprocessing,
    com load balancing, health monitoring e auto-recovery.
    """
    
    def __init__(self, max_workers_per_type: int = 4):
        # Worker management
        self._workers: Dict[str, WorkerProcess] = {}
        self._workers_by_type: Dict[WorkerType, List[str]] = defaultdict(list)
        self._worker_configs: Dict[WorkerType, WorkerConfig] = {}
        
        # Task queues by priority
        self._task_queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }
        
        # Configuration
        self.max_workers_per_type = max_workers_per_type
        
        # Background management
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._dispatcher_thread: Optional[threading.Thread] = None
        self._result_collector_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Synchronization
        self._lock = threading.RLock()
        
        # Metrics
        self.total_tasks_submitted = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        self.factory_start_time: Optional[datetime] = None
        
        logger.info("🏭 Process Worker Factory initialized")
    
    def configure_worker_type(self, worker_type: WorkerType, config: WorkerConfig):
        """Configure settings for a worker type"""
        with self._lock:
            self._worker_configs[worker_type] = config
            logger.info(f"⚙️ Configured {worker_type.value} workers")
    
    def start(self):
        """Start the worker factory"""
        if self._running:
            return
        
        logger.info("🚀 Starting Process Worker Factory")
        self._running = True
        self.factory_start_time = datetime.now()
        
        # Start background threads
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="worker_monitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        self._dispatcher_thread = threading.Thread(
            target=self._dispatcher_loop,
            name="task_dispatcher",
            daemon=True
        )
        self._dispatcher_thread.start()
        
        self._result_collector_thread = threading.Thread(
            target=self._result_collector_loop,
            name="result_collector",
            daemon=True
        )
        self._result_collector_thread.start()
        
        logger.info("✅ Process Worker Factory started")
    
    def stop(self, timeout: float = 30.0):
        """Stop the worker factory"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping Process Worker Factory")
        self._running = False
        self._stop_event.set()
        
        # Wait for background threads
        for thread in [self._monitor_thread, self._dispatcher_thread, self._result_collector_thread]:
            if thread:
                thread.join(timeout=5.0)
        
        # Stop all workers
        with self._lock:
            worker_list = list(self._workers.values())
        
        for worker in worker_list:
            worker.stop(timeout=10.0)
        
        logger.info("✅ Process Worker Factory stopped")
    
    def submit_task(self, 
                   worker_type: WorkerType,
                   function_name: str,
                   *args,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   timeout_seconds: Optional[float] = None,
                   **kwargs) -> str:
        """Submit task for execution"""
=======
    """Simplified worker factory used by performance-sensitive modules."""

    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._configs: Dict[WorkerType, WorkerConfig] = {}
        self._results: Dict[str, Future] = {}
        self._submitted_tasks = 0
        self._completed_tasks = 0
        self._failed_tasks = 0

        self._executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="jarvis-worker"
        )
        self._function_registry: Dict[str, Callable[..., Any]] = {
            "yolo_inference": self._fallback_yolo_inference,
        }

    def configure_worker_type(
        self, worker_type: WorkerType, config: WorkerConfig
    ) -> bool:
        with self._lock:
            self._configs[worker_type] = config
        logger.debug("Configured worker type %s", worker_type.value)
        return True

    def register_function(
        self, function_name: str, function: Callable[..., Any]
    ) -> None:
        self._function_registry[function_name] = function

    def start(self) -> bool:
        self._running = True
        return True

    def stop(self) -> bool:
        self._running = False
        with self._lock:
            pending = list(self._results.values())
            self._results.clear()
        for future in pending:
            future.cancel()
        return True

    def submit_task(
        self,
        worker_type: WorkerType,
        function_name: str,
        *args: Any,
        priority: TaskPriority = TaskPriority.NORMAL,
        **kwargs: Any,
    ) -> str:
        if not self._running:
            self.start()

        task_id = str(uuid.uuid4())
>>>>>>> Stashed changes
        task = WorkerTask(
            task_id=task_id,
            worker_type=worker_type,
            function_name=function_name,
            args=args,
            kwargs=kwargs,
            priority=priority,
<<<<<<< Updated upstream
            timeout_seconds=timeout_seconds,
            metadata={"worker_type": worker_type.value}
        )
        
        with self._lock:
            self._task_queues[priority].append((worker_type, task))
            self.total_tasks_submitted += 1
        
        logger.debug(f"📤 Submitted {function_name} task {task.task_id[:8]} for {worker_type.value}")
        return task.task_id
    
    def get_task_result(self, task_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Get result for a specific task (blocking)"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check all workers for results
            with self._lock:
                for worker in self._workers.values():
                    result = worker.get_result()
                    if result and result.get('task_id') == task_id:
                        return result
            
            time.sleep(0.1)
        
        logger.warning(f"Timeout waiting for result of task {task_id[:8]}")
        return None
    
    def scale_workers(self, worker_type: WorkerType, target_count: int):
        """Scale workers for a specific type"""
        with self._lock:
            current_workers = self._workers_by_type[worker_type]
            current_count = len(current_workers)
            
            if target_count > current_count:
                # Scale up
                for _ in range(target_count - current_count):
                    if len(current_workers) >= self.max_workers_per_type:
                        logger.warning(f"Cannot scale {worker_type.value} beyond max limit ({self.max_workers_per_type})")
                        break
                    
                    self._create_worker(worker_type)
                    
            elif target_count < current_count:
                # Scale down
                workers_to_remove = current_count - target_count
                for _ in range(workers_to_remove):
                    if current_workers:
                        worker_id = current_workers.pop()
                        worker = self._workers.get(worker_id)
                        if worker:
                            worker.stop()
                            del self._workers[worker_id]
    
    def _create_worker(self, worker_type: WorkerType) -> Optional[str]:
        """Create a new worker of specified type"""
        config = self._worker_configs.get(worker_type)
        if not config:
            # Use default configuration
            config = WorkerConfig(worker_type=worker_type)
        
        worker = WorkerProcess(config)
        worker.start()
        
        if worker.is_healthy():
            with self._lock:
                self._workers[worker.config.worker_id] = worker
                self._workers_by_type[worker_type].append(worker.config.worker_id)
            
            logger.info(f"➕ Created {worker_type.value} worker {worker.config.worker_id[:8]}")
            return worker.config.worker_id
        else:
            logger.error(f"Failed to create healthy {worker_type.value} worker")
            worker.stop()
            return None
    
    def _get_best_worker_for_task(self, worker_type: WorkerType, task: WorkerTask) -> Optional[WorkerProcess]:
        """Get the best available worker for a task"""
        with self._lock:
            worker_ids = self._workers_by_type.get(worker_type, [])
            
            if not worker_ids:
                # No workers of this type - create one
                new_worker_id = self._create_worker(worker_type)
                if new_worker_id:
                    return self._workers.get(new_worker_id)
                return None
            
            # Find best worker (idle, lowest load, healthy)
            best_worker = None
            best_score = float('inf')
            
            for worker_id in worker_ids:
                worker = self._workers.get(worker_id)
                if not worker or not worker.is_healthy():
                    continue
                
                if worker.state == WorkerState.IDLE:
                    # Idle worker is best
                    return worker
                
                if worker.state == WorkerState.BUSY:
                    # Score based on current load
                    load_score = len(worker._current_tasks) / worker.config.max_concurrent_tasks
                    if load_score < best_score:
                        best_score = load_score
                        best_worker = worker
            
            return best_worker
    
    def _monitor_loop(self):
        """Monitor worker health and perform maintenance"""
        while self._running:
            try:
                with self._lock:
                    workers_to_restart = []
                    workers_to_remove = []
                    
                    for worker_id, worker in self._workers.items():
                        # Update health metrics
                        worker.update_health_metrics()
                        
                        # Check if worker needs restart
                        if not worker.is_healthy():
                            if worker.state == WorkerState.CRASHED:
                                workers_to_remove.append(worker_id)
                            elif worker.state in [WorkerState.OVERLOADED, WorkerState.UNHEALTHY]:
                                workers_to_restart.append(worker_id)
                
                # Restart unhealthy workers (outside lock to avoid deadlock)
                for worker_id in workers_to_restart:
                    worker = self._workers.get(worker_id)
                    if worker:
                        logger.warning(f"⚠️ Restarting unhealthy worker {worker_id[:8]}")
                        worker.restart()
                
                # Remove crashed workers
                for worker_id in workers_to_remove:
                    worker = self._workers.get(worker_id)
                    if worker:
                        logger.error(f"💥 Removing crashed worker {worker_id[:8]}")
                        worker.stop()
                        
                        with self._lock:
                            del self._workers[worker_id]
                            # Remove from type mapping
                            for worker_type, worker_list in self._workers_by_type.items():
                                if worker_id in worker_list:
                                    worker_list.remove(worker_id)
                                    break
                
                self._stop_event.wait(timeout=30.0)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Worker monitor error: {e}")
                time.sleep(5.0)
    
    def _dispatcher_loop(self):
        """Dispatch tasks to available workers"""
        while self._running:
            try:
                task_dispatched = False
                
                # Process tasks by priority (highest first)
                for priority in TaskPriority:
                    with self._lock:
                        if not self._task_queues[priority]:
                            continue
                        
                        worker_type, task = self._task_queues[priority].popleft()
                    
                    # Find worker for task
                    worker = self._get_best_worker_for_task(worker_type, task)
                    if worker and worker.submit_task(task):
                        task_dispatched = True
                        logger.debug(f"📋 Dispatched task {task.task_id[:8]} to worker {worker.config.worker_id[:8]}")
                    else:
                        # Put task back in queue if no worker available
                        with self._lock:
                            self._task_queues[priority].appendleft((worker_type, task))
                        
                        # Only try one task per cycle if no worker available
                        break
                
                # Sleep if no tasks dispatched
                if not task_dispatched:
                    self._stop_event.wait(timeout=0.1)
                    
            except Exception as e:
                logger.error(f"Task dispatcher error: {e}")
                time.sleep(1.0)
    
    def _result_collector_loop(self):
        """Collect results from all workers"""
        while self._running:
            try:
                results_collected = 0
                
                with self._lock:
                    workers = list(self._workers.values())
                
                # Collect results from all workers
                for worker in workers:
                    while True:
                        result = worker.get_result()
                        if not result:
                            break
                        
                        results_collected += 1
                        
                        # Update global metrics
                        if result.get('success', False):
                            self.total_tasks_completed += 1
                        else:
                            self.total_tasks_failed += 1
                        
                        # Log result (in real implementation, would store or forward results)
                        task_id = result.get('task_id', 'unknown')
                        success = result.get('success', False)
                        duration = result.get('duration_seconds', 0.0)
                        
                        status = "✅" if success else "❌"
                        logger.debug(f"{status} Task {task_id[:8]} completed in {duration:.2f}s")
                
                # Sleep if no results collected
                if results_collected == 0:
                    self._stop_event.wait(timeout=0.1)
                    
            except Exception as e:
                logger.error(f"Result collector error: {e}")
                time.sleep(1.0)
    
=======
        )

        future = self._executor.submit(self._execute_task, task)
        with self._lock:
            self._results[task_id] = future
            self._submitted_tasks += 1

        return task_id

    def get_task_result(
        self, task_id: str, timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        with self._lock:
            future = self._results.get(task_id)

        if future is None:
            return None

        try:
            result = future.result(timeout=timeout)
        except TimeoutError:
            return {
                "success": False,
                "result": None,
                "error": "timeout",
                "duration_seconds": timeout or 0.0,
            }
        finally:
            if future.done():
                with self._lock:
                    self._results.pop(task_id, None)

        return result

>>>>>>> Stashed changes
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
<<<<<<< Updated upstream
            # Count workers by type and state
            workers_by_type = {}
            workers_by_state = defaultdict(int)
            total_tasks_in_progress = 0
            
            for worker_type, worker_ids in self._workers_by_type.items():
                worker_stats = []
                for worker_id in worker_ids:
                    worker = self._workers.get(worker_id)
                    if worker:
                        stats = worker.get_stats()
                        worker_stats.append(stats)
                        workers_by_state[stats['state']] += 1
                        total_tasks_in_progress += stats['current_tasks']
                
                workers_by_type[worker_type.value] = {
                    'count': len(worker_ids),
                    'workers': worker_stats
                }
            
            # Task queue sizes
            queue_sizes = {
                priority.name: len(queue) for priority, queue in self._task_queues.items()
            }
            
            uptime = None
            if self.factory_start_time:
                uptime = (datetime.now() - self.factory_start_time).total_seconds()
            
            return {
                "factory": {
                    "running": self._running,
                    "uptime_seconds": uptime,
                    "total_workers": len(self._workers),
                    "max_workers_per_type": self.max_workers_per_type,
                    "total_tasks_submitted": self.total_tasks_submitted,
                    "total_tasks_completed": self.total_tasks_completed,
                    "total_tasks_failed": self.total_tasks_failed,
                    "tasks_in_progress": total_tasks_in_progress,
                    "success_rate": (self.total_tasks_completed / max(1, self.total_tasks_completed + self.total_tasks_failed)) * 100
                },
                "workers_by_type": workers_by_type,
                "workers_by_state": dict(workers_by_state),
                "task_queues": queue_sizes
            }
    
    def get_worker_stats(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a specific worker"""
        with self._lock:
            worker = self._workers.get(worker_id)
            return worker.get_stats() if worker else None

# Global instance
process_worker_factory = ProcessWorkerFactory()

if __name__ == "__main__":
    # Test the process worker factory
    def test_worker_factory():
        print("🧪 Testing Process Worker Factory")
        print("=" * 50)
        
        # Configure worker types
        ai_config = WorkerConfig(
            worker_type=WorkerType.AI_PROCESSOR,
            max_concurrent_tasks=2,
            max_memory_mb=256
        )
        
        vision_config = WorkerConfig(
            worker_type=WorkerType.VISION_ANALYZER,
            max_concurrent_tasks=1,
            max_memory_mb=512
        )
        
        process_worker_factory.configure_worker_type(WorkerType.AI_PROCESSOR, ai_config)
        process_worker_factory.configure_worker_type(WorkerType.VISION_ANALYZER, vision_config)
        
        # Start factory
        process_worker_factory.start()
        
        # Submit test tasks
        print("\n📤 Submitting test tasks...")
        
        task_ids = []
        
        # AI tasks
        task_ids.append(process_worker_factory.submit_task(
            WorkerType.AI_PROCESSOR, 
            "ai_inference", 
            {"data": "test"}, 
            model="bert",
            priority=TaskPriority.HIGH
        ))
        
        task_ids.append(process_worker_factory.submit_task(
            WorkerType.AI_PROCESSOR,
            "train_model",
            {"training_data": "dataset"},
            epochs=5
        ))
        
        # Vision tasks
        task_ids.append(process_worker_factory.submit_task(
            WorkerType.VISION_ANALYZER,
            "analyze_image",
            "test_image.jpg"
        ))
        
        task_ids.append(process_worker_factory.submit_task(
            WorkerType.VISION_ANALYZER,
            "detect_objects",
            {"image_data": "binary_data"}
        ))
        
        # Wait for results
        print(f"⏳ Waiting for {len(task_ids)} tasks to complete...")
        
        completed_results = []
        for task_id in task_ids:
            result = process_worker_factory.get_task_result(task_id, timeout=10.0)
            if result:
                completed_results.append(result)
                print(f"✅ Task {task_id[:8]}: {result.get('success')} ({result.get('duration_seconds', 0):.2f}s)")
            else:
                print(f"❌ Task {task_id[:8]}: Timeout")
        
        # Wait a bit for background processing
        time.sleep(2)
        
        # Show statistics
        print("\n📊 Factory Statistics:")
        stats = process_worker_factory.get_stats()
        
        print(f"Factory: {stats['factory']}")
        print(f"Workers by state: {stats['workers_by_state']}")
        print(f"Task queues: {stats['task_queues']}")
        
        for worker_type, worker_info in stats['workers_by_type'].items():
            print(f"\n{worker_type.upper()} Workers ({worker_info['count']}):")
            for worker in worker_info['workers']:
                print(f"  Worker {worker['worker_id'][:8]}: {worker['state']} - {worker['tasks_completed']} tasks")
        
        # Stop factory
        process_worker_factory.stop()
        
        print("✅ Test completed")
    
    test_worker_factory()
=======
            in_flight = len(self._results)
            submitted = self._submitted_tasks
            completed = self._completed_tasks
            failed = self._failed_tasks

        return {
            "running": self._running,
            "submitted_tasks": submitted,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "in_flight": in_flight,
            "configured_worker_types": [wt.value for wt in self._configs.keys()],
        }

    def _execute_task(self, task: WorkerTask) -> Dict[str, Any]:
        started = time.perf_counter()
        try:
            handler = self._function_registry.get(task.function_name)
            if handler is None:
                raise ValueError(f"Unsupported worker function: {task.function_name}")

            output = handler(*task.args, **task.kwargs)
            duration = time.perf_counter() - started

            with self._lock:
                self._completed_tasks += 1

            return {
                "success": True,
                "result": output,
                "duration_seconds": duration,
                "worker_type": task.worker_type.value,
                "function_name": task.function_name,
            }
        except Exception as exc:
            duration = time.perf_counter() - started
            with self._lock:
                self._failed_tasks += 1
            logger.error("Worker task failed (%s): %s", task.function_name, exc)
            return {
                "success": False,
                "result": None,
                "error": str(exc),
                "duration_seconds": duration,
                "worker_type": task.worker_type.value,
                "function_name": task.function_name,
            }

    def _fallback_yolo_inference(self, *args: Any, **kwargs: Any) -> list:
        # Conservative fallback: return empty detections and let caller handle local inference fallback.
        return []


process_worker_factory = ProcessWorkerFactory()


__all__ = [
    "ProcessWorkerFactory",
    "TaskPriority",
    "WorkerConfig",
    "WorkerState",
    "WorkerType",
    "process_worker_factory",
]
>>>>>>> Stashed changes
