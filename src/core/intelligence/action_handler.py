"""
JARVIS 5.0 - Action Handler
============================
CORREÇÃO P2: Separação do God Object AIAgent

RESPONSABILIDADE:
  Gerenciar todas as AÇÕES do sistema:
  - Parsing de ações (JSON ou regex legado)
  - Execução via ActionExecutor
  - Validação de segurança
  - Web search, file I/O, system commands

ARQUITETURA:
  AIAgent (Orquestrador)
    ↓
  PerceptionEngine
  DecisionEngine
  ActionHandler ← ESTE MÓDULO
"""

import logging
import asyncio
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiofiles
import os

logger = logging.getLogger(__name__)

# ============================================================================
# SAFE IMPORTS
# ============================================================================
try:
    from src.core.intelligence.action_executor import get_action_executor, ActionExecutor
    from src.core.intelligence.structured_output import ActionUnion
    ACTION_EXECUTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ action_executor não disponível: {e}")
    get_action_executor = None
    ActionExecutor = None
    ActionUnion = None
    ACTION_EXECUTOR_AVAILABLE = False

try:
    from src.utils.web_search_tool import web_search_tool
    WEB_SEARCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ web_search_tool não disponível: {e}")
    web_search_tool = None
    WEB_SEARCH_AVAILABLE = False

try:
    from src.utils.security_manager import security_manager
    SECURITY_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ security_manager não disponível: {e}")
    security_manager = None
    SECURITY_MANAGER_AVAILABLE = False


class ActionHandler:
    """
    Manipulador de Ações - Executa ações estruturadas ou legadas
    
    CAPABILITIES:
      1. Structured Actions: Executa via ActionExecutor (P1)
      2. Legacy Actions: Regex parsing [ACTION: ...]
      3. Security Validation: Valida cada ação antes de executar
      4. Web Search: Integração com web_search_tool
      5. File I/O: Read/Write/List com sandboxing
    
    USAGE:
      handler = ActionHandler()
      results = await handler.execute_actions(parsed.actions)
      # results = [
      #     {"status": "success", "action": "type_text", "result": "..."},
      #     ...
      # ]
    """
    
    def __init__(self):
        """Inicializa action handler"""
        self.executor = get_action_executor() if ACTION_EXECUTOR_AVAILABLE else None
        self.web_search = web_search_tool if WEB_SEARCH_AVAILABLE else None
        self.security = security_manager if SECURITY_MANAGER_AVAILABLE else None
        
        logger.info("✅ ActionHandler inicializado")
        if not ACTION_EXECUTOR_AVAILABLE:
            logger.warning("⚠️ Modo degradado: Action executor desativado")
    
    
    async def execute_actions(
        self,
        actions: List,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executa lista de ações (estruturadas ou legadas)
        
        Args:
            actions: Lista de ActionUnion (estruturado) ou strings (legado)
            context: Contexto adicional (usado para feedback ao LLM)
        
        Returns:
            Lista de resultados:
            [
                {
                    "status": "success" | "failed" | "blocked",
                    "action": str,
                    "result": str,
                    "error": str (opcional)
                },
                ...
            ]
        """
        if not actions:
            return []
        
        logger.info(f"🚀 Executing {len(actions)} actions...")
        results = []
        
        for action in actions:
            try:
                # MODO 1: Structured Action (P1 - Pydantic models)
                if hasattr(action, 'action'):
                    result = await self._execute_structured_action(action)
                
                # MODO 2: Legacy Action (String com regex)
                elif isinstance(action, str):
                    result = await self._execute_legacy_action(action)
                
                else:
                    result = {
                        "status": "failed",
                        "action": "unknown",
                        "error": f"Tipo de ação desconhecido: {type(action)}"
                    }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Erro ao executar ação: {e}")
                results.append({
                    "status": "failed",
                    "action": str(action)[:50],
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"✅ Actions executed: {success_count}/{len(results)} successful")
        return results
    
    
    async def _execute_structured_action(self, action: ActionUnion) -> Dict[str, Any]:
        """Executa ação estruturada (Pydantic model)"""
        
        # Validação de segurança
        if self.security:
            is_safe = self._validate_security(action)
            if not is_safe:
                return {
                    "status": "blocked",
                    "action": action.action,
                    "error": "Security validation failed"
                }
        
        # Executar via ActionExecutor
        if not self.executor:
            return {
                "status": "failed",
                "action": action.action,
                "error": "ActionExecutor não disponível"
            }
        
        try:
            # Rodar executor síncrono em thread separada
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.executor.execute_action,
                action
            )
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Structured action failed: {e}")
            return {
                "status": "failed",
                "action": action.action,
                "error": str(e)
            }
    
    
    async def _execute_legacy_action(self, action_str: str) -> Dict[str, Any]:
        """Executa ação legada ([ACTION: ...])"""
        
        logger.debug(f"🔧 Legacy action: {action_str}")
        
        # Extrair comando
        match = re.search(r'\[ACTION: (.*?)\]', action_str)
        if not match:
            return {
                "status": "failed",
                "action": "parse",
                "error": "Formato inválido"
            }
        
        command = match.group(1)
        
        # Roteamento de comandos
        if "search_web" in command or "SEARCH:" in action_str:
            return await self._handle_web_search(action_str)
        
        elif "read_file" in command:
            return await self._handle_read_file(command)
        
        elif "write_file" in command:
            return await self._handle_write_file(command)
        
        elif "list_dir" in command:
            return await self._handle_list_dir(command)
        
        else:
            # Fallback: Executar via action_controller (se disponível)
            return {
                "status": "failed",
                "action": command,
                "error": "Comando legado não suportado"
            }
    
    
    def _validate_security(self, action) -> bool:
        """Valida ação contra security manager"""
        if not self.security:
            return True  # Sem security manager = permitir tudo
        
        try:
            action_type = action.action
            
            # File actions
            if action_type in ['read_file', 'write_file']:
                path = action.path
                operation = 'read' if action_type == 'read_file' else 'write'
                return self.security.validate_file_action(path, operation)
            
            # Command execution
            elif action_type in ['run_command', 'open_program']:
                # TODO: Implementar validação de comandos
                return True
            
            # Outras ações são safe
            return True
        
        except Exception as e:
            logger.error(f"❌ Security validation error: {e}")
            return False
    
    
    async def _handle_web_search(self, action_str: str) -> Dict[str, Any]:
        """Executa busca web"""
        if not self.web_search:
            return {
                "status": "failed",
                "action": "search_web",
                "error": "Web search não disponível"
            }
        
        try:
            # Extrair query
            query_match = re.search(r"(?:SEARCH:|search_web\()['\"](.*?)['\"]", action_str)
            if not query_match:
                return {
                    "status": "failed",
                    "action": "search_web",
                    "error": "Query não encontrada"
                }
            
            query = query_match.group(1)
            
            # Executar busca
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                self.web_search.search,
                query
            )
            
            return {
                "status": "success",
                "action": "search_web",
                "result": search_results
            }
        
        except Exception as e:
            logger.error(f"❌ Web search failed: {e}")
            return {
                "status": "failed",
                "action": "search_web",
                "error": str(e)
            }
    
    
    async def _handle_read_file(self, command: str) -> Dict[str, Any]:
        """Lê arquivo"""
        try:
            # Extrair path
            path_match = re.search(r"read_file\(['\"](.+?)['\"]\)", command)
            if not path_match:
                return {
                    "status": "failed",
                    "action": "read_file",
                    "error": "Path não encontrado"
                }
            
            file_path = path_match.group(1)
            
            # Validar segurança
            if self.security and not self.security.validate_file_action(file_path, 'read'):
                return {
                    "status": "blocked",
                    "action": "read_file",
                    "error": "Security: Path bloqueado"
                }
            
            # Ler arquivo (AsyncIO nativo com aiofiles)
            path_obj = Path(file_path)
            if not path_obj.exists():
                return {
                    "status": "failed",
                    "action": "read_file",
                    "error": f"Arquivo não encontrado: {file_path}"
                }
            
            # Usar aiofiles para I/O assíncrono nativo com timeout
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Adicionar timeout de 5s para leitura
                content = await asyncio.wait_for(f.read(), timeout=5.0)
            
            # Truncar se muito grande
            if len(content) > 3000:
                content = content[:3000] + "\n... (truncado)"
            
            return {
                "status": "success",
                "action": "read_file",
                "result": f"[ARQUIVO: {file_path}]\n{content}"
            }
        
        except Exception as e:
            logger.error(f"❌ Read file failed: {e}")
            return {
                "status": "failed",
                "action": "read_file",
                "error": str(e)
            }
    
    
    async def _handle_write_file(self, command: str) -> Dict[str, Any]:
        """Escreve arquivo"""
        try:
            # Extrair path e content
            args_match = re.search(r"write_file\(['\"](.+?)['\"]\s*,\s*['\"](.+?)['\"]\)", command, re.DOTALL)
            if not args_match:
                return {
                    "status": "failed",
                    "action": "write_file",
                    "error": "Args não encontrados"
                }
            
            file_path = args_match.group(1)
            content = args_match.group(2).replace('\\n', '\n')
            
            # Validar segurança
            if self.security and not self.security.validate_file_action(file_path, 'write'):
                return {
                    "status": "blocked",
                    "action": "write_file",
                    "error": "Security: Path bloqueado"
                }
            
            # Escrever arquivo (AsyncIO nativo com aiofiles)
            path_obj = Path(file_path)
            
            # Criar diretório se não existe (síncrono OK)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Usar aiofiles para escrita assíncrona
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "status": "success",
                "action": "write_file",
                "result": f"Arquivo '{file_path}' escrito com sucesso"
            }
        
        except Exception as e:
            logger.error(f"❌ Write file failed: {e}")
            return {
                "status": "failed",
                "action": "write_file",
                "error": str(e)
            }
    
    
    async def _handle_list_dir(self, command: str) -> Dict[str, Any]:
        """Lista diretório"""
        try:
            # Extrair path
            path_match = re.search(r"list_dir\(['\"](.+?)['\"]\)", command)
            if not path_match:
                return {
                    "status": "failed",
                    "action": "list_dir",
                    "error": "Path não encontrado"
                }
            
            dir_path = path_match.group(1)
            
            # Listar (mantém síncrono - os.listdir é rápido)
            if not os.path.isdir(dir_path):
                raise FileNotFoundError(f"Diretório não encontrado: {dir_path}")
            
            items = os.listdir(dir_path)
            # Limitar a 50 items
            items = items[:50]
            
            return {
                "status": "success",
                "action": "list_dir",
                "result": f"[DIRETÓRIO: {dir_path}]\n{', '.join(items)}"
            }
        
        except Exception as e:
            logger.error(f"❌ List dir failed: {e}")
            return {
                "status": "failed",
                "action": "list_dir",
                "error": str(e)
            }


# ============================================================================
# SINGLETON GETTER
# ============================================================================
_action_handler_instance = None

def get_action_handler() -> ActionHandler:
    """Retorna instância singleton do ActionHandler"""
    global _action_handler_instance
    if _action_handler_instance is None:
        _action_handler_instance = ActionHandler()
    return _action_handler_instance
