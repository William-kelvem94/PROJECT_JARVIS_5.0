"""
Sistema de Carregamento Dinâmico de Skills
Permite adicionar skills sem modificar código principal
"""

import importlib
import os
import inspect
from typing import Dict, Any, Callable, Optional
from pathlib import Path
from core.logger import logger

class DynamicSkillLoader:
    """
    Carrega skills dinamicamente de um diretório.
    Skills devem seguir um padrão específico.
    """
    
    def __init__(self, skills_dir: str = "skills"):
        """
        Inicializa o loader de skills dinâmicas.
        
        Args:
            skills_dir: Diretório contendo skills (padrão: ./skills)
        """
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        self.loaded_skills: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"DynamicSkillLoader inicializado: {self.skills_dir}")
    
    def load_skills(self, reload: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Carrega todas as skills do diretório.
        
        Args:
            reload: Se True, recarrega skills já carregadas
        
        Returns:
            Dicionário com skills carregadas
        """
        if not reload and self.loaded_skills:
            return self.loaded_skills
        
        logger.info(f"Carregando skills de {self.skills_dir}")
        
        # Buscar arquivos Python no diretório
        skill_files = list(self.skills_dir.glob("*.py"))
        skill_files = [f for f in skill_files if not f.name.startswith("_")]
        
        for skill_file in skill_files:
            try:
                skill_info = self._load_skill_file(skill_file)
                if skill_info:
                    skill_name = skill_info["name"]
                    self.loaded_skills[skill_name] = skill_info
                    logger.info(f" Skill carregada: {skill_name}")
                    
            except Exception as e:
                logger.error(f" Erro ao carregar skill {skill_file.name}: {e}")
        
        logger.info(f"Total de skills carregadas: {len(self.loaded_skills)}")
        return self.loaded_skills
    
    def _load_skill_file(self, skill_file: Path) -> Optional[Dict[str, Any]]:
        """
        Carrega um arquivo de skill.
        
        Formato esperado:
        - Função async: skill_handler(message, params, context)
        - Variável: SKILL_NAME (nome da skill)
        - Variável: SKILL_DESCRIPTION (descrição opcional)
        
        Args:
            skill_file: Caminho do arquivo
        
        Returns:
            Informações da skill ou None
        """
        try:
            # Importar módulo
            module_name = skill_file.stem
            spec = importlib.util.spec_from_file_location(module_name, skill_file)
            
            if spec is None or spec.loader is None:
                logger.warning(f"Não foi possível carregar spec de {skill_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Buscar função de skill
            skill_handler = None
            skill_name = None
            skill_description = ""
            
            # Buscar SKILL_NAME
            if hasattr(module, "SKILL_NAME"):
                skill_name = module.SKILL_NAME
            elif hasattr(module, "skill_name"):
                skill_name = module.skill_name
            
            # Buscar SKILL_DESCRIPTION
            if hasattr(module, "SKILL_DESCRIPTION"):
                skill_description = module.SKILL_DESCRIPTION
            elif hasattr(module, "skill_description"):
                skill_description = module.skill_description
            
            # Buscar função handler
            # Procurar função com nome padrão
            if hasattr(module, "handle_skill"):
                skill_handler = module.handle_skill
            elif hasattr(module, "skill_handler"):
                skill_handler = module.skill_handler
            elif hasattr(module, "execute"):
                skill_handler = module.execute
            
            # Se não encontrou, buscar qualquer função async que não seja privada
            if skill_handler is None:
                for name, obj in inspect.getmembers(module, inspect.iscoroutinefunction):
                    if not name.startswith("_") and name not in ["main", "setup"]:
                        skill_handler = obj
                        if not skill_name:
                            skill_name = name
                        break
            
            # Se ainda não encontrou, buscar função sync
            if skill_handler is None:
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if not name.startswith("_") and name not in ["main", "setup"]:
                        # Verificar assinatura
                        sig = inspect.signature(obj)
                        params = list(sig.parameters.keys())
                        if len(params) >= 2:  # message, params pelo menos
                            skill_handler = obj
                            if not skill_name:
                                skill_name = name
                            break
            
            if skill_handler is None:
                logger.warning(f"Nenhum handler encontrado em {skill_file}")
                return None
            
            if not skill_name:
                skill_name = module_name
            
            # Verificar se função tem assinatura correta
            sig = inspect.signature(skill_handler)
            params = list(sig.parameters.keys())
            
            return {
                "name": skill_name,
                "description": skill_description,
                "handler": skill_handler,
                "file": str(skill_file),
                "is_async": inspect.iscoroutinefunction(skill_handler),
                "parameters": params
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar skill file {skill_file}: {e}")
            return None
    
    def register_skill(self, skill_name: str, handler: Callable, description: str = "") -> bool:
        """
        Registra uma skill manualmente.
        
        Args:
            skill_name: Nome da skill
            handler: Função handler
            description: Descrição opcional
        
        Returns:
            True se registrou com sucesso
        """
        try:
            self.loaded_skills[skill_name] = {
                "name": skill_name,
                "description": description,
                "handler": handler,
                "file": "manual",
                "is_async": inspect.iscoroutinefunction(handler),
                "parameters": list(inspect.signature(handler).parameters.keys())
            }
            logger.info(f"Skill registrada manualmente: {skill_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar skill {skill_name}: {e}")
            return False
    
    def get_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Obtém uma skill pelo nome."""
        return self.loaded_skills.get(skill_name)
    
    def list_skills(self) -> Dict[str, str]:
        """Lista todas as skills carregadas com descrições."""
        return {
            name: info.get("description", "Sem descrição")
            for name, info in self.loaded_skills.items()
        }
    
    def reload_skill(self, skill_name: str) -> bool:
        """
        Recarrega uma skill específica.
        
        Args:
            skill_name: Nome da skill
        
        Returns:
            True se recarregou com sucesso
        """
        skill_info = self.loaded_skills.get(skill_name)
        if not skill_info or skill_info.get("file") == "manual":
            logger.warning(f"Não é possível recarregar skill manual: {skill_name}")
            return False
        
        skill_file = Path(skill_info["file"])
        try:
            new_info = self._load_skill_file(skill_file)
            if new_info:
                self.loaded_skills[skill_name] = new_info
                logger.info(f"Skill recarregada: {skill_name}")
                return True
        except Exception as e:
            logger.error(f"Erro ao recarregar skill {skill_name}: {e}")
        
        return False

