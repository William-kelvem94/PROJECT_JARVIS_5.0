# -*- coding: utf-8 -*-
# src/learning/training_scheduler.py
import threading
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from ..utils.safe_execute import safe_execute

logger = logging.getLogger("JARVIS-TRAINING-SCHEDULER")

@dataclass
class TrainingTask:
    """Representa uma tarefa de treinamento agendada."""
    task_id: str
    dataset_path: Path
    model_name: str
    priority: int = 5  # 1-10, maior é mais prioritário
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    created_at: float = field(default_factory=lambda: time.time())
    retry_count: int = 0
    max_retries: int = 3

class TrainingQueue:
    """Fila de tarefas de treinamento com gerenciamento de prioridades."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.tasks: List[TrainingTask] = []
        self.lock = threading.Lock()
        self._task_counter = 0
    
    @safe_execute(default=False)
    def add_task(self, task: TrainingTask) -> bool:
        """Adiciona uma tarefa à fila."""
        with self.lock:
            if len(self.tasks) >= self.max_size:
                logger.warning(f"🚫 Fila cheia ({self.max_size} tarefas)")
                return False
                
            self.tasks.append(task)
            # Ordenar por prioridade (maior primeiro) e tempo de criação
            self.tasks.sort(key=lambda t: (-t.priority, t.created_at))
            
            logger.info(f"📝 Tarefa {task.task_id} adicionada (prioridade: {task.priority})")
            return True
    
    @safe_execute(default=None)
    def get_next_task(self) -> Optional[TrainingTask]:
        """Obtém a próxima tarefa prioritária."""
        with self.lock:
            pending_tasks = [t for t in self.tasks if t.status == "pending"]
            if not pending_tasks:
                return None
                
            task = pending_tasks[0]
            task.status = "running"
            return task
    
    @safe_execute()
    def mark_completed(self, task_id: str, success: bool = True):
        """Marca uma tarefa como concluída ou falha."""
        with self.lock:
            for task in self.tasks:
                if task.task_id == task_id:
                    if success:
                        task.status = "completed"
                        logger.info(f"✅ Tarefa {task_id} concluída")
                    else:
                        task.retry_count += 1
                        if task.retry_count >= task.max_retries:
                            task.status = "failed"
                            logger.error(f"❌ Tarefa {task_id} falhou após {task.retry_count} tentativas")
                        else:
                            task.status = "pending"  # Permitir retry
                            logger.warning(f"🔄 Tarefa {task_id} falhou, retry {task.retry_count}/{task.max_retries}")
                    break

class TrainingScheduler:
    """
    Agenda e gerencia tarefas de treinamento de forma assíncrona e thread-safe.
    """
    
    def __init__(self):
        self.queue = TrainingQueue()
        self.active_tasks: Dict[str, TrainingTask] = {}
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.is_running = False
        
    @safe_execute(default=False)
    def start_scheduler(self, training_callback: Callable):
        """Inicia o agendamento em background."""
        if self.is_running:
            logger.warning("⚠️ Agendador já está rodando")
            return False
            
        self.stop_event.clear()
        self.is_running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            args=(training_callback,),
            daemon=True,
            name="TrainingScheduler"
        )
        self.scheduler_thread.start()
        
        logger.info("🚀 Iniciando agendador de treinamento")
        return True
    
    @safe_execute()
    def stop_scheduler(self):
        """Para o agendamento."""
        if not self.is_running:
            return
            
        self.stop_event.set()
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
            logger.info("🛑 Agendador de treinamento parado")
    
    @safe_execute(default=False)
    def schedule_training(self, task_config: Dict[str, Any]) -> bool:
        """Agenda uma nova tarefa de treinamento."""
        task = TrainingTask(
            task_id=f"train_{int(time.time())}_{len(self.queue.tasks)}",
            dataset_path=Path(task_config["dataset_path"]),
            model_name=task_config["model_name"],
            priority=task_config.get("priority", 5),
            config=task_config.get("config", {})
        )
        
        return self.queue.add_task(task)
    
    def _scheduler_loop(self, training_callback: Callable):
        """Loop principal do agendador."""
        logger.info("🔄 Iniciando loop do agendador")
        
        while not self.stop_event.is_set() and self.is_running:
            try:
                # Obter próxima tarefa
                task = self.queue.get_next_task()
                if task:
                    logger.info(f"🎯 Executando tarefa: {task.task_id}")
                    
                    # Executar treinamento
                    success = training_callback(task)
                    
                    # Marcar como concluída/falha
                    self.queue.mark_completed(task.task_id, success)
                    
                    # Limpar tarefas concluídas periodicamente
                    self._cleanup_completed_tasks()
                
                # Esperar antes da próxima verificação
                self.stop_event.wait(10)  # Verificar a cada 10 segundos
                
            except Exception as e:
                logger.error(f"❌ Erro no loop do agendador: {e}")
                time.sleep(5)  # Espera antes de retry
    
    @safe_execute()
    def _cleanup_completed_tasks(self):
        """Limpa tarefas concluídas da fila."""
        with self.queue.lock:
            completed_count = len([t for t in self.queue.tasks if t.status in ["completed", "failed"]])
            if completed_count > 10:  # Limpar quando muitas tarefas concluídas
                self.queue.tasks = [t for t in self.queue.tasks if t.status == "pending"]
                logger.info(f"🧹 Limpas {completed_count} tarefas concluídas")
    
    @safe_execute(default={})
    def get_queue_status(self) -> Dict[str, Any]:
        """Retorna status atual da fila."""
        with self.queue.lock:
            status_counts = {}
            for task in self.queue.tasks:
                status_counts[task.status] = status_counts.get(task.status, 0) + 1
                
            return {
                'total_tasks': len(self.queue.tasks),
                'status_counts': status_counts,
                'is_running': self.is_running,
                'active_tasks': len(self.active_tasks)
            }
