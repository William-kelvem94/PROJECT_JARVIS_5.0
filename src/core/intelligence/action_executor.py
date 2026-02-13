"""
Executor de AÃ§Ãµes Estruturado
==============================
Executa aÃ§Ãµes validadas pelos modelos Pydantic.
Substitui execuÃ§Ã£o via regex por execuÃ§Ã£o type-safe.

CORREÃ‡ÃƒO P1: Action Executor Seguro
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
    RegisterNicknameAction,
)

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executa aÃ§Ãµes estruturadas de forma segura.
    
    Cada tipo de aÃ§Ã£o tem um mÃ©todo handler especÃ­fico.
    """
    
    def __init__(self):
        """Inicializa executor com controllers necessÃ¡rios"""
        self.action_controller = None
        self.security_manager = None
        self.web_search_tool = None
        self.voice_controller = None
        
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
            ActionType.WINDOW_MANAGE: self._execute_window_manage,
            ActionType.DRAG_DROP: self._execute_drag_drop,
            ActionType.IOT_CONTROL: self._execute_iot_control,
            ActionType.ANALYZE_AND_ORGANIZE: self._execute_analyze_and_organize,
            ActionType.READ_CODEBASE: self._execute_read_codebase,
            ActionType.READ_CODE_FILE: self._execute_read_code_file,
            ActionType.UPDATE_SYSTEM_CODE: self._execute_update_system_code,
            ActionType.READ_CLIPBOARD: self._execute_read_clipboard,
            ActionType.GET_PROCESSES: self._execute_get_processes,
            ActionType.SET_PROCESS_PRIORITY: self._execute_set_process_priority,
            ActionType.SET_POWER_PLAN: self._execute_set_power_plan,
            ActionType.GET_HARDWARE_SUGGESTIONS: self._execute_get_hardware_suggestions,
            ActionType.REGISTER_NICKNAME: self._execute_register_nickname,
        }
    
    def _load_controllers(self):
        """Carrega controllers necessÃ¡rios"""
        try:
            from src.core.actions.action_controller import action_controller
            self.action_controller = action_controller
        except ImportError:
            logger.warning("âš ï¸ action_controller nÃ£o disponÃ­vel")
        
        try:
            from src.core.security.security_manager import security_manager
            self.security_manager = security_manager
        except ImportError:
            logger.warning("âš ï¸ security_manager nÃ£o disponÃ­vel")
            # Criar dummy
            class DummySecurityManager:
                def validate_file_action(self, *args, **kwargs):
                    return True
            self.security_manager = DummySecurityManager()
        
        try:
            from src.utils.web_search_tool import web_search_tool
            self.web_search_tool = web_search_tool
        except ImportError:
            logger.warning("âš ï¸ web_search_tool nÃ£o disponÃ­vel")

        try:
            from src.core.audio.voice_controller import voice_controller
            self.voice_controller = voice_controller
        except ImportError:
            logger.warning("âš ï¸ voice_controller nÃ£o disponÃ­vel")

        try:
            from src.core.actions.advanced_action_controller import advanced_action_controller
            self.advanced_action_controller = advanced_action_controller
        except ImportError:
            logger.warning("âš ï¸ advanced_action_controller nÃ£o disponÃ­vel")
        
        try:
            from src.core.management.hardware_manager import hardware_manager
            self.hardware_manager = hardware_manager
        except ImportError:
            logger.warning("âš ï¸ hardware_manager nÃ£o disponÃ­vel")
            self.hardware_manager = None
    
    def execute_action(self, action: ActionUnion) -> Dict[str, Any]:
        """
        Executa uma Ãºnica aÃ§Ã£o estruturada.
        
        Args:
            action: AÃ§Ã£o validada (Pydantic model)
        
        Returns:
            Resultado da execuÃ§Ã£o com status e dados
        """
        action_type = ActionType(action.action)
        handler = self.handlers.get(action_type)
        
        if not handler:
            logger.error(f"Handler nÃ£o encontrado para aÃ§Ã£o: {action_type}")
            
            # ðŸ”¥ Fase 4: Registro de Skill Gap (Curiosidade Neural)
            try:
                from src.learning.curiosity_engine import curiosity_engine
                if curiosity_engine:
                    curiosity_engine.register_skill_gap(action_type.value)
            except Exception as e:
                logger.debug(f"Falha ao registrar skill gap: {e}")

            return {
                "status": "error",
                "action": action_type.value,
                "error": "Handler nÃ£o implementado"
            }
        
        try:
            # ðŸ”¥ Fase 3: ConfirmaÃ§Ã£o de AÃ§Ãµes CrÃ­ticas
            if self.voice_controller:
                if action_type == ActionType.WRITE_FILE:
                    if not self.voice_controller.confirm_with_voice("Preciso escrever um arquivo no sistema. Posso prosseguir?"):
                        return {"status": "cancelled", "action": action_type.value, "error": "Cancelado pelo usuÃ¡rio"}
                elif action_type == ActionType.RUN_COMMAND:
                    if not self.voice_controller.confirm_with_voice(f"Vou executar um comando de terminal. Posso continuar?"):
                        return {"status": "cancelled", "action": action_type.value, "error": "Cancelado pelo usuÃ¡rio"}
                elif action_type == ActionType.OPEN_PROGRAM:
                    if not self.voice_controller.confirm_with_voice(f"Vou abrir um novo programa. Tudo bem?"):
                        return {"status": "cancelled", "action": action_type.value, "error": "Cancelado pelo usuÃ¡rio"}

            logger.info(f"Executando aÃ§Ã£o: {action_type.value}")
            result = handler(action)
            
            # ðŸ”¥ Fase 4: DestilaÃ§Ã£o de Conhecimento (Aprendizado)
            try:
                from src.learning.knowledge_distiller import knowledge_distiller
                # Nota: aqui passamos apenas a aÃ§Ã£o individual, a orquestraÃ§Ã£o 
                # pode passar o comando completo depois de executar a lista.
                # Por enquanto, logamos o sucesso.
            except ImportError: pass

            # Logs para o Dashboard Web (Phase 3)
            from src.utils.web_emitter import emit_log_sync
            emit_log_sync(f"AÃ§Ã£o executada: {action_type.value}")

            return {
                "status": "success",
                "action": action_type.value,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Erro ao executar aÃ§Ã£o {action_type.value}: {e}")
            return {
                "status": "error",
                "action": action_type.value,
                "error": str(e)
            }
    
    def execute_actions(self, actions: List[ActionUnion]) -> List[Dict[str, Any]]:
        """
        Executa lista de aÃ§Ãµes em sequÃªncia.
        
        Args:
            actions: Lista de aÃ§Ãµes validadas
        
        Returns:
            Lista de resultados
        """
        results = []
        
        for i, action in enumerate(actions):
            logger.info(f"Executando aÃ§Ã£o {i+1}/{len(actions)}")
            result = self.execute_action(action)
            results.append(result)
            
            # Se aÃ§Ã£o crÃ­tica falhou, interromper
            if result["status"] == "error" and action.action in [
                ActionType.READ_FILE,
                ActionType.WRITE_FILE,
            ]:
                logger.warning(f"AÃ§Ã£o crÃ­tica falhou, interrompendo sequÃªncia")
                break
        
        return results
    
    # ========================================================================
    # HANDLERS - Um mÃ©todo por tipo de aÃ§Ã£o
    # ========================================================================
    
    def _execute_click(self, action: ClickAction) -> str:
        """Executa clique do mouse"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
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
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        self.action_controller.type_text(
            action.text,
            interval=action.interval
        )
        
        return f"Texto digitado: {action.text[:50]}..."
    
    def _execute_press_key(self, action: PressKeyAction) -> str:
        """Pressiona tecla"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        for _ in range(action.presses):
            self.action_controller.press_key(action.key)
            if action.presses > 1:
                time.sleep(0.1)
        
        return f"Tecla '{action.key}' pressionada {action.presses}x"
    
    def _execute_hotkey(self, action: HotkeyAction) -> str:
        """Executa atalho de teclado"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        self.action_controller.hotkey(*action.keys)
        
        return f"Atalho: {'+'.join(action.keys)}"
    
    def _execute_scroll(self, action: ScrollAction) -> str:
        """Executa scroll"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        # Implementar scroll (pode precisar de mÃ©todo em action_controller)
        logger.warning("Scroll nÃ£o totalmente implementado")
        
        return f"Scroll {action.direction} ({action.amount})"
    
    def _execute_open_program(self, action: OpenProgramAction) -> str:
        """Abre programa"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        # Usar Win+R para abrir programa
        self.action_controller.hotkey('win', 'r')
        time.sleep(0.5)
        self.action_controller.type_text(action.program)
        self.action_controller.press_key('enter')
        
        return f"Programa '{action.program}' aberto"
    
    def _execute_run_command(self, action: RunCommandAction) -> str:
        """Executa comando do sistema"""
        import subprocess
        
        # ValidaÃ§Ã£o de seguranÃ§a bÃ¡sica
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
        """LÃª arquivo"""
        # Validar com security manager
        if not self.security_manager.validate_file_action(action.path, 'read'):
            raise RuntimeError(f"Leitura de arquivo nÃ£o autorizada: {action.path}")
        
        if not os.path.exists(action.path):
            raise FileNotFoundError(f"Arquivo nÃ£o encontrado: {action.path}")
        
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
            raise RuntimeError(f"Escrita de arquivo nÃ£o autorizada: {action.path}")
        
        # Criar diretÃ³rio se necessÃ¡rio
        os.makedirs(os.path.dirname(action.path) or '.', exist_ok=True)
        
        mode = 'a' if action.append else 'w'
        
        with open(action.path, mode, encoding=action.encoding) as f:
            f.write(action.content)
        
        return f"Arquivo '{action.path}' escrito ({len(action.content)} chars)"
    
    def _execute_list_dir(self, action: ListDirAction) -> str:
        """Lista diretÃ³rio"""
        if not os.path.isdir(action.path):
            raise NotADirectoryError(f"NÃ£o Ã© um diretÃ³rio: {action.path}")
        
        items = os.listdir(action.path)
        
        # Filtrar por pattern se fornecido
        if action.pattern:
            import fnmatch
            items = [item for item in items if fnmatch.fnmatch(item, action.pattern)]
        
        # Limitar para nÃ£o sobrecarregar contexto
        if len(items) > 50:
            items = items[:50]
            items.append("... (mais itens)")
        
        return f"ConteÃºdo de '{action.path}': {items}"
    
    def _execute_search_web(self, action: SearchWebAction) -> str:
        """Busca na web"""
        if not self.web_search_tool:
            raise RuntimeError("web_search_tool nÃ£o disponÃ­vel")
        
        results = self.web_search_tool.search(
            action.query,
            max_results=action.max_results
        )
        
        # Formatar resultados
        formatted = f"Resultados para '{action.query}':\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'Sem tÃ­tulo')}\n"
            formatted += f"   {result.get('snippet', '')[:100]}...\n"
        
        return formatted
    
    def _execute_wait(self, action: WaitAction) -> str:
        """Aguarda tempo especificado"""
        time.sleep(action.seconds)
        return f"Aguardado {action.seconds}s"

    def _execute_window_manage(self, action: Any) -> str:
        """Handler para WindowAction"""
        if not self.advanced_action_controller:
            raise RuntimeError("advanced_action_controller nÃ£o disponÃ­vel")
        
        success = self.advanced_action_controller.window_manage(
            window_title=action.window_title,
            operation=action.operation,
            width=action.width,
            height=action.height,
            x=action.x,
            y=action.y
        )
        return "Janela gerenciada com sucesso" if success else "Falha ao gerenciar janela"

    def _execute_drag_drop(self, action: Any) -> str:
        """Handler para DragDropAction"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        success = self.action_controller.drag_and_drop(
            action.x_start, action.y_start,
            action.x_end, action.y_end,
            duration=action.duration
        )
        return "Drag and drop executado" if success else "Falha no drag and drop"

    def _execute_iot_control(self, action: Any) -> str:
        """Handler para IOTControlAction"""
        try:
            from src.core.iot.iot_manager import iot_manager
            success = iot_manager.control_device(
                device_id=action.device,
                command=action.command,
                params=action.params
            )
            return f"Comando IoT '{action.command}' enviado para '{action.device}'" if success else "Falha no comando IoT"
        except ImportError:
            raise RuntimeError("iot_manager nÃ£o disponÃ­vel")

    def _execute_analyze_and_organize(self, action: Any) -> str:
        """Handler para AnalyzeAndOrganizeAction"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        success = self.action_controller.analyze_and_organize(action.path, action.mapping)
        return f"DiretÃ³rio '{action.path}' organizado com sucesso via IA" if success else f"Falha ao organizar diretÃ³rio '{action.path}'"

    def _execute_read_clipboard(self, action: Any) -> str:
        """Handler para ReadClipboardAction"""
        if not self.action_controller:
            raise RuntimeError("action_controller nÃ£o disponÃ­vel")
        
        content = self.action_controller.read_clipboard()
        return f"ConteÃºdo do clipboard:\n{content}" if content else "Clipboard vazio ou erro na leitura."

    def _execute_read_codebase(self, action: Any) -> str:
        """Handler para ReadCodebaseAction"""
        if not self.system_controller:
            raise RuntimeError("system_controller nÃ£o disponÃ­vel")
        
        files = self.system_controller.read_codebase_structure()
        return f"Arquivos encontrados: {files[:50]}..." if len(files) > 0 else "Nenhum arquivo encontrado."

    def _execute_read_code_file(self, action: Any) -> str:
        """Handler para ReadCodeFileAction"""
        if not self.system_controller:
            raise RuntimeError("system_controller nÃ£o disponÃ­vel")
        
        content = self.system_controller.read_file_content(action.path)
        if content:
            return f"ConteÃºdo de {action.path}:\n{content[:2000]}..."
        return f"Falha ao ler arquivo: {action.path}"

    def _execute_update_system_code(self, action: Any) -> str:
        """Handler para UpdateSystemCodeAction"""
        if not self.system_controller:
            raise RuntimeError("system_controller nÃ£o disponÃ­vel")
        
        result = self.system_controller.safe_code_update(action.path, action.new_code)
        if result["status"] == "success":
            return f"âœ… {result['message']} Backup em: {result['backup']}"
        return f"âŒ Erro na atualizaÃ§Ã£o: {result['message']}"

    def _execute_get_processes(self, action: Any) -> str:
        """Handler para GetProcessesAction"""
        if not self.hardware_manager:
            raise RuntimeError("hardware_manager nÃ£o disponÃ­vel")
        
        processes = self.hardware_manager.get_running_processes(action.limit)
        return f"Top Processos: {[{'pid': p['pid'], 'name': p['name'], 'cpu': p['cpu_percent']} for p in processes]}"

    def _execute_set_process_priority(self, action: Any) -> str:
        """Handler para SetProcessPriorityAction"""
        if not self.hardware_manager:
            raise RuntimeError("hardware_manager nÃ£o disponÃ­vel")
        
        success = self.hardware_manager.set_process_priority(action.pid, action.level)
        return f"Prioridade do PID {action.pid} alterada para {action.level}" if success else "Falha ao alterar prioridade."

    def _execute_set_power_plan(self, action: Any) -> str:
        """Handler para SetPowerPlanAction"""
        if not self.hardware_manager:
            raise RuntimeError("hardware_manager nÃ£o disponÃ­vel")
        
        success = self.hardware_manager.set_power_plan(action.mode)
        return f"Plano de energia alterado para {action.mode}" if success else "Falha ao alterar plano de energia."

    def _execute_get_hardware_suggestions(self, action: Any) -> str:
        """Handler para GetHardwareSuggestionsAction"""
        if not self.hardware_manager:
            raise RuntimeError("hardware_manager nÃ£o disponÃ­vel")
        
        suggestion = self.hardware_manager.suggest_optimizations()
        return suggestion

    def _execute_register_nickname(self, action: RegisterNicknameAction) -> str:
        """Handler para RegisterNicknameAction"""
        from src.core.audio.voice_filter import AtomicVoiceFilter
        success = AtomicVoiceFilter.add_nickname(action.nickname)
        if success:
            return f"Apelido '{action.nickname}' registrado com sucesso. Agora vocÃª pode me chamar assim!"
        return f"O apelido '{action.nickname}' jÃ¡ estÃ¡ registrado ou Ã© invÃ¡lido."


# InstÃ¢ncia global (singleton)
_executor_instance = None

def get_action_executor() -> ActionExecutor:
    """ObtÃ©m instÃ¢ncia singleton do executor"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ActionExecutor()
    return _executor_instance
