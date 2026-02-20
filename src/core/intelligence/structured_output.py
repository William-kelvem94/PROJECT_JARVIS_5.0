"""
Modelos Estruturados para AÃ§Ãµes do Agente
==========================================
Define schemas Pydantic para output estruturado do LLM.
Substitui parsing frÃ¡gil por regex com validaÃ§Ã£o robusta.

CORREÃ‡ÃƒO P1: Parser JSON Estruturado
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS - Tipos de AÃ§Ãµes DisponÃ­veis
# ============================================================================


class ActionType(str, Enum):
    """Tipos de aÃ§Ãµes que o agente pode executar"""

    # AÃ§Ãµes de Interface
    CLICK_AT = "click_at"
    TYPE_TEXT = "type_text"
    PRESS_KEY = "press_key"
    HOTKEY = "hotkey"
    SCROLL = "scroll"

    # AÃ§Ãµes de Sistema
    OPEN_PROGRAM = "open_program"
    RUN_COMMAND = "run_command"

    # AÃ§Ãµes de Arquivo
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_DIR = "list_dir"
    CREATE_DIR = "create_dir"
    DELETE_FILE = "delete_file"
    ORGANIZE_DIRECTORY = "organize_directory"

    # AÃ§Ãµes de Web
    SEARCH_WEB = "search_web"
    OPEN_URL = "open_url"

    # AÃ§Ãµes IoT (Phase 4)
    IOT_CONTROL = "iot_control"

    # AÃ§Ãµes de Desktop AvanÃ§adas (Phase 4)
    WINDOW_MANAGE = "window_manage"
    DRAG_DROP = "drag_drop"

    # AÃ§Ãµes de Controle
    WAIT = "wait"
    SCREENSHOT = "screenshot"

    # AÃ§Ãµes de EvoluÃ§Ã£o (Singularity Edition)
    READ_CODEBASE = "read_codebase"
    READ_CODE_FILE = "read_code_file"
    UPDATE_SYSTEM_CODE = "update_system_code"

    # AÃ§Ãµes de Soberania de Hardware (Singularity)
    GET_PROCESSES = "get_processes"
    SET_PROCESS_PRIORITY = "set_process_priority"
    SET_POWER_PLAN = "set_power_plan"
    GET_HARDWARE_SUGGESTIONS = "get_hardware_suggestions"
    READ_CLIPBOARD = "read_clipboard"
    ANALYZE_AND_ORGANIZE = "analyze_and_organize"
    REGISTER_NICKNAME = "register_nickname"
    REGISTER_USER = "register_user"
    RELOCATE_USER = "relocate_user"

    # NOVAS AÇÕES (Integradas do PVA)
    SEARCH_LOCAL_FILES = "search_local_files"
    RUN_AUTONOMOUS_RESEARCH = "run_autonomous_research"


# ============================================================================
# MODELOS DE AÃ‡Ã•ES - Um modelo por tipo de aÃ§Ã£o
# ============================================================================


class ClickAction(BaseModel):
    """AÃ§Ã£o: Clicar em coordenada especÃ­fica"""

    action: Literal[ActionType.CLICK_AT] = ActionType.CLICK_AT
    x: int = Field(..., ge=0, description="Coordenada X do clique")
    y: int = Field(..., ge=0, description="Coordenada Y do clique")
    button: str = Field("left", description="BotÃ£o do mouse: left, right, middle")
    clicks: int = Field(1, ge=1, le=3, description="NÃºmero de cliques")


class TypeTextAction(BaseModel):
    """AÃ§Ã£o: Digitar texto"""

    action: Literal[ActionType.TYPE_TEXT] = ActionType.TYPE_TEXT
    text: str = Field(..., min_length=1, description="Texto a ser digitado")
    interval: float = Field(
        0.0, ge=0.0, le=1.0, description="Intervalo entre teclas (segundos)"
    )


class PressKeyAction(BaseModel):
    """AÃ§Ã£o: Pressionar tecla Ãºnica"""

    action: Literal[ActionType.PRESS_KEY] = ActionType.PRESS_KEY
    key: str = Field(
        ..., min_length=1, description="Tecla a ser pressionada (ex: enter, esc, tab)"
    )
    presses: int = Field(1, ge=1, le=10, description="NÃºmero de pressionamentos")


class HotkeyAction(BaseModel):
    """AÃ§Ã£o: Atalho de teclado (mÃºltiplas teclas)"""

    action: Literal[ActionType.HOTKEY] = ActionType.HOTKEY
    keys: List[str] = Field(
        ..., min_items=2, description="Teclas do atalho (ex: ['ctrl', 'c'])"
    )


class ScrollAction(BaseModel):
    """AÃ§Ã£o: Rolar tela"""

    action: Literal[ActionType.SCROLL] = ActionType.SCROLL
    direction: Literal["up", "down", "left", "right"] = Field(
        "down", description="DireÃ§Ã£o do scroll"
    )
    amount: int = Field(3, ge=1, le=20, description="Quantidade de scroll")


class OpenProgramAction(BaseModel):
    """AÃ§Ã£o: Abrir programa"""

    action: Literal[ActionType.OPEN_PROGRAM] = ActionType.OPEN_PROGRAM
    program: str = Field(..., min_length=1, description="Nome ou caminho do programa")


class RunCommandAction(BaseModel):
    """AÃ§Ã£o: Executar comando do sistema"""

    action: Literal[ActionType.RUN_COMMAND] = ActionType.RUN_COMMAND
    command: str = Field(..., min_length=1, description="Comando a ser executado")
    shell: bool = Field(True, description="Executar via shell")


class ReadFileAction(BaseModel):
    """AÃ§Ã£o: Ler conteÃºdo de arquivo"""

    action: Literal[ActionType.READ_FILE] = ActionType.READ_FILE
    path: str = Field(..., min_length=1, description="Caminho do arquivo")
    encoding: str = Field("utf-8", description="Encoding do arquivo")
    max_chars: int = Field(
        3000, ge=100, le=50000, description="MÃ¡ximo de caracteres a ler"
    )


class WriteFileAction(BaseModel):
    """AÃ§Ã£o: Escrever em arquivo"""

    action: Literal[ActionType.WRITE_FILE] = ActionType.WRITE_FILE
    path: str = Field(..., min_length=1, description="Caminho do arquivo")
    content: str = Field(..., description="ConteÃºdo a escrever")
    encoding: str = Field("utf-8", description="Encoding do arquivo")
    append: bool = Field(False, description="Anexar ao invÃ©s de sobrescrever")


class ListDirAction(BaseModel):
    """AÃ§Ã£o: Listar conteÃºdo de diretÃ³rio"""

    action: Literal[ActionType.LIST_DIR] = ActionType.LIST_DIR
    path: str = Field(..., min_length=1, description="Caminho do diretÃ³rio")
    pattern: Optional[str] = Field(None, description="PadrÃ£o de filtro (ex: *.py)")


class OrganizeDirectoryAction(BaseModel):
    """AÃ§Ã£o: Organizar arquivos em subpastas por categoria"""

    action: Literal[ActionType.ORGANIZE_DIRECTORY] = ActionType.ORGANIZE_DIRECTORY
    path: str = Field(
        ..., min_length=1, description="Caminho da pasta a ser organizada"
    )


class SearchWebAction(BaseModel):
    """AÃ§Ã£o: Buscar na web"""

    action: Literal[ActionType.SEARCH_WEB] = ActionType.SEARCH_WEB
    query: str = Field(..., min_length=1, description="Query de busca")
    max_results: int = Field(5, ge=1, le=20, description="MÃ¡ximo de resultados")


class IOTAction(BaseModel):
    """AÃ§Ã£o: Controlar dispositivos IoT (Home Assistant)"""

    action: Literal[ActionType.IOT_CONTROL] = ActionType.IOT_CONTROL
    device: str = Field(..., description="ID ou nome do dispositivo (ex: luz_sala)")
    command: str = Field(
        ..., description="Comando (ex: turn_on, turn_off, set_brightness)"
    )
    params: Optional[Dict[str, Any]] = Field(
        None, description="ParÃ¢metros extras (ex: {'brightness': 50})"
    )


class WindowAction(BaseModel):
    """AÃ§Ã£o: Gerenciar janelas do sistema"""

    action: Literal[ActionType.WINDOW_MANAGE] = ActionType.WINDOW_MANAGE
    window_title: Optional[str] = Field(None, description="Parte do tÃ­tulo da janela")
    operation: Literal["focus", "minimize", "maximize", "close", "resize", "move"] = (
        Field(..., description="OperaÃ§Ã£o")
    )
    width: Optional[int] = Field(None, description="Nova largura")
    height: Optional[int] = Field(None, description="Nova altura")
    x: Optional[int] = Field(None, description="Nova posiÃ§Ã£o X")
    y: Optional[int] = Field(None, description="Nova posiÃ§Ã£o Y")


class DragDropAction(BaseModel):
    """AÃ§Ã£o: Arrastar e soltar"""

    action: Literal[ActionType.DRAG_DROP] = ActionType.DRAG_DROP
    x_start: int = Field(..., description="X inicial")
    y_start: int = Field(..., description="Y inicial")
    x_end: int = Field(..., description="X final")
    y_end: int = Field(..., description="Y final")
    duration: float = Field(1.0, description="DuraÃ§Ã£o do arrasto")


class WaitAction(BaseModel):
    """AÃ§Ã£o: Aguardar (delay)"""

    action: Literal[ActionType.WAIT] = ActionType.WAIT
    seconds: float = Field(..., ge=0.1, le=10.0, description="Segundos a aguardar")


class ReadCodebaseAction(BaseModel):
    """AÃ§Ã£o: Listar estrutura de arquivos fonte (introspecÃ§Ã£o)"""

    action: Literal[ActionType.READ_CODEBASE] = ActionType.READ_CODEBASE


class ReadCodeFileAction(BaseModel):
    """AÃ§Ã£o: Ler conteÃºdo de um arquivo cÃ³digo do sistema"""

    action: Literal[ActionType.READ_CODE_FILE] = ActionType.READ_CODE_FILE
    path: str = Field(
        ..., description="Caminho relativo do arquivo (ex: src/core/main.py)"
    )


class UpdateSystemCodeAction(BaseModel):
    """AÃ§Ã£o: Reescrever arquivo cÃ³digo do sistema autonomamente"""

    action: Literal[ActionType.UPDATE_SYSTEM_CODE] = ActionType.UPDATE_SYSTEM_CODE
    path: str = Field(..., description="Caminho relativo do arquivo")
    new_code: str = Field(..., description="CÃ³digo Python completo e corrigido")


class ReadClipboardAction(BaseModel):
    """AÃ§Ã£o: Ler o conteÃºdo atual da Ã¡rea de transferÃªncia"""

    action: Literal[ActionType.READ_CLIPBOARD] = ActionType.READ_CLIPBOARD


class AnalyzeAndOrganizeAction(BaseModel):
    """AÃ§Ã£o: Organizar diretÃ³rio com base em lÃ³gica de IA"""

    action: Literal[ActionType.ANALYZE_AND_ORGANIZE] = ActionType.ANALYZE_AND_ORGANIZE
    path: str = Field(..., description="Caminho do diretÃ³rio")
    mapping: Dict[str, str] = Field(..., description="Mapeamento {arquivo: subpasta}")


class GetProcessesAction(BaseModel):
    """AÃ§Ã£o: Listar processos do sistema para otimizaÃ§Ã£o"""

    action: Literal[ActionType.GET_PROCESSES] = ActionType.GET_PROCESSES
    limit: int = Field(10, description="NÃºmero de processos a listar")


class SetProcessPriorityAction(BaseModel):
    """AÃ§Ã£o: Alterar prioridade de um processo"""

    action: Literal[ActionType.SET_PROCESS_PRIORITY] = ActionType.SET_PROCESS_PRIORITY
    pid: int = Field(..., description="ID do processo")
    level: str = Field(
        ...,
        description="NÃ­vel: IDLE, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH, REALTIME",
    )


class SetPowerPlanAction(BaseModel):
    """AÃ§Ã£o: Alterar plano de energia (GAMER, BALANCED, POWER_SAVER)"""

    action: Literal[ActionType.SET_POWER_PLAN] = ActionType.SET_POWER_PLAN
    mode: str = Field(..., description="Plano desejado")


class GetHardwareSuggestionsAction(BaseModel):
    """AÃ§Ã£o: Obter sugestÃµes de otimizaÃ§Ã£o de hardware da IA"""

    action: Literal[ActionType.GET_HARDWARE_SUGGESTIONS] = (
        ActionType.GET_HARDWARE_SUGGESTIONS
    )


class RegisterNicknameAction(BaseModel):
    """AÃ§Ã£o: Registrar um novo apelido/palavra de ativaÃ§Ã£o para o JARVIS"""

    action: Literal[ActionType.REGISTER_NICKNAME] = ActionType.REGISTER_NICKNAME
    nickname: str = Field(
        ..., min_length=2, description="O novo apelido a ser registrado"
    )


class SearchLocalFilesAction(BaseModel):
    """AÃ§Ã£o: Buscar arquivos no computador usando MetaCache"""

    action: Literal[ActionType.SEARCH_LOCAL_FILES] = ActionType.SEARCH_LOCAL_FILES
    query: str = Field(..., description="Termo de busca (nome do arquivo ou metadado)")


class RunAutonomousResearchAction(BaseModel):
    """AÃ§Ã£o: Pesquisa profunda na web sobre um tema"""

    action: Literal[ActionType.RUN_AUTONOMOUS_RESEARCH] = (
        ActionType.RUN_AUTONOMOUS_RESEARCH
    )
    topic: str = Field(..., description="Tema da pesquisa")


class DeleteFileAction(BaseModel):
    """AÃ§Ã£o: Excluir um arquivo (Requer permissão da Jaula de Vidro)"""

    action: Literal[ActionType.DELETE_FILE] = ActionType.DELETE_FILE
    path: str = Field(..., description="Caminho do arquivo a ser excluído")


# ============================================================================
# MODELO DE RESPOSTA DO AGENTE
# ============================================================================


# Union de todos os tipos de aÃ§Ãµes
class RegisterUserAction(BaseModel):
    """Ação: Cadastrar novo usuário confiável (Pessoa de Confiança)"""

    action: Literal[ActionType.REGISTER_USER] = ActionType.REGISTER_USER
    name: str = Field(..., description="Nome do usuário a ser cadastrado")
    relationship: str = Field(
        ..., description="O que essa pessoa é para o Master (ex: Irmão, Amigo, etc)"
    )
    role: str = Field(
        "trusted", description="Nível de permissão (master, trusted, guest)"
    )


class RelocateUserAction(BaseModel):
    """Ação: Mover um usuário para um novo workspace (compartilhado ou novo)"""

    action: Literal[ActionType.RELOCATE_USER] = ActionType.RELOCATE_USER
    name: str = Field(..., description="Nome do usuário")
    new_workspace: str = Field(..., description="Caminho absoluto do novo workspace")


ActionUnion = Union[
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
    IOTAction,
    WindowAction,
    DragDropAction,
    WaitAction,
    OrganizeDirectoryAction,
    ReadCodebaseAction,
    ReadCodeFileAction,
    UpdateSystemCodeAction,
    ReadClipboardAction,
    AnalyzeAndOrganizeAction,
    GetProcessesAction,
    SetProcessPriorityAction,
    SetPowerPlanAction,
    GetHardwareSuggestionsAction,
    RegisterNicknameAction,
    SearchLocalFilesAction,
    RunAutonomousResearchAction,
    DeleteFileAction,
    RegisterUserAction,
    RelocateUserAction,
]


class AgentResponse(BaseModel):
    """
    Resposta estruturada completa do agente.

    O LLM deve retornar JSON neste formato:
    {
        "thought": "RaciocÃ­nio sobre o que fazer",
        "actions": [
            {"action": "type_text", "text": "OlÃ¡"},
            {"action": "press_key", "key": "enter"}
        ],
        "final_answer": "Mensagem para o usuÃ¡rio"
    }
    """

    thought: str = Field(
        ..., min_length=1, description="RaciocÃ­nio/pensamento do agente"
    )
    actions: List[ActionUnion] = Field(
        default_factory=list, description="Lista de aÃ§Ãµes a executar"
    )
    final_answer: str = Field(
        ..., min_length=1, description="Resposta final para o usuÃ¡rio"
    )

    @validator("actions")
    def validate_actions_limit(cls, v):
        """Limita nÃºmero de aÃ§Ãµes para evitar loops infinitos"""
        if len(v) > 10:
            logger.warning(f"AÃ§Ãµes limitadas de {len(v)} para 10")
            return v[:10]
        return v


# ============================================================================
# PARSER DE RESPOSTA JSON
# ============================================================================


class ResponseParser:
    """Parser seguro de respostas JSON do LLM"""

    @staticmethod
    def parse_llm_response(raw_response: str) -> AgentResponse:
        """
        Parseia resposta do LLM em estrutura validada.

        Args:
            raw_response: String JSON do LLM

        Returns:
            AgentResponse validado

        Raises:
            ValueError: Se parsing falhar
        """
        try:
            # ðŸ†• PROTEÃ‡ÃƒO: Resposta vazia ou None
            if not raw_response or not raw_response.strip():
                logger.warning("âš ï¸ LLM retornou resposta vazia")
                return AgentResponse(
                    thought="Resposta vazia do modelo",
                    actions=[],
                    final_answer="Desculpe, nÃ£o consegui processar sua pergunta. Tente novamente.",
                )

            # Tentar extrair JSON se estiver em markdown
            if "```json" in raw_response:
                start = raw_response.find("```json") + 7
                end = raw_response.find("```", start)
                raw_response = raw_response[start:end].strip()
            elif "```" in raw_response:
                start = raw_response.find("```") + 3
                end = raw_response.find("```", start)
                raw_response = raw_response[start:end].strip()

            # ðŸ”’ PROTEÃ‡ÃƒO PÃ“S-EXTRAÃ‡ÃƒO: Se markdown tinha bloco vazio
            if not raw_response or not raw_response.strip():
                logger.warning("âš ï¸ LLM retornou bloco de cÃ³digo vazio")
                return AgentResponse(
                    thought="Modelo retornou bloco vazio",
                    actions=[],
                    final_answer="Desculpe, nÃ£o consegui processar sua pergunta. Tente novamente.",
                )

            # Parse JSON
            data = json.loads(raw_response)

            # Validar com Pydantic
            return AgentResponse(**data)

        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido do LLM: {e}")
            logger.debug(
                f"Raw response (primeiros 500 chars): {raw_response[:500] if raw_response else 'NONE'}"
            )

            # RESILIÊNCIA: Se não é JSON, tenta tratar como texto puro
            # Limpa possíveis tags markdown remanescentes
            import re

            clean_text = re.sub(r"```(?:json)?|```", "", raw_response).strip()

            # Tentar fallback para ações legadas ou retornar texto limpo
            if not clean_text:
                return AgentResponse(
                    thought="Resposta não estruturada (Fallback para Texto)",
                    actions=[],
                    final_answer="Senhor, tive uma falha na estruturação da resposta, mas estou operacional.",
                )

            return ResponseParser._fallback_text_parse(clean_text)

        except Exception as e:
            logger.error(f"Erro ao validar resposta: {e}")

            # Fallback: Tentar extrair resposta de texto plano
            return ResponseParser._fallback_text_parse(raw_response)

    @staticmethod
    def _fallback_text_parse(text: str) -> AgentResponse:
        """Fallback: Parser de texto plano se JSON falhar"""
        # Se houver [ACTION: ...], tentar parsear com regex (legado)
        if "[ACTION:" in text:
            logger.warning("Usando fallback regex para aÃ§Ãµes (nÃ£o estruturado)")
            return ResponseParser._legacy_regex_parse(text)

        # Resposta pura sem aÃ§Ãµes
        return AgentResponse(
            thought="Resposta direta sem raciocÃ­nio estruturado",
            actions=[],
            final_answer=text.strip(),
        )

    @staticmethod
    def _legacy_regex_parse(text: str) -> AgentResponse:
        """Parser legado por regex (fallback)"""
        import re

        actions = []
        action_strings = re.findall(r"\[ACTION: (.*?)\]", text)

        for action_str in action_strings:
            try:
                # Tentar converter regex para estruturado
                if "click_at" in action_str:
                    coords = re.findall(r"\d+", action_str)
                    if len(coords) >= 2:
                        actions.append(ClickAction(x=int(coords[0]), y=int(coords[1])))

                elif "type_text" in action_str:
                    match = re.search(r"'(.*?)'", action_str)
                    if match:
                        actions.append(TypeTextAction(text=match.group(1)))

                elif "press_key" in action_str:
                    match = re.search(r"'(.*?)'", action_str)
                    if match:
                        actions.append(PressKeyAction(key=match.group(1)))

                elif "hotkey" in action_str:
                    keys = re.findall(r"'(.*?)'", action_str)
                    if keys:
                        actions.append(HotkeyAction(keys=keys))

            except Exception as e:
                logger.warning(f"Falha ao converter aÃ§Ã£o legada: {action_str} - {e}")

        # Remover tags de aÃ§Ã£o do texto
        clean_text = re.sub(r"\[ACTION: .*?\]", "", text).strip()

        return AgentResponse(
            thought="RaciocÃ­nio nÃ£o estruturado (legado)",
            actions=actions,
            final_answer=clean_text if clean_text else "AÃ§Ãµes executadas.",
        )


# ============================================================================
# GERADOR DE SCHEMA PARA LLM
# ============================================================================


def get_actions_schema() -> Dict[str, Any]:
    """
    Gera schema JSON das aÃ§Ãµes disponÃ­veis para passar ao LLM.

    Usado para instruir o LLM sobre o formato esperado.
    """
    return {
        "type": "object",
        "required": ["thought", "final_answer"],
        "properties": {
            "thought": {
                "type": "string",
                "description": "Seu raciocÃ­nio sobre o que fazer",
            },
            "actions": {
                "type": "array",
                "description": "Lista de aÃ§Ãµes a executar (opcional)",
                "items": {
                    "oneOf": [
                        ClickAction.schema(),
                        TypeTextAction.schema(),
                        PressKeyAction.schema(),
                        HotkeyAction.schema(),
                        ScrollAction.schema(),
                        OpenProgramAction.schema(),
                        ReadFileAction.schema(),
                        WriteFileAction.schema(),
                        ListDirAction.schema(),
                        SearchWebAction.schema(),
                        WaitAction.schema(),
                        OrganizeDirectoryAction.schema(),
                        ReadCodebaseAction.schema(),
                        ReadCodeFileAction.schema(),
                        UpdateSystemCodeAction.schema(),
                        ReadClipboardAction.schema(),
                        AnalyzeAndOrganizeAction.schema(),
                        GetProcessesAction.schema(),
                        SetProcessPriorityAction.schema(),
                        SetPowerPlanAction.schema(),
                        GetHardwareSuggestionsAction.schema(),
                        RegisterNicknameAction.schema(),
                        SearchLocalFilesAction.schema(),
                        RunAutonomousResearchAction.schema(),
                    ]
                },
            },
            "final_answer": {
                "type": "string",
                "description": "Sua resposta final para o usuÃ¡rio",
            },
        },
    }


def get_example_responses() -> List[Dict[str, Any]]:
    """Exemplos de respostas vÃ¡lidas para few-shot learning"""
    return [
        {
            "user": "Abra o Notepad e escreva 'OlÃ¡'",
            "response": {
                "thought": "Preciso abrir o Notepad e depois digitar o texto",
                "actions": [
                    {"action": "open_program", "program": "notepad"},
                    {"action": "wait", "seconds": 1.0},
                    {"action": "type_text", "text": "OlÃ¡"},
                ],
                "final_answer": "Notepad aberto e texto digitado com sucesso.",
            },
        },
        {
            "user": "Qual o conteÃºdo do arquivo config.yaml?",
            "response": {
                "thought": "Preciso ler o arquivo config.yaml",
                "actions": [{"action": "read_file", "path": "config/config.yaml"}],
                "final_answer": "Vou ler o arquivo para vocÃª.",
            },
        },
        {
            "user": "Como estÃ¡ o tempo hoje?",
            "response": {
                "thought": "Esta Ã© uma pergunta que requer conhecimento atual, preciso buscar",
                "actions": [{"action": "search_web", "query": "clima hoje"}],
                "final_answer": "Deixe-me verificar o clima para vocÃª.",
            },
        },
        {
            "user": "A partir de agora, seu apelido Ã© Batatinha",
            "response": {
                "thought": "O usuÃ¡rio quer me dar um novo apelido. Preciso registrar 'Batatinha' no sistema.",
                "actions": [{"action": "register_nickname", "nickname": "Batatinha"}],
                "final_answer": "Entendido, senhor. Registrei 'Batatinha' como um dos meus nomes de ativaÃ§Ã£o.",
            },
        },
    ]
