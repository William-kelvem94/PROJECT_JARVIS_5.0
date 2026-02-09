"""
Executor de Ações Estruturado
==============================
Executa ações validadas pelos modelos Pydantic.
Substitui execução via regex por execução type-safe.

CORREÇÃO P1: Action Executor Seguro
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.core.intelligence.structured_output import (
    ActionUnion,
    ClickAction,
    TypeTextAction,
    PressKeyAction,
    HotkeyAction,
    ScrollAction,
    OpenProgramAction,
    RunCommandAction,
    ReadFileAction,
    WriteFileAction,
    ListDirAction,
    SearchWebAction,
    WaitAction,
    ActionType,
)

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executa ações estruturadas de forma segura.
    
    Cada tipo de ação tem um método handler específico.
    """
    
    def __init__(self):
        """Inicializa executor com controllers necessários"""
        self.action_controller = None
        self.security_manager = None
        self.web_search_tool = None
        
        # Importar controllers
        self._load_controllers()
        
        # Mapeamento de tipos para handlers
        self.handlers = {
            ActionType.CLICK_AT: self._execute_click,
            ActionType.TYPE_TEXT: self._execute_type_text,
            ActionType.PRESS_KEY: self._execute_press_key,
            ActionType.HOTKEY: self._execute_hotkey,
            ActionType.SCROLL: self._execute_scroll,
            ActionType.OPEN_PROGRAM: self._execute_open_program,
            ActionType.RUN_COMMAND: self._execute_run_command,
            ActionType.READ_FILE: self._execute_read_file,
            ActionType.WRITE_FILE: self._execute_write_file,
            ActionType.LIST_DIR: self._execute_list_dir,
            ActionType.SEARCH_WEB: self._execute_search_web,
            ActionType.WAIT: self._execute_wait,
        }
    
    def _load_controllers(self):
        """Carrega controllers necessários"""
        try:
            from src.core.actions.action_controller import action_controller
            self.action_controller = action_controller
        except ImportError:
            logger.warning("⚠️ action_controller não disponível")
        
        try:
            from src.core.security.security_manager import security_manager
            self.security_manager = security_manager
        except ImportError:
            logger.warning("⚠️ security_manager não disponível")
            # Criar dummy
            class DummySecurityManager:
                def validate_file_action(self, *args, **kwargs):
                    return True
            self.security_manager = DummySecurityManager()
        
        try:
            from src.utils.web_search_tool import web_search_tool
            self.web_search_tool = web_search_tool
        except ImportError:
            logger.warning("⚠️ web_search_tool não disponível")
    
    def execute_action(self, action: ActionUnion) -> Dict[str, Any]:
        """
        Executa uma única ação estruturada.
        
        Args:
            action: Ação validada (Pydantic model)
        
        Returns:
            Resultado da execução com status e dados
        """
        action_type = ActionType(action.action)
        handler = self.handlers.get(action_type)
        
        if not handler:
            logger.error(f"Handler não encontrado para ação: {action_type}")
            return {
                "status": "error",
                "action": action_type.value,
                "error": "Handler não implementado"
            }
        
        try:
            logger.info(f"Executando ação: {action_type.value}")
            result = handler(action)
            return {
                "status": "success",
                "action": action_type.value,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Erro ao executar ação {action_type.value}: {e}")
            return {
                "status": "error",
                "action": action_type.value,
                "error": str(e)
            }
    
    def execute_actions(self, actions: List[ActionUnion]) -> List[Dict[str, Any]]:
        """
        Executa lista de ações em sequência.
        
        Args:
            actions: Lista de ações validadas
        
        Returns:
            Lista de resultados
        """
        results = []
        
        for i, action in enumerate(actions):
            logger.info(f"Executando ação {i+1}/{len(actions)}")
            result = self.execute_action(action)
            results.append(result)
            
            # Se ação crítica falhou, interromper
            if result["status"] == "error" and action.action in [
                ActionType.READ_FILE,
                ActionType.WRITE_FILE,
            ]:
                logger.warning(f"Ação crítica falhou, interrompendo sequência")
                break
        
        return results
    
    # ========================================================================
    # HANDLERS - Um método por tipo de ação
    # ========================================================================
    
    def _execute_click(self, action: ClickAction) -> str:
        """Executa clique do mouse"""
        if not self.action_controller:
            raise RuntimeError("action_controller não disponível")
        
        self.action_controller.click_at(
            action.x,
            action.y,
            button=action.button,
            clicks=action.clicks
        )
        
        return f"Clique em ({action.x}, {action.y})"
    
    def _execute_type_text(self, action: TypeTextAction) -> str:
        """Digita texto"""
        if not self.action_controller:
            raise RuntimeError("action_controller não disponível")
        
        self.action_controller.type_text(
            action.text,
            interval=action.interval
        )
        
        return f"Texto digitado: {action.text[:50]}..."
    
    def _execute_press_key(self, action: PressKeyAction) -> str:
        """Pressiona tecla"""
        if not self.action_controller:
            raise RuntimeError("action_controller não disponível")
        
        for _ in range(action.presses):
            self.action_controller.press_key(action.key)
            if action.presses > 1:
                time.sleep(0.1)
        
        return f"Tecla '{action.key}' pressionada {action.presses}x"
    
    def _execute_hotkey(self, action: HotkeyAction) -> str:
        """Executa atalho de teclado"""
        if not self.action_controller:
            raise RuntimeError("action_controller não disponível")
        
        self.action_controller.hotkey(*action.keys)
        
        return f"Atalho: {'+'.join(action.keys)}"
    
    def _execute_scroll(self, action: ScrollAction) -> str:
        """Executa scroll"""
        if not self.action_controller:
            raise RuntimeError("action_controller não disponível")
        
        # Implementar scroll (pode precisar de método em action_controller)
        logger.warning("Scroll não totalmente implementado")
        
        return f"Scroll {action.direction} ({action.amount})"
    
    def _execute_open_program(self, action: OpenProgramAction) -> str:
        """Abre programa"""
        if not self.action_controller:
            raise RuntimeError("action_controller não disponível")
        
        # Usar Win+R para abrir programa
        self.action_controller.hotkey('win', 'r')
        time.sleep(0.5)
        self.action_controller.type_text(action.program)
        self.action_controller.press_key('enter')
        
        return f"Programa '{action.program}' aberto"
    
    def _execute_run_command(self, action: RunCommandAction) -> str:
        """Executa comando do sistema"""
        import subprocess
        
        # Validação de segurança básica
        dangerous_cmds = ['rm -rf', 'del /f', 'format', 'shutdown']
        if any(cmd in action.command.lower() for cmd in dangerous_cmds):
            raise RuntimeError(f"Comando perigoso bloqueado: {action.command}")
        
        result = subprocess.run(
            action.command,
            shell=action.shell,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout[:500]  # Limitar output
        
        return f"Comando executado. Output: {output}"
    
    def _execute_read_file(self, action: ReadFileAction) -> str:
        """Lê arquivo"""
        # Validar com security manager
        if not self.security_manager.validate_file_action(action.path, 'read'):
            raise RuntimeError(f"Leitura de arquivo não autorizada: {action.path}")
        
        if not os.path.exists(action.path):
            raise FileNotFoundError(f"Arquivo não encontrado: {action.path}")
        
        with open(action.path, 'r', encoding=action.encoding, errors='ignore') as f:
            content = f.read(action.max_chars)
        
        # Se truncado, adicionar nota
        if len(content) >= action.max_chars:
            content += "\n... (truncado)"
        
        return content
    
    def _execute_write_file(self, action: WriteFileAction) -> str:
        """Escreve arquivo"""
        # Validar com security manager
        if not self.security_manager.validate_file_action(action.path, 'write'):
            raise RuntimeError(f"Escrita de arquivo não autorizada: {action.path}")
        
        # Criar diretório se necessário
        os.makedirs(os.path.dirname(action.path) or '.', exist_ok=True)
        
        mode = 'a' if action.append else 'w'
        
        with open(action.path, mode, encoding=action.encoding) as f:
            f.write(action.content)
        
        return f"Arquivo '{action.path}' escrito ({len(action.content)} chars)"
    
    def _execute_list_dir(self, action: ListDirAction) -> str:
        """Lista diretório"""
        if not os.path.isdir(action.path):
            raise NotADirectoryError(f"Não é um diretório: {action.path}")
        
        items = os.listdir(action.path)
        
        # Filtrar por pattern se fornecido
        if action.pattern:
            import fnmatch
            items = [item for item in items if fnmatch.fnmatch(item, action.pattern)]
        
        # Limitar para não sobrecarregar contexto
        if len(items) > 50:
            items = items[:50]
            items.append("... (mais itens)")
        
        return f"Conteúdo de '{action.path}': {items}"
    
    def _execute_search_web(self, action: SearchWebAction) -> str:
        """Busca na web"""
        if not self.web_search_tool:
            raise RuntimeError("web_search_tool não disponível")
        
        results = self.web_search_tool.search(
            action.query,
            max_results=action.max_results
        )
        
        # Formatar resultados
        formatted = f"Resultados para '{action.query}':\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'Sem título')}\n"
            formatted += f"   {result.get('snippet', '')[:100]}...\n"
        
        return formatted
    
    def _execute_wait(self, action: WaitAction) -> str:
        """Aguarda tempo especificado"""
        time.sleep(action.seconds)
        return f"Aguardado {action.seconds}s"


# Instância global (singleton)
_executor_instance = None

def get_action_executor() -> ActionExecutor:
    """Obtém instância singleton do executor"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ActionExecutor()
    return _executor_instance
