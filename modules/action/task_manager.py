"""
Gerenciador de Tarefas (Agenda, Alarmes, Lembretes)
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from core.logger import logger

class TaskManager:
    """
    Gerenciador de tarefas, alarmes e lembretes.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Inicializa o gerenciador de tarefas.
        
        Args:
            storage_path: Caminho para armazenar tarefas (padrão: ./data/tasks.json)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path("./data/tasks.json")
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks = self._load_tasks()
        
        logger.info(f"TaskManager inicializado - {len(self.tasks)} tarefas carregadas")
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Carrega tarefas do arquivo."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar tarefas: {e}")
        return []
    
    def _save_tasks(self):
        """Salva tarefas no arquivo."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar tarefas: {e}")
    
    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Adiciona uma nova tarefa.
        
        Args:
            title: Título da tarefa
            description: Descrição opcional
            due_date: Data limite (formato ISO ou relativo)
            priority: "low", "medium", "high"
        
        Returns:
            Resultado da operação
        """
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "created": datetime.now().isoformat(),
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }
        
        self.tasks.append(task)
        self._save_tasks()
        
        logger.info(f"Tarefa adicionada: {title}")
        
        return {
            "success": True,
            "action": "Adicionar tarefa",
            "result": f"Tarefa '{title}' adicionada com sucesso!",
            "task": task
        }
    
    def set_alarm(self, time: str, message: str, repeat: bool = False) -> Dict[str, Any]:
        """
        Define um alarme.
        
        Args:
            time: Hora do alarme (formato HH:MM ou ISO)
            message: Mensagem do alarme
            repeat: Se deve repetir
        
        Returns:
            Resultado da operação
        """
        alarm = {
            "id": len([t for t in self.tasks if t.get("type") == "alarm"]) + 1,
            "type": "alarm",
            "time": time,
            "message": message,
            "repeat": repeat,
            "active": True,
            "created": datetime.now().isoformat()
        }
        
        self.tasks.append(alarm)
        self._save_tasks()
        
        logger.info(f"Alarme definido: {time} - {message}")
        
        return {
            "success": True,
            "action": "Definir alarme",
            "result": f"Alarme definido para {time}: {message}",
            "alarm": alarm
        }
    
    def list_tasks(self, filter_completed: bool = False) -> Dict[str, Any]:
        """
        Lista tarefas.
        
        Args:
            filter_completed: Se True, mostra apenas não completadas
        
        Returns:
            Lista de tarefas
        """
        tasks = self.tasks
        if filter_completed:
            tasks = [t for t in tasks if not t.get("completed", False)]
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Marca tarefa como completada.
        
        Args:
            task_id: ID da tarefa
        
        Returns:
            Resultado da operação
        """
        for task in self.tasks:
            if task.get("id") == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                
                return {
                    "success": True,
                    "action": "Completar tarefa",
                    "result": f"Tarefa '{task['title']}' marcada como completada!",
                    "task": task
                }
        
        return {
            "success": False,
            "error": f"Tarefa com ID {task_id} não encontrada"
        }
    
    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Remove uma tarefa.
        
        Args:
            task_id: ID da tarefa
        
        Returns:
            Resultado da operação
        """
        for i, task in enumerate(self.tasks):
            if task.get("id") == task_id:
                removed = self.tasks.pop(i)
                self._save_tasks()
                
                return {
                    "success": True,
                    "action": "Remover tarefa",
                    "result": f"Tarefa '{removed['title']}' removida!",
                    "task": removed
                }
        
        return {
            "success": False,
            "error": f"Tarefa com ID {task_id} não encontrada"
        }
    
    def get_upcoming_tasks(self, days: int = 7) -> Dict[str, Any]:
        """
        Obtém tarefas próximas.
        
        Args:
            days: Número de dias a frente
        
        Returns:
            Lista de tarefas próximas
        """
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        
        upcoming = []
        for task in self.tasks:
            if task.get("completed", False):
                continue
            
            due_date = task.get("due_date")
            if due_date:
                try:
                    if isinstance(due_date, str):
                        due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    else:
                        due = due_date
                    
                    if now <= due <= cutoff:
                        upcoming.append(task)
                except Exception:
                    pass
        
        return {
            "success": True,
            "upcoming": sorted(upcoming, key=lambda t: t.get("due_date", "")),
            "count": len(upcoming)
        }

