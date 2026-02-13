"""
JARVIS 5.0 - Action Handler
============================
CORREÃ‡ÃƒO P2: SeparaÃ§Ã£o do God Object AIAgent

RESPONSABILIDADE:
  Gerenciar todas as AÃ‡Ã•ES do sistema:
  - Parsing de aÃ§Ãµes (JSON ou regex legado)
  - ExecuÃ§Ã£o via ActionExecutor
  - ValidaÃ§Ã£o de seguranÃ§a
  - Web search, file I/O, system commands

ARQUITETURA:
  AIAgent (Orquestrador)
    â†“
  PerceptionEngine
  DecisionEngine
  ActionHandler â† ESTE MÃ“DULO
"""

import logging
import asyncio
import re
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path
import aiofiles
import os

if TYPE_CHECKING:
    from src.core.intelligence.structured_output import ActionUnion

logger = logging.getLogger(__name__)

# ============================================================================
# SAFE IMPORTS
# ============================================================================
try:
    from src.core.intelligence.action_executor import get_action_executor, ActionExecutor
    # ðŸ†• PROTEÃ‡ÃƒO: Importamos um sÃ­mbolo vÃ¡lido para garantir que o mÃ³dulo existe
    from src.core.intelligence.structured_output import ActionType as _AT
    ACTION_EXECUTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ action_executor nÃ£o disponÃ­vel: {e}")
    get_action_executor = None
    ActionExecutor = None
    ActionUnion = None
    ACTION_EXECUTOR_AVAILABLE = False

try:
    from src.utils.web_search_tool import web_search_tool
    WEB_SEARCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ web_search_tool nÃ£o disponÃ­vel: {e}")
    web_search_tool = None
    WEB_SEARCH_AVAILABLE = False

try:
    from src.core.security.security_manager import security_manager
    SECURITY_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ security_manager nÃ£o disponÃ­vel: {e}")
    security_manager = None
    SECURITY_MANAGER_AVAILABLE = False


class ActionHandler:
    """
    Manipulador de AÃ§Ãµes - Executa aÃ§Ãµes estruturadas ou legadas
    
    CAPABILITIES:
      1. Structured Actions: Executa via ActionExecutor (P1)
      2. Legacy Actions: Regex parsing [ACTION: ...]
      3. Security Validation: Valida cada aÃ§Ã£o antes de executar
      4. Web Search: IntegraÃ§Ã£o com web_search_tool
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
        
        logger.info("âœ… ActionHandler inicializado")
        if not ACTION_EXECUTOR_AVAILABLE:
            logger.warning("âš ï¸ Modo degradado: Action executor desativado")
    
    
    async def execute_actions(
        self,
        actions: List,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executa lista de aÃ§Ãµes (estruturadas ou legadas)
        
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
        
        logger.info(f"ðŸš€ Executing {len(actions)} actions...")
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
                        "error": f"Tipo de aÃ§Ã£o desconhecido: {type(action)}"
                    }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"âŒ Erro ao executar aÃ§Ã£o: {e}")
                results.append({
                    "status": "failed",
                    "action": str(action)[:50],
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"âœ… Actions executed: {success_count}/{len(results)} successful")
        return results
    
    def execute_actions_sync(self, actions: List, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """VersÃ£o sÃ­ncrona para compatibilidade com AIAgent legado"""
        try:
            import asyncio
            # Se jÃ¡ houver um loop rodando nesta thread, precisamos de uma abordagem diferente
            # mas geralmente background threads de worker nÃ£o tÃªm loop.
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Usar o loop existente se possÃ­vel (approach delicado)
                    # Por simplicidade, assumimos que threads de worker podem criar seu loop
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(self.execute_actions(actions, context))
                else:
                    return loop.run_until_complete(self.execute_actions(actions, context))
            except RuntimeError:
                return asyncio.run(self.execute_actions(actions, context))
        except Exception as e:
            logger.error(f"Erro na execuÃ§Ã£o sÃ­ncrona de aÃ§Ãµes: {e}")
            return [{"status": "failed", "action": "sync_wrapper", "error": str(e)}]
    
    
    async def _execute_structured_action(self, action: 'ActionUnion') -> Dict[str, Any]:
        """Executa aÃ§Ã£o estruturada (Pydantic model)"""
        
        # ValidaÃ§Ã£o de seguranÃ§a
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
                "error": "ActionExecutor nÃ£o disponÃ­vel"
            }
        
        try:
            # Rodar executor sÃ­ncrono em thread separada
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.executor.execute_action,
                action
            )
            
            return result
        
        except Exception as e:
            logger.error(f"âŒ Structured action failed: {e}")
            return {
                "status": "failed",
                "action": action.action,
                "error": str(e)
            }
    
    
    async def _execute_legacy_action(self, action_str: str) -> Dict[str, Any]:
        """Executa aÃ§Ã£o legada ([ACTION: ...])"""
        
        logger.debug(f"ðŸ”§ Legacy action parsing: {action_str[:100]}...")
        
        # 1. Tentar extrair todas as aÃ§Ãµes no formato [ACTION: cmd]
        actions = re.findall(r'\[ACTION: (.*?)\]', action_str)
        if not actions:
            # Tentar formato SEARCH: se nÃ£o houver ACTION:
            if "SEARCH:" in action_str:
                return await self._handle_web_search(action_str)
            return {
                "status": "failed",
                "action": "parse",
                "error": "Nenhuma aÃ§Ã£o encontrada no formato [ACTION: ...]"
            }
        
        combined_results = []
        for cmd in actions:
            result = {"status": "success", "action": cmd, "result": "Executado"}
            try:
                # --- Mouse & Keyboard ---
                if "click_at" in cmd:
                    coords = re.findall(r'\d+', cmd)
                    if len(coords) >= 2:
                        from src.core.intelligence.structured_output import ClickAction
                        action = ClickAction(action="click_at", x=int(coords[0]), y=int(coords[1]))
                        result = self.executor.execute_action(action)
                
                elif "type_text" in cmd:
                    text_match = re.search(r"['\"](.*?)['\"]", cmd)
                    if text_match:
                        from src.core.intelligence.structured_output import TypeTextAction
                        action = TypeTextAction(action="type_text", text=text_match.group(1))
                        result = self.executor.execute_action(action)
                
                elif "press_key" in cmd:
                    key_match = re.search(r"['\"](.*?)['\"]", cmd)
                    if key_match:
                        from src.core.intelligence.structured_output import PressKeyAction
                        action = PressKeyAction(action="press_key", key=key_match.group(1))
                        result = self.executor.execute_action(action)
                
                elif "hotkey" in cmd:
                    keys = re.findall(r"['\"](.*?)['\"]", cmd)
                    if keys:
                        from src.core.intelligence.structured_output import HotkeyAction
                        action = HotkeyAction(action="hotkey", keys=keys)
                        result = self.executor.execute_action(action)
                
                # --- File System ---
                elif "read_file" in cmd:
                    path_match = re.search(r"['\"](.*?)['\"]", cmd)
                    if path_match:
                        from src.core.intelligence.structured_output import ReadFileAction
                        action = ReadFileAction(action="read_file", path=path_match.group(1))
                        result = self.executor.execute_action(action)
                
                elif "write_file" in cmd:
                    # write_file('path', 'content')
                    args = re.findall(r"['\"](.*?)['\"]", cmd)
                    if len(args) >= 2:
                        from src.core.intelligence.structured_output import WriteFileAction
                        action = WriteFileAction(action="write_file", path=args[0], content=args[1])
                        result = self.executor.execute_action(action)
                
                elif "list_dir" in cmd:
                    path_match = re.search(r"['\"](.*?)['\"]", cmd)
                    if path_match:
                        from src.core.intelligence.structured_output import ListDirAction
                        action = ListDirAction(action="list_dir", path=path_match.group(1))
                        result = self.executor.execute_action(action)
                
                # --- System ---
                elif "open_program" in cmd:
                    prog_match = re.search(r"['\"](.*?)['\"]", cmd)
                    if prog_match:
                        from src.core.intelligence.structured_output import OpenProgramAction
                        action = OpenProgramAction(action="open_program", program=prog_match.group(1))
                        result = self.executor.execute_action(action)
                
                elif "search_web" in cmd:
                    query_match = re.search(r"['\"](.*?)['\"]", cmd)
                    if query_match:
                        from src.core.intelligence.structured_output import SearchWebAction
                        action = SearchWebAction(action="search_web", query=query_match.group(1))
                        result = self.executor.execute_action(action)
                
                else:
                    result = {
                        "status": "failed",
                        "action": cmd,
                        "error": "Comando legado desconhecido ou nÃ£o mapeado"
                    }
                
                combined_results.append(result)
                
            except Exception as e:
                logger.error(f"Erro ao processar comando legado: {e}")
                combined_results.append({"status": "failed", "action": cmd, "error": str(e)})
        
        # Retornar o Ãºltimo resultado ou um consolidado
        if len(combined_results) == 1:
            return combined_results[0]
        
        return {
            "status": "success" if all(r["status"] == "success" for r in combined_results) else "partial_success",
            "action": "multiple_legacy",
            "result": "\n".join([str(r.get("result", r.get("error", ""))) for r in combined_results])
        }
    
    
    def _validate_security(self, action) -> bool:
        """Valida aÃ§Ã£o contra security manager"""
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
                # TODO: Implementar validaÃ§Ã£o de comandos
                return True
            
            # Outras aÃ§Ãµes sÃ£o safe
            return True
        
        except Exception as e:
            logger.error(f"âŒ Security validation error: {e}")
            return False
    
    
    async def _handle_web_search(self, action_str: str) -> Dict[str, Any]:
        """Executa busca web"""
        if not self.web_search:
            return {
                "status": "failed",
                "action": "search_web",
                "error": "Web search nÃ£o disponÃ­vel"
            }
        
        try:
            # Extrair query
            query_match = re.search(r"(?:SEARCH:|search_web\()['\"](.*?)['\"]", action_str)
            if not query_match:
                return {
                    "status": "failed",
                    "action": "search_web",
                    "error": "Query nÃ£o encontrada"
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
            logger.error(f"âŒ Web search failed: {e}")
            return {
                "status": "failed",
                "action": "search_web",
                "error": str(e)
            }
    
    
    async def _handle_read_file(self, command: str) -> Dict[str, Any]:
        """LÃª arquivo"""
        try:
            # Extrair path
            path_match = re.search(r"read_file\(['\"](.+?)['\"]\)", command)
            if not path_match:
                return {
                    "status": "failed",
                    "action": "read_file",
                    "error": "Path nÃ£o encontrado"
                }
            
            file_path = path_match.group(1)
            
            # Validar seguranÃ§a
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
                    "error": f"Arquivo nÃ£o encontrado: {file_path}"
                }
            
            # Usar aiofiles para I/O assÃ­ncrono nativo com timeout
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
            logger.error(f"âŒ Read file failed: {e}")
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
                    "error": "Args nÃ£o encontrados"
                }
            
            file_path = args_match.group(1)
            content = args_match.group(2).replace('\\n', '\n')
            
            # Validar seguranÃ§a
            if self.security and not self.security.validate_file_action(file_path, 'write'):
                return {
                    "status": "blocked",
                    "action": "write_file",
                    "error": "Security: Path bloqueado"
                }
            
            # Escrever arquivo (AsyncIO nativo com aiofiles)
            path_obj = Path(file_path)
            
            # Criar diretÃ³rio se nÃ£o existe (sÃ­ncrono OK)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Usar aiofiles para escrita assÃ­ncrona
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "status": "success",
                "action": "write_file",
                "result": f"Arquivo '{file_path}' escrito com sucesso"
            }
        
        except Exception as e:
            logger.error(f"âŒ Write file failed: {e}")
            return {
                "status": "failed",
                "action": "write_file",
                "error": str(e)
            }
    
    
    async def _handle_list_dir(self, command: str) -> Dict[str, Any]:
        """Lista diretÃ³rio"""
        try:
            # Extrair path
            path_match = re.search(r"list_dir\(['\"](.+?)['\"]\)", command)
            if not path_match:
                return {
                    "status": "failed",
                    "action": "list_dir",
                    "error": "Path nÃ£o encontrado"
                }
            
            dir_path = path_match.group(1)
            
            # Listar (mantÃ©m sÃ­ncrono - os.listdir Ã© rÃ¡pido)
            if not os.path.isdir(dir_path):
                raise FileNotFoundError(f"DiretÃ³rio nÃ£o encontrado: {dir_path}")
            
            items = os.listdir(dir_path)
            # Limitar a 50 items
            items = items[:50]
            
            return {
                "status": "success",
                "action": "list_dir",
                "result": f"[DIRETÃ“RIO: {dir_path}]\n{', '.join(items)}"
            }
        
        except Exception as e:
            logger.error(f"âŒ List dir failed: {e}")
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
    """Retorna instÃ¢ncia singleton do ActionHandler"""
    global _action_handler_instance
    if _action_handler_instance is None:
        _action_handler_instance = ActionHandler()
    return _action_handler_instance
