"""
Task Decomposition Engine - Sistema de planejamento e execução de tarefas complexas
Decompõe tarefas complexas em etapas simples, executa e verifica resultados
"""

import json
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
from core.logger import logger


class TaskStatus(Enum):
    """Status de uma tarefa."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_VERIFICATION = "waiting_verification"


class Task:
    """Representa uma tarefa única."""
    
    def __init__(
        self,
        task_id: str,
        description: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        verification_func: Optional[Callable] = None
    ):
        self.task_id = task_id
        self.description = description
        self.action = action
        self.parameters = parameters or {}
        self.dependencies = dependencies or []
        self.verification_func = verification_func
        
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.attempts = 0
        self.max_attempts = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte tarefa para dicionário."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "action": self.action,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "attempts": self.attempts
        }


class TaskPlan:
    """Plano de execução de tarefas."""
    
    def __init__(self, plan_id: str, description: str):
        self.plan_id = plan_id
        self.description = description
        self.tasks: List[Task] = []
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
    
    def add_task(self, task: Task):
        """Adiciona tarefa ao plano."""
        self.tasks.append(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Recupera tarefa por ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_next_task(self) -> Optional[Task]:
        """Retorna próxima tarefa a executar."""
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Verificar se dependências foram completadas
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = self.get_task(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                return task
        
        return None
    
    def get_progress(self) -> Dict[str, Any]:
        """Retorna progresso do plano."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "percentage": (completed / total * 100) if total > 0 else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte plano para dicionário."""
        return {
            "plan_id": self.plan_id,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.get_progress()
        }


class TaskDecomposer:
    """
    Decompõe tarefas complexas em etapas executáveis.
    Usa LLM para analisar requisição e criar plano de ação.
    """
    
    def __init__(self, llm_client=None):
        """
        Inicializa o decompositor de tarefas.
        
        Args:
            llm_client: Cliente LLM para análise de tarefas
        """
        self.llm_client = llm_client
        logger.info("TaskDecomposer inicializado")
    
    def decompose(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """
        Decompõe requisição do usuário em plano de tarefas.
        
        Args:
            user_request: Requisição do usuário
            context: Contexto adicional
        
        Returns:
            Plano de tarefas
        """
        logger.info(f"Decompondo tarefa: {user_request}")
        
        # Criar plano
        plan_id = f"plan_{datetime.utcnow().timestamp()}"
        plan = TaskPlan(plan_id, user_request)
        
        # Usar LLM para decompor (se disponível)
        if self.llm_client:
            tasks = self._decompose_with_llm(user_request, context)
        else:
            tasks = self._decompose_simple(user_request)
        
        # Adicionar tarefas ao plano
        for task in tasks:
            plan.add_task(task)
        
        logger.info(f"Plano criado com {len(tasks)} tarefas")
        return plan
    
    def _decompose_with_llm(self, user_request: str, context: Optional[Dict[str, Any]]) -> List[Task]:
        """Decompõe usando LLM."""
        # Prompt para LLM
        prompt = f"""
Analise a seguinte requisição e decomponha em tarefas executáveis simples:

Requisição: {user_request}

Contexto: {json.dumps(context) if context else 'Nenhum'}

Retorne um JSON com lista de tarefas no formato:
{{
  "tasks": [
    {{
      "task_id": "task_1",
      "description": "Descrição da tarefa",
      "action": "nome_da_ação",
      "parameters": {{}},
      "dependencies": []
    }}
  ]
}}

Ações disponíveis: search, open_app, file_operation, send_message, set_reminder, system_command
"""
        
        try:
            # Chamar LLM
            response = self.llm_client.generate(prompt)
            
            # Parse JSON
            tasks_data = json.loads(response)
            
            # Criar objetos Task
            tasks = []
            for task_data in tasks_data.get("tasks", []):
                task = Task(
                    task_id=task_data["task_id"],
                    description=task_data["description"],
                    action=task_data["action"],
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", [])
                )
                tasks.append(task)
            
            return tasks
        
        except Exception as e:
            logger.error(f"Erro ao decompor com LLM: {e}")
            return self._decompose_simple(user_request)
    
    def _decompose_simple(self, user_request: str) -> List[Task]:
        """Decomposição simples baseada em regras."""
        tasks = []
        
        request_lower = user_request.lower()
        
        # Regras simples de decomposição
        if "enviar email" in request_lower or "send email" in request_lower:
            tasks.append(Task("task_1", "Abrir cliente de email", "open_app", {"app": "email"}))
            tasks.append(Task("task_2", "Compor email", "compose_email", {}, ["task_1"]))
            tasks.append(Task("task_3", "Enviar email", "send_email", {}, ["task_2"]))
        
        elif "agendar reunião" in request_lower or "schedule meeting" in request_lower:
            tasks.append(Task("task_1", "Abrir calendário", "open_app", {"app": "calendar"}))
            tasks.append(Task("task_2", "Criar evento", "create_event", {}, ["task_1"]))
            tasks.append(Task("task_3", "Enviar convites", "send_invites", {}, ["task_2"]))
        
        elif "pesquisar" in request_lower or "search" in request_lower:
            tasks.append(Task("task_1", "Pesquisar informação", "web_search", {"query": user_request}))
            tasks.append(Task("task_2", "Processar resultados", "process_results", {}, ["task_1"]))
        
        else:
            # Tarefa genérica
            tasks.append(Task("task_1", user_request, "generic_action", {"request": user_request}))
        
        return tasks


class TaskExecutor:
    """
    Executor de tarefas.
    Executa tarefas do plano e verifica resultados.
    """
    
    def __init__(self, action_handlers: Optional[Dict[str, Callable]] = None):
        """
        Inicializa o executor.
        
        Args:
            action_handlers: Mapa de ações para handlers
        """
        self.action_handlers = action_handlers or {}
        self.current_plan: Optional[TaskPlan] = None
        logger.info("TaskExecutor inicializado")
    
    def register_handler(self, action: str, handler: Callable):
        """
        Registra handler para uma ação.
        
        Args:
            action: Nome da ação
            handler: Função handler
        """
        self.action_handlers[action] = handler
        logger.debug(f"Handler registrado para ação: {action}")
    
    def execute_plan(self, plan: TaskPlan) -> bool:
        """
        Executa plano de tarefas.
        
        Args:
            plan: Plano a executar
        
        Returns:
            True se todas as tarefas foram completadas com sucesso
        """
        self.current_plan = plan
        plan.started_at = datetime.utcnow()
        
        logger.info(f"Executando plano: {plan.plan_id} ({len(plan.tasks)} tarefas)")
        
        # Executar tarefas sequencialmente respeitando dependências
        while True:
            next_task = plan.get_next_task()
            
            if not next_task:
                # Verificar se há tarefas pendentes (esperando dependências)
                pending = [t for t in plan.tasks if t.status == TaskStatus.PENDING]
                if pending:
                    logger.error("Tarefas pendentes com dependências não satisfeitas")
                    return False
                break
            
            # Executar tarefa
            success = self.execute_task(next_task)
            
            if not success:
                logger.error(f"Falha ao executar tarefa: {next_task.task_id}")
                # Continuar ou parar?
                # Por enquanto, continuar com outras tarefas
        
        plan.completed_at = datetime.utcnow()
        
        # Verificar sucesso geral
        all_completed = all(t.status == TaskStatus.COMPLETED for t in plan.tasks)
        logger.info(f"Plano finalizado - Sucesso: {all_completed}")
        
        return all_completed
    
    def execute_task(self, task: Task) -> bool:
        """
        Executa uma tarefa individual.
        
        Args:
            task: Tarefa a executar
        
        Returns:
            True se executada com sucesso
        """
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        task.attempts += 1
        
        logger.info(f"Executando tarefa: {task.task_id} - {task.description}")
        
        try:
            # Obter handler para ação
            handler = self.action_handlers.get(task.action)
            
            if not handler:
                logger.warning(f"Handler não encontrado para ação: {task.action}")
                task.status = TaskStatus.FAILED
                task.error = f"Handler não encontrado: {task.action}"
                return False
            
            # Executar handler
            result = handler(task.parameters)
            
            # Verificar resultado
            if task.verification_func:
                verified = task.verification_func(result)
                if not verified:
                    task.status = TaskStatus.FAILED
                    task.error = "Verificação falhou"
                    logger.warning(f"Verificação falhou para tarefa: {task.task_id}")
                    return False
            
            # Sucesso
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Tarefa completada: {task.task_id}")
            return True
        
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Erro ao executar tarefa {task.task_id}: {e}")
            return False
    
    def get_plan_status(self) -> Optional[Dict[str, Any]]:
        """Retorna status do plano atual."""
        if not self.current_plan:
            return None
        
        return self.current_plan.to_dict()
