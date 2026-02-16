"""
Workflow Engine - Sistema de AutomaÃ§Ã£o Inteligente
Permite criar, gravar e executar workflows complexos
"""

import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """Representa um passo em um workflow"""
    type: str  # click, type, key, hotkey, wait, open_app, etc
    params: Dict[str, Any]
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        return cls(**data)

@dataclass
class Workflow:
    """Representa um workflow completo"""
    name: str
    description: str
    steps: List[WorkflowStep]
    created_at: str
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at,
            "tags": self.tags or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        steps = [WorkflowStep.from_dict(s) for s in data.get('steps', [])]
        return cls(
            name=data['name'],
            description=data['description'],
            steps=steps,
            created_at=data['created_at'],
            tags=data.get('tags', [])
        )

class WorkflowEngine:
    """Engine para criar e executar workflows"""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(exist_ok=True)
        self.workflows: Dict[str, Workflow] = {}
        self.load_all_workflows()
        
        # Callbacks para executar aÃ§Ãµes
        self.action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Registra handlers padrÃ£o para aÃ§Ãµes comuns"""
        from src.core.actions.advanced_action_controller import advanced_action_controller
        
        self.action_handlers = {
            'click': lambda params: advanced_action_controller.click(**params),
            'type': lambda params: advanced_action_controller.type_text(**params),
            'key': lambda params: advanced_action_controller.press_key(**params),
            'hotkey': lambda params: advanced_action_controller.hotkey(*params.get('keys', [])),
            'wait': lambda params: time.sleep(params.get('duration', 1)),
            'open_app': lambda params: advanced_action_controller.open_application(params.get('app_name')),
            'close_app': lambda params: advanced_action_controller.close_application(params.get('app_name')),
        }
    
    def create_workflow(self, name: str, description: str, tags: List[str] = None) -> Workflow:
        """Cria um novo workflow vazio"""
        workflow = Workflow(
            name=name,
            description=description,
            steps=[],
            created_at=datetime.now().isoformat(),
            tags=tags or []
        )
        self.workflows[name] = workflow
        logger.info(f"âœ… Workflow criado: {name}")
        return workflow
    
    def add_step(self, workflow_name: str, step: WorkflowStep):
        """Adiciona um passo a um workflow"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow nÃ£o encontrado: {workflow_name}")
        
        self.workflows[workflow_name].steps.append(step)
        logger.info(f"âœ… Passo adicionado ao workflow {workflow_name}: {step.type}")
    
    def execute_workflow(self, workflow_name: str, on_progress: Callable[[str], None] = None) -> bool:
        """Executa um workflow"""
        if workflow_name not in self.workflows:
            logger.error(f"âŒ Workflow nÃ£o encontrado: {workflow_name}")
            return False
        
        workflow = self.workflows[workflow_name]
        logger.info(f"ðŸš€ Executando workflow: {workflow_name} ({len(workflow.steps)} passos)")
        
        if on_progress:
            on_progress(f"Iniciando workflow: {workflow_name}")
        
        try:
            for i, step in enumerate(workflow.steps, 1):
                logger.info(f"Passo {i}/{len(workflow.steps)}: {step.type} - {step.description}")
                
                if on_progress:
                    on_progress(f"Passo {i}/{len(workflow.steps)}: {step.description or step.type}")
                
                # Executar aÃ§Ã£o
                handler = self.action_handlers.get(step.type)
                if handler:
                    result = handler(step.params)
                    if result is False:
                        logger.warning(f"âš ï¸ Passo falhou: {step.type}")
                else:
                    logger.warning(f"âš ï¸ Handler nÃ£o encontrado para: {step.type}")
                
                # Pequeno delay entre passos
                time.sleep(0.1)
            
            logger.info(f"âœ… Workflow concluÃ­do: {workflow_name}")
            if on_progress:
                on_progress(f"Workflow concluÃ­do: {workflow_name}")
            return True
            
        except Exception as e:
            logger.error(f"âŒ Erro ao executar workflow: {e}")
            if on_progress:
                on_progress(f"Erro: {str(e)}")
            return False
    
    def save_workflow(self, workflow_name: str):
        """Salva um workflow em arquivo JSON"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow nÃ£o encontrado: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        file_path = self.workflows_dir / f"{workflow_name}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"âœ… Workflow salvo: {file_path}")
    
    def load_workflow(self, workflow_name: str) -> Optional[Workflow]:
        """Carrega um workflow de arquivo JSON"""
        file_path = self.workflows_dir / f"{workflow_name}.json"
        
        if not file_path.exists():
            logger.warning(f"âš ï¸ Arquivo nÃ£o encontrado: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            workflow = Workflow.from_dict(data)
            self.workflows[workflow_name] = workflow
            logger.info(f"âœ… Workflow carregado: {workflow_name}")
            return workflow
            
        except Exception as e:
            logger.error(f"âŒ Erro ao carregar workflow: {e}")
            return None
    
    def load_all_workflows(self):
        """Carrega todos os workflows do diretÃ³rio"""
        for file_path in self.workflows_dir.glob("*.json"):
            workflow_name = file_path.stem
            self.load_workflow(workflow_name)
        
        logger.info(f"âœ… {len(self.workflows)} workflows carregados")
    
    def list_workflows(self) -> List[str]:
        """Lista todos os workflows disponÃ­veis"""
        return list(self.workflows.keys())
    
    def delete_workflow(self, workflow_name: str):
        """Deleta um workflow"""
        if workflow_name in self.workflows:
            del self.workflows[workflow_name]
        
        file_path = self.workflows_dir / f"{workflow_name}.json"
        if file_path.exists():
            file_path.unlink()
        
        logger.info(f"âœ… Workflow deletado: {workflow_name}")


# InstÃ¢ncia global
# Alterado para usar data/workflows e manter a raiz limpa
workflow_engine = WorkflowEngine(workflows_dir="data/workflows")


# Exemplo de workflow prÃ©-definido
def create_example_workflows():
    """Cria workflows de exemplo"""
    
    # Workflow 1: Abrir navegador e pesquisar
    wf1 = workflow_engine.create_workflow(  # noqa: F841
        name="pesquisar_google",
        description="Abre Chrome e faz uma pesquisa no Google",
        tags=["navegador", "pesquisa"]
    )
    
    workflow_engine.add_step("pesquisar_google", WorkflowStep(
        type="open_app",
        params={"app_name": "chrome"},
        description="Abrir Google Chrome"
    ))
    
    workflow_engine.add_step("pesquisar_google", WorkflowStep(
        type="wait",
        params={"duration": 2},
        description="Aguardar carregamento"
    ))
    
    workflow_engine.add_step("pesquisar_google", WorkflowStep(
        type="hotkey",
        params={"keys": ["ctrl", "l"]},
        description="Focar na barra de endereÃ§o"
    ))
    
    workflow_engine.add_step("pesquisar_google", WorkflowStep(
        type="type",
        params={"text": "JARVIS AI assistant"},
        description="Digitar pesquisa"
    ))
    
    workflow_engine.add_step("pesquisar_google", WorkflowStep(
        type="key",
        params={"key": "enter"},
        description="Executar pesquisa"
    ))
    
    workflow_engine.save_workflow("pesquisar_google")
    logger.info("âœ… Workflow de exemplo criado: pesquisar_google")


if __name__ == "__main__":
    create_example_workflows()
    print("Workflows disponÃ­veis:", workflow_engine.list_workflows())
