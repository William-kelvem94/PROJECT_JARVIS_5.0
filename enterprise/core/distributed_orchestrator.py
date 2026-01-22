"""
Distributed Orchestrator - Orquestração Distribuída com Saga Pattern
Gerencia comandos complexos distribuídos entre múltiplos serviços
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from core.logger import logger
from enterprise.core.event_bus import EventBus, Event, EventType
from enterprise.core.service_registry import ServiceRegistry

class SagaStatus(Enum):
    """Status de uma Saga."""
    PENDING = "pending"
    RUNNING = "running"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SagaStep:
    """Passo de uma Saga."""
    id: str
    service: str
    action: str
    payload: Dict[str, Any]
    compensate_action: Optional[str] = None
    compensate_payload: Optional[Dict[str, Any]] = None
    completed: bool = False
    failed: bool = False

@dataclass
class Command:
    """Comando a ser executado."""
    id: str
    type: str
    payload: Dict[str, Any]
    source: str

@dataclass
class CommandResult:
    """Resultado de execução de comando."""
    command_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    steps_completed: List[str] = None

class CommandSaga:
    """
    Saga para executar comandos distribuídos.
    Implementa padrão Saga para transações distribuídas.
    """
    
    def __init__(
        self,
        command: Command,
        steps: List[SagaStep],
        event_bus: EventBus,
        service_registry: ServiceRegistry
    ):
        """
        Inicializa Saga.
        
        Args:
            command: Comando a executar
            steps: Passos da Saga
            event_bus: Event Bus para comunicação
            service_registry: Registry para descoberta de serviços
        """
        self.command = command
        self.steps = steps
        self.event_bus = event_bus
        self.service_registry = service_registry
        self.status = SagaStatus.PENDING
        self.results: Dict[str, Any] = {}
        
        logger.info(f"Saga criada para comando {command.id} com {len(steps)} passos")
    
    async def execute(self) -> CommandResult:
        """
        Executa a Saga.
        
        Returns:
            Resultado do comando
        """
        self.status = SagaStatus.RUNNING
        
        try:
            # Executar passos em ordem
            for step in self.steps:
                logger.info(f"Executando passo {step.id} da Saga")
                
                # Obter URL do serviço
                service_url = self.service_registry.get_service_url(
                    step.service,
                    step.action
                )
                
                if not service_url:
                    raise Exception(f"Serviço {step.service} não encontrado")
                
                # Criar evento de comando
                command_event = Event(
                    id=str(uuid.uuid4()),
                    type=EventType.COMMAND,
                    source="orchestrator",
                    destination=step.service,
                    payload={
                        "command_id": self.command.id,
                        "step_id": step.id,
                        "action": step.action,
                        "payload": step.payload
                    },
                    timestamp=asyncio.get_event_loop().time(),
                    correlation_id=self.command.id
                )
                
                # Enviar comando e aguardar resposta
                response = await self.event_bus.request(
                    command_event,
                    f"commands.{step.service}",
                    timeout=30.0
                )
                
                if not response:
                    raise Exception(f"Timeout executando passo {step.id}")
                
                if response.type == EventType.ERROR:
                    # Erro no passo, iniciar compensação
                    logger.error(f"Erro no passo {step.id}: {response.payload}")
                    await self._compensate(up_to_step=step.id)
                    self.status = SagaStatus.FAILED
                    return CommandResult(
                        command_id=self.command.id,
                        success=False,
                        result=None,
                        error=response.payload.get("error", "Erro desconhecido")
                    )
                
                # Passo completado
                step.completed = True
                self.results[step.id] = response.payload
                logger.info(f"Passo {step.id} completado")
            
            # Todos os passos completados
            self.status = SagaStatus.COMPLETED
            
            return CommandResult(
                command_id=self.command.id,
                success=True,
                result=self.results,
                steps_completed=[s.id for s in self.steps if s.completed]
            )
            
        except Exception as e:
            logger.error(f"Erro executando Saga: {e}")
            await self._compensate()
            self.status = SagaStatus.FAILED
            
            return CommandResult(
                command_id=self.command.id,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _compensate(self, up_to_step: Optional[str] = None):
        """
        Compensa transações já executadas (rollback).
        
        Args:
            up_to_step: ID do passo até onde compensar (None = todos)
        """
        self.status = SagaStatus.COMPENSATING
        
        # Compensar em ordem reversa
        steps_to_compensate = reversed(self.steps)
        
        for step in steps_to_compensate:
            if up_to_step and step.id == up_to_step:
                break
            
            if not step.completed:
                continue
            
            if not step.compensate_action:
                logger.warning(f"Sem ação de compensação para passo {step.id}")
                continue
            
            logger.info(f"Compensando passo {step.id}")
            
            try:
                service_url = self.service_registry.get_service_url(
                    step.service,
                    step.compensate_action
                )
                
                if service_url:
                    compensate_event = Event(
                        id=str(uuid.uuid4()),
                        type=EventType.COMMAND,
                        source="orchestrator",
                        destination=step.service,
                        payload={
                            "command_id": self.command.id,
                            "step_id": step.id,
                            "action": step.compensate_action,
                            "payload": step.compensate_payload or step.payload
                        },
                        timestamp=datetime.now(),
                        correlation_id=self.command.id
                    )
                    
                    await self.event_bus.publish(
                        compensate_event,
                        f"commands.{step.service}"
                    )
                    
                    logger.info(f"Compensação do passo {step.id} enviada")
                    
            except Exception as e:
                logger.error(f"Erro compensando passo {step.id}: {e}")

class DistributedOrchestrator:
    """
    Orquestrador distribuído para gerenciar comandos complexos.
    """
    
    def __init__(
        self,
        event_bus: EventBus,
        service_registry: ServiceRegistry
    ):
        """
        Inicializa orquestrador distribuído.
        
        Args:
            event_bus: Event Bus para comunicação
            service_registry: Registry de serviços
        """
        self.event_bus = event_bus
        self.service_registry = service_registry
        self.active_sagas: Dict[str, CommandSaga] = {}
        
        logger.info("DistributedOrchestrator inicializado")
    
    async def process_command(self, command: Command) -> CommandResult:
        """
        Processa um comando distribuído.
        
        Args:
            command: Comando a processar
        
        Returns:
            Resultado do comando
        """
        # Criar steps da Saga baseado no tipo de comando
        steps = await self._create_saga_steps(command)
        
        if not steps:
            return CommandResult(
                command_id=command.id,
                success=False,
                result=None,
                error=f"Comando tipo {command.type} não suportado"
            )
        
        # Criar e executar Saga
        saga = CommandSaga(
            command=command,
            steps=steps,
            event_bus=self.event_bus,
            service_registry=self.service_registry
        )
        
        self.active_sagas[command.id] = saga
        
        try:
            result = await saga.execute()
            return result
        finally:
            # Limpar saga após execução
            if command.id in self.active_sagas:
                del self.active_sagas[command.id]
    
    async def _create_saga_steps(self, command: Command) -> List[SagaStep]:
        """
        Cria steps da Saga baseado no tipo de comando.
        
        Args:
            command: Comando
        
        Returns:
            Lista de steps
        """
        # Implementação básica - pode ser estendida
        steps = []
        
        if command.type == "open_app":
            steps.append(SagaStep(
                id="step1",
                service="automation-engine",
                action="/automation/open_app",
                payload=command.payload,
                compensate_action="/automation/close_app",
                compensate_payload=command.payload
            ))
        
        elif command.type == "complex_workflow":
            # Exemplo de workflow complexo
            steps.append(SagaStep(
                id="step1",
                service="data-pipeline",
                action="/pipeline/process",
                payload=command.payload.get("data", {})
            ))
            
            steps.append(SagaStep(
                id="step2",
                service="ai-engine",
                action="/ai/analyze",
                payload={"data": "{{step1.result}}"}  # Referência ao resultado anterior
            ))
            
            steps.append(SagaStep(
                id="step3",
                service="automation-engine",
                action="/automation/execute",
                payload={"analysis": "{{step2.result}}"}
            ))
        
        return steps

