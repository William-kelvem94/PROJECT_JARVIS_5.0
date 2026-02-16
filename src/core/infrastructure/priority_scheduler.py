#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Priority Scheduling Kernel (Kernel de Escalonamento Prioritário)
==============================================================================
FASE 1.2: Substitui QTimer fixo por sistema de eventos assíncronos com prioridades.

Responsibilities:
- Escalonamento de tarefas por níveis de prioridade
- Preempção inteligente para tarefas críticas
- Throttling automático baseado em carga do sistema
- Fair scheduling para tarefas de mesma prioridade
- Metrics e observabilidade do scheduler

Philosophy:
- Tarefas críticas nunca esperem
- Recursos limitados distribuídos de forma justa
- Prevenção de starvation de tarefas baixa prioridade
- Adaptação dinâmica à carga do sistema
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from enum import IntEnum, Enum
from typing import Dict, List, Optional, Any, Callable, Coroutine
from dataclasses import dataclass, field
from collections import deque
import uuid

logger = logging.getLogger(__name__)


class TaskPriority(IntEnum):
    """Prioridades de tarefas (menor valor = maior prioridade)"""

    EMERGENCY = 0  # Emergências e kill switches
    CRITICAL = 10  # UI responsividade, safety systems
    HIGH = 20  # User interactions, time-sensitive operations
    NORMAL = 30  # Regular processing, AI responses
    LOW = 40  # Background processing, learning
    IDLE = 50  # Cleanup, non-urgent maintenance


class TaskType(Enum):
    """Tipos de tarefas"""

    ONESHOT = "oneshot"  # Executa uma vez
    PERIODIC = "periodic"  # Executa periodicamente
    CONTINUOUS = "continuous"  # Loop contínuo
    CONDITIONAL = "conditional"  # Executa quando condição for atendida


class TaskState(Enum):
    """Estados de uma tarefa"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


@dataclass
class TaskMetrics:
    """Métricas de execução de uma tarefa"""

    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_count: int = 0
    total_runtime: float = 0.0
    average_runtime: float = 0.0
    last_runtime: float = 0.0
    failure_count: int = 0
    last_error: Optional[str] = None


@dataclass
class SchedulerTask:
    """Definição de uma tarefa no scheduler"""

    id: str
    name: str
    coroutine_factory: Callable[[], Coroutine]
    priority: TaskPriority
    task_type: TaskType

    # Scheduling parameters
    interval_seconds: Optional[float] = None  # Para tarefas periódicas
    delay_seconds: float = 0.0  # Delay antes da primeira execução
    max_runtime_seconds: Optional[float] = None  # Timeout para execução
    max_retries: int = 3  # Tentativas em caso de erro

    # Conditional parameters
    condition: Optional[Callable[[], bool]] = None  # Para tarefas condicionais

    # State and metrics
    state: TaskState = TaskState.PENDING
    metrics: TaskMetrics = field(default_factory=TaskMetrics)
    asyncio_task: Optional[asyncio.Task] = None
    next_execution: Optional[datetime] = None

    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class SystemLoad:
    """Informações de carga do sistema"""

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_io_percent: float = 0.0
    network_io_percent: float = 0.0
    temperature: Optional[float] = None

    @property
    def overall_load(self) -> float:
        """Carga geral do sistema (0.0 a 1.0)"""
        return (self.cpu_percent + self.memory_percent) / 200.0


class PriorityScheduler:
    """
    Kernel de Escalonamento Prioritário para JARVIS 5.0

    Gerencia execução de tarefas assíncronas com diferentes prioridades,
    preempção inteligente e adaptação à carga do sistema.
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, SchedulerTask] = {}
        self.task_queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }

        # Execution control
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._scheduler_loop: Optional[asyncio.AbstractEventLoop] = None

        # System monitoring
        self.system_load = SystemLoad()
        self._load_monitor_task: Optional[asyncio.Task] = None

        # Metrics and observability
        self.total_tasks_executed = 0
        self.total_execution_time = 0.0
        self.scheduler_start_time: Optional[datetime] = None

        # Configuration
        self.load_adaptation_enabled = True
        self.preemption_enabled = True
        self.max_load_threshold = 0.9  # Suspend low priority tasks if load > 90%

        logger.info("⚙️ Priority Scheduler initialized")

    def schedule_task(
        self,
        name: str,
        coroutine_factory: Callable[[], Coroutine],
        priority: TaskPriority = TaskPriority.NORMAL,
        task_type: TaskType = TaskType.ONESHOT,
        interval_seconds: Optional[float] = None,
        delay_seconds: float = 0.0,
        max_runtime_seconds: Optional[float] = None,
        max_retries: int = 3,
        condition: Optional[Callable[[], bool]] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Agendar uma tarefa para execução

        Returns:
            Task ID for management
        """
        task_id = str(uuid.uuid4())

        # Calculate next execution time
        next_execution = datetime.now() + timedelta(seconds=delay_seconds)

        task = SchedulerTask(
            id=task_id,
            name=name,
            coroutine_factory=coroutine_factory,
            priority=priority,
            task_type=task_type,
            interval_seconds=interval_seconds,
            delay_seconds=delay_seconds,
            max_runtime_seconds=max_runtime_seconds,
            max_retries=max_retries,
            condition=condition,
            context=context or {},
            tags=tags or [],
            next_execution=next_execution,
        )

        self.tasks[task_id] = task
        self.task_queues[priority].append(task_id)

        logger.debug(
            f"📋 Scheduled task '{name}' (ID: {task_id[:8]}, Priority: {priority.name})"
        )

        return task_id

    def schedule_periodic(
        self,
        name: str,
        coroutine_factory: Callable[[], Coroutine],
        interval_seconds: float,
        priority: TaskPriority = TaskPriority.NORMAL,
        immediate: bool = False,
        **kwargs,
    ) -> str:
        """Convenience method for periodic tasks"""
        delay = 0.0 if immediate else interval_seconds

        return self.schedule_task(
            name=name,
            coroutine_factory=coroutine_factory,
            priority=priority,
            task_type=TaskType.PERIODIC,
            interval_seconds=interval_seconds,
            delay_seconds=delay,
            **kwargs,
        )

    def schedule_conditional(
        self,
        name: str,
        coroutine_factory: Callable[[], Coroutine],
        condition: Callable[[], bool],
        check_interval_seconds: float = 1.0,
        priority: TaskPriority = TaskPriority.NORMAL,
        **kwargs,
    ) -> str:
        """Convenience method for conditional tasks"""

        # Wrapper coroutine factory that includes condition checking
        async def conditional_wrapper():
            while True:
                if condition():
                    await coroutine_factory()
                    break  # Execute once when condition is met
                await asyncio.sleep(check_interval_seconds)

        return self.schedule_task(
            name=name,
            coroutine_factory=conditional_wrapper,
            priority=priority,
            task_type=TaskType.CONDITIONAL,
            condition=condition,
            **kwargs,
        )

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Cancel running asyncio task if exists
        if task.asyncio_task and not task.asyncio_task.done():
            task.asyncio_task.cancel()

        # Remove from queue
        if task_id in self._running_tasks:
            del self._running_tasks[task_id]

        # Update state
        task.state = TaskState.CANCELLED

        logger.debug(f"❌ Cancelled task '{task.name}' (ID: {task_id[:8]})")
        return True

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            "id": task.id,
            "name": task.name,
            "priority": task.priority.name,
            "type": task.task_type.value,
            "state": task.state.value,
            "metrics": {
                "execution_count": task.metrics.execution_count,
                "total_runtime": task.metrics.total_runtime,
                "average_runtime": task.metrics.average_runtime,
                "failure_count": task.metrics.failure_count,
                "last_error": task.metrics.last_error,
            },
            "next_execution": (
                task.next_execution.isoformat() if task.next_execution else None
            ),
        }

    def get_scheduler_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scheduler metrics"""
        total_tasks = len(self.tasks)
        running_tasks = len(self._running_tasks)

        # Count tasks by state
        state_counts = {}
        priority_counts = {}

        for task in self.tasks.values():
            state_counts[task.state.value] = state_counts.get(task.state.value, 0) + 1
            priority_counts[task.priority.name] = (
                priority_counts.get(task.priority.name, 0) + 1
            )

        uptime = None
        if self.scheduler_start_time:
            uptime = (datetime.now() - self.scheduler_start_time).total_seconds()

        return {
            "scheduler": {
                "running": self._running,
                "uptime_seconds": uptime,
                "total_tasks": total_tasks,
                "running_tasks": running_tasks,
                "max_concurrent": self.max_concurrent_tasks,
                "total_executed": self.total_tasks_executed,
                "total_execution_time": self.total_execution_time,
            },
            "system_load": {
                "cpu_percent": self.system_load.cpu_percent,
                "memory_percent": self.system_load.memory_percent,
                "overall_load": self.system_load.overall_load,
            },
            "task_distribution": {
                "by_state": state_counts,
                "by_priority": priority_counts,
            },
            "configuration": {
                "load_adaptation_enabled": self.load_adaptation_enabled,
                "preemption_enabled": self.preemption_enabled,
                "max_load_threshold": self.max_load_threshold,
            },
        }

    async def start(self):
        """Start the scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self.scheduler_start_time = datetime.now()
        self._scheduler_loop = asyncio.get_event_loop()

        logger.info("🚀 Priority Scheduler starting...")

        # Start system load monitoring
        self._load_monitor_task = asyncio.create_task(self._monitor_system_load())

        # Start main scheduler loop
        self._scheduler_task = asyncio.create_task(self._scheduler_loop_func())

        logger.info("✅ Priority Scheduler started")

    async def stop(self, timeout: float = 30.0):
        """Stop the scheduler gracefully"""
        if not self._running:
            return

        logger.info("🛑 Stopping Priority Scheduler...")
        self._running = False

        # Cancel all running tasks
        for task_id in list(self._running_tasks.keys()):
            self.cancel_task(task_id)

        # Stop monitoring
        if self._load_monitor_task:
            self._load_monitor_task.cancel()
            try:
                await asyncio.wait_for(self._load_monitor_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        # Stop scheduler loop
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await asyncio.wait_for(self._scheduler_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        logger.info("✅ Priority Scheduler stopped")

    async def _scheduler_loop_func(self):
        """Main scheduler loop"""
        while self._running:
            try:
                await self._scheduler_cycle()
                await asyncio.sleep(0.1)  # 10 cycles per second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler cycle error: {e}")
                await asyncio.sleep(1.0)

    async def _scheduler_cycle(self):
        """Single scheduler cycle - select and execute tasks"""
        current_time = datetime.now()

        # Clean up completed tasks
        self._cleanup_completed_tasks()

        # Check if we can start new tasks
        if len(self._running_tasks) >= self.max_concurrent_tasks:
            return  # At capacity

        # Apply load-based throttling
        if self._should_throttle():
            return

        # Find next task to execute (priority-based)
        next_task = self._get_next_ready_task(current_time)
        if next_task:
            await self._execute_task(next_task)

    def _get_next_ready_task(self, current_time: datetime) -> Optional[SchedulerTask]:
        """Get the next ready task based on priority and timing"""

        # Check each priority level from highest to lowest
        for priority in TaskPriority:
            queue = self.task_queues[priority]

            # Look through the priority queue
            for _ in range(len(queue)):
                task_id = queue.popleft()

                if task_id not in self.tasks:
                    continue  # Task was removed

                task = self.tasks[task_id]

                # Skip if not ready to execute
                if task.next_execution and current_time < task.next_execution:
                    queue.append(task_id)  # Put back in queue
                    continue

                # Skip if already running
                if task.state == TaskState.RUNNING:
                    queue.append(task_id)  # Put back in queue
                    continue

                # Skip if cancelled or failed permanently
                if task.state in [TaskState.CANCELLED, TaskState.FAILED]:
                    continue  # Don't put back in queue

                # Check conditional tasks
                if task.task_type == TaskType.CONDITIONAL:
                    if task.condition and not task.condition():
                        queue.append(task_id)  # Put back in queue
                        continue

                # This task is ready to run
                # For periodic tasks, schedule next execution
                if task.task_type == TaskType.PERIODIC and task.interval_seconds:
                    task.next_execution = current_time + timedelta(
                        seconds=task.interval_seconds
                    )
                    queue.append(task_id)  # Put back for next cycle

                return task

        return None

    async def _execute_task(self, task: SchedulerTask):
        """Execute a single task"""
        task_start = time.time()
        task.state = TaskState.RUNNING
        task.metrics.started_at = datetime.now()

        logger.debug(
            f"🏃 Executing task '{task.name}' (Priority: {task.priority.name})"
        )

        try:
            # Create coroutine and wrap with timeout if specified
            coro = task.coroutine_factory()

            if task.max_runtime_seconds:
                coro = asyncio.wait_for(coro, timeout=task.max_runtime_seconds)

            # Execute the task
            asyncio_task = asyncio.create_task(coro)
            task.asyncio_task = asyncio_task
            self._running_tasks[task.id] = asyncio_task

            # Wait for completion (non-blocking for scheduler)
            asyncio.create_task(
                self._handle_task_completion(task, asyncio_task, task_start)
            )

        except Exception as e:
            await self._handle_task_error(task, e, task_start)

    async def _handle_task_completion(
        self, task: SchedulerTask, asyncio_task: asyncio.Task, start_time: float
    ):
        """Handle task completion (success or failure)"""
        try:
            await asyncio_task

            # Task completed successfully
            runtime = time.time() - start_time
            task.state = TaskState.COMPLETED
            task.metrics.completed_at = datetime.now()
            task.metrics.execution_count += 1
            task.metrics.total_runtime += runtime
            task.metrics.last_runtime = runtime
            task.metrics.average_runtime = (
                task.metrics.total_runtime / task.metrics.execution_count
            )

            self.total_tasks_executed += 1
            self.total_execution_time += runtime

            logger.debug(f"✅ Task '{task.name}' completed ({runtime:.2f}s)")

        except asyncio.CancelledError:
            task.state = TaskState.CANCELLED
            logger.debug(f"❌ Task '{task.name}' was cancelled")

        except Exception as e:
            await self._handle_task_error(task, e, start_time)

        finally:
            # Cleanup
            if task.id in self._running_tasks:
                del self._running_tasks[task.id]
            task.asyncio_task = None

    async def _handle_task_error(
        self, task: SchedulerTask, error: Exception, start_time: float
    ):
        """Handle task execution error"""
        runtime = time.time() - start_time
        task.metrics.failure_count += 1
        task.metrics.last_error = str(error)
        task.metrics.last_runtime = runtime

        logger.warning(f"⚠️ Task '{task.name}' failed: {error}")

        # Check if we should retry
        if task.metrics.failure_count < task.max_retries:
            task.state = TaskState.PENDING
            # Add delay before retry
            task.next_execution = datetime.now() + timedelta(
                seconds=2**task.metrics.failure_count
            )
            logger.debug(
                f"🔄 Retrying task '{task.name}' (attempt {task.metrics.failure_count + 1})"
            )
        else:
            task.state = TaskState.FAILED
            logger.error(
                f"💥 Task '{task.name}' failed permanently after {task.max_retries} retries"
            )

    def _cleanup_completed_tasks(self):
        """Clean up completed one-shot tasks and remove from queues"""
        to_remove = []

        for task_id, task in self.tasks.items():
            # Remove completed one-shot tasks
            if task.task_type == TaskType.ONESHOT and task.state == TaskState.COMPLETED:
                to_remove.append(task_id)
            # Remove permanently failed tasks
            elif task.state == TaskState.FAILED:
                to_remove.append(task_id)
            # Remove cancelled tasks
            elif task.state == TaskState.CANCELLED:
                to_remove.append(task_id)

        for task_id in to_remove:
            # Also remove from queues to prevent memory leaks/re-execution attempts
            task = self.tasks[task_id]
            if task.priority in self.task_queues:
                try:
                    self.task_queues[task.priority].remove(task_id)
                except ValueError:
                    pass  # Task might not be in queue if running/already removed

            # Remove from tracking dict
            del self.tasks[task_id]
            logger.debug(f"🧹 Cleaned up task '{task.name}' ({task_id[:8]})")

    def _should_throttle(self) -> bool:
        """Check if scheduler should throttle due to system load"""
        if not self.load_adaptation_enabled:
            return False

        return self.system_load.overall_load > self.max_load_threshold

    async def _monitor_system_load(self):
        """Monitor system load continuously"""
        while self._running:
            try:
                # Get CPU and memory usage
                self.system_load.cpu_percent = psutil.cpu_percent(interval=None)
                self.system_load.memory_percent = psutil.virtual_memory().percent

                # Log high load conditions
                if self.system_load.overall_load > 0.8:
                    logger.warning(
                        f"🔥 High system load: CPU={self.system_load.cpu_percent:.1f}% RAM={self.system_load.memory_percent:.1f}%"
                    )

                await asyncio.sleep(2.0)  # Update every 2 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System load monitoring error: {e}")
                await asyncio.sleep(5.0)


# Global instance
priority_scheduler = PriorityScheduler()

if __name__ == "__main__":
    # Test the scheduler
    async def test_scheduler():
        print("🧪 Testing Priority Scheduler")
        print("=" * 50)

        # Test tasks of different priorities
        async def high_priority_task():
            print("🔴 High priority task running")
            await asyncio.sleep(1)
            print("🔴 High priority task done")

        async def normal_task():
            print("🟡 Normal task running")
            await asyncio.sleep(2)
            print("🟡 Normal task done")

        async def low_priority_task():
            print("🟢 Low priority task running")
            await asyncio.sleep(0.5)
            print("🟢 Low priority task done")

        # Schedule tasks
        priority_scheduler.schedule_task(
            "high_task", high_priority_task, TaskPriority.HIGH
        )
        priority_scheduler.schedule_task(
            "normal_task", normal_task, TaskPriority.NORMAL
        )
        priority_scheduler.schedule_task(
            "low_task", low_priority_task, TaskPriority.LOW
        )

        # Schedule periodic task
        async def periodic_task():
            print("🔄 Periodic task executed")

        priority_scheduler.schedule_periodic(
            "periodic_test", periodic_task, 3.0, TaskPriority.NORMAL
        )

        # Start scheduler
        await priority_scheduler.start()

        # Run for a while
        await asyncio.sleep(10)

        # Show metrics
        print("\n📊 Scheduler Metrics:")
        metrics = priority_scheduler.get_scheduler_metrics()
        for key, value in metrics.items():
            print(f"{key}: {value}")

        # Stop scheduler
        await priority_scheduler.stop()

        print("✅ Test completed")

    asyncio.run(test_scheduler())
