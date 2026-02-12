"""
Modelos Estruturados para Ações do Agente
==========================================
Define schemas Pydantic para output estruturado do LLM.
Substitui parsing frágil por regex com validação robusta.

CORREÇÃO P1: Parser JSON Estruturado
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS - Tipos de Ações Disponíveis
# ============================================================================

class ActionType(str, Enum):
    """Tipos de ações que o agente pode executar"""
    # Ações de Interface
    CLICK_AT = "click_at"
    TYPE_TEXT = "type_text"
    PRESS_KEY = "press_key"
    HOTKEY = "hotkey"
    SCROLL = "scroll"
    
    # Ações de Sistema
    OPEN_PROGRAM = "open_program"
    RUN_COMMAND = "run_command"
    
    # Ações de Arquivo
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_DIR = "list_dir"
    CREATE_DIR = "create_dir"
    DELETE_FILE = "delete_file"
    ORGANIZE_DIRECTORY = "organize_directory"
    
    # Ações de Web
    SEARCH_WEB = "search_web"
    OPEN_URL = "open_url"
    
    # Ações IoT (Phase 4)
    IOT_CONTROL = "iot_control"
    
    # Ações de Desktop Avançadas (Phase 4)
    WINDOW_MANAGE = "window_manage"
    DRAG_DROP = "drag_drop"
    
    # Ações de Controle
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    
    # Ações de Evolução (Singularity Edition)
    READ_CODEBASE = "read_codebase"
    READ_CODE_FILE = "read_code_file"
    UPDATE_SYSTEM_CODE = "update_system_code"
    
    # Ações de Soberania de Hardware (Singularity)
    GET_PROCESSES = "get_processes"
    SET_PROCESS_PRIORITY = "set_process_priority"
    SET_POWER_PLAN = "set_power_plan"
    GET_HARDWARE_SUGGESTIONS = "get_hardware_suggestions"
    READ_CLIPBOARD = "read_clipboard"
    ANALYZE_AND_ORGANIZE = "analyze_and_organize"


# ============================================================================
# MODELOS DE AÇÕES - Um modelo por tipo de ação
# ============================================================================

class ClickAction(BaseModel):
    """Ação: Clicar em coordenada específica"""
    action: Literal[ActionType.CLICK_AT] = ActionType.CLICK_AT
    x: int = Field(..., ge=0, description="Coordenada X do clique")
    y: int = Field(..., ge=0, description="Coordenada Y do clique")
    button: str = Field("left", description="Botão do mouse: left, right, middle")
    clicks: int = Field(1, ge=1, le=3, description="Número de cliques")


class TypeTextAction(BaseModel):
    """Ação: Digitar texto"""
    action: Literal[ActionType.TYPE_TEXT] = ActionType.TYPE_TEXT
    text: str = Field(..., min_length=1, description="Texto a ser digitado")
    interval: float = Field(0.0, ge=0.0, le=1.0, description="Intervalo entre teclas (segundos)")


class PressKeyAction(BaseModel):
    """Ação: Pressionar tecla única"""
    action: Literal[ActionType.PRESS_KEY] = ActionType.PRESS_KEY
    key: str = Field(..., min_length=1, description="Tecla a ser pressionada (ex: enter, esc, tab)")
    presses: int = Field(1, ge=1, le=10, description="Número de pressionamentos")


class HotkeyAction(BaseModel):
    """Ação: Atalho de teclado (múltiplas teclas)"""
    action: Literal[ActionType.HOTKEY] = ActionType.HOTKEY
    keys: List[str] = Field(..., min_items=2, description="Teclas do atalho (ex: ['ctrl', 'c'])")


class ScrollAction(BaseModel):
    """Ação: Rolar tela"""
    action: Literal[ActionType.SCROLL] = ActionType.SCROLL
    direction: Literal["up", "down", "left", "right"] = Field("down", description="Direção do scroll")
    amount: int = Field(3, ge=1, le=20, description="Quantidade de scroll")


class OpenProgramAction(BaseModel):
    """Ação: Abrir programa"""
    action: Literal[ActionType.OPEN_PROGRAM] = ActionType.OPEN_PROGRAM
    program: str = Field(..., min_length=1, description="Nome ou caminho do programa")


class RunCommandAction(BaseModel):
    """Ação: Executar comando do sistema"""
    action: Literal[ActionType.RUN_COMMAND] = ActionType.RUN_COMMAND
    command: str = Field(..., min_length=1, description="Comando a ser executado")
    shell: bool = Field(True, description="Executar via shell")


class ReadFileAction(BaseModel):
    """Ação: Ler conteúdo de arquivo"""
    action: Literal[ActionType.READ_FILE] = ActionType.READ_FILE
    path: str = Field(..., min_length=1, description="Caminho do arquivo")
    encoding: str = Field("utf-8", description="Encoding do arquivo")
    max_chars: int = Field(3000, ge=100, le=50000, description="Máximo de caracteres a ler")


class WriteFileAction(BaseModel):
    """Ação: Escrever em arquivo"""
    action: Literal[ActionType.WRITE_FILE] = ActionType.WRITE_FILE
    path: str = Field(..., min_length=1, description="Caminho do arquivo")
    content: str = Field(..., description="Conteúdo a escrever")
    encoding: str = Field("utf-8", description="Encoding do arquivo")
    append: bool = Field(False, description="Anexar ao invés de sobrescrever")


class ListDirAction(BaseModel):
    """Ação: Listar conteúdo de diretório"""
    action: Literal[ActionType.LIST_DIR] = ActionType.LIST_DIR
    path: str = Field(..., min_length=1, description="Caminho do diretório")
    pattern: Optional[str] = Field(None, description="Padrão de filtro (ex: *.py)")


class OrganizeDirectoryAction(BaseModel):
    """Ação: Organizar arquivos em subpastas por categoria"""
    action: Literal[ActionType.ORGANIZE_DIRECTORY] = ActionType.ORGANIZE_DIRECTORY
    path: str = Field(..., min_length=1, description="Caminho da pasta a ser organizada")


class SearchWebAction(BaseModel):
    """Ação: Buscar na web"""
    action: Literal[ActionType.SEARCH_WEB] = ActionType.SEARCH_WEB
    query: str = Field(..., min_length=1, description="Query de busca")
    max_results: int = Field(5, ge=1, le=20, description="Máximo de resultados")


class IOTAction(BaseModel):
    """Ação: Controlar dispositivos IoT (Home Assistant)"""
    action: Literal[ActionType.IOT_CONTROL] = ActionType.IOT_CONTROL
    device: str = Field(..., description="ID ou nome do dispositivo (ex: luz_sala)")
    command: str = Field(..., description="Comando (ex: turn_on, turn_off, set_brightness)")
    params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros extras (ex: {'brightness': 50})")


class WindowAction(BaseModel):
    """Ação: Gerenciar janelas do sistema"""
    action: Literal[ActionType.WINDOW_MANAGE] = ActionType.WINDOW_MANAGE
    window_title: Optional[str] = Field(None, description="Parte do título da janela")
    operation: Literal["focus", "minimize", "maximize", "close", "resize", "move"] = Field(..., description="Operação")
    width: Optional[int] = Field(None, description="Nova largura")
    height: Optional[int] = Field(None, description="Nova altura")
    x: Optional[int] = Field(None, description="Nova posição X")
    y: Optional[int] = Field(None, description="Nova posição Y")


class DragDropAction(BaseModel):
    """Ação: Arrastar e soltar"""
    action: Literal[ActionType.DRAG_DROP] = ActionType.DRAG_DROP
    x_start: int = Field(..., description="X inicial")
    y_start: int = Field(..., description="Y inicial")
    x_end: int = Field(..., description="X final")
    y_end: int = Field(..., description="Y final")
    duration: float = Field(1.0, description="Duração do arrasto")


class WaitAction(BaseModel):
    """Ação: Aguardar (delay)"""
    action: Literal[ActionType.WAIT] = ActionType.WAIT
    seconds: float = Field(..., ge=0.1, le=10.0, description="Segundos a aguardar")


class ReadCodebaseAction(BaseModel):
    """Ação: Listar estrutura de arquivos fonte (introspecção)"""
    action: Literal[ActionType.READ_CODEBASE] = ActionType.READ_CODEBASE


class ReadCodeFileAction(BaseModel):
    """Ação: Ler conteúdo de um arquivo código do sistema"""
    action: Literal[ActionType.READ_CODE_FILE] = ActionType.READ_CODE_FILE
    path: str = Field(..., description="Caminho relativo do arquivo (ex: src/core/main.py)")


class UpdateSystemCodeAction(BaseModel):
    """Ação: Reescrever arquivo código do sistema autonomamente"""
    action: Literal[ActionType.UPDATE_SYSTEM_CODE] = ActionType.UPDATE_SYSTEM_CODE
    path: str = Field(..., description="Caminho relativo do arquivo")
    new_code: str = Field(..., description="Código Python completo e corrigido")


class ReadClipboardAction(BaseModel):
    """Ação: Ler o conteúdo atual da área de transferência"""
    action: Literal[ActionType.READ_CLIPBOARD] = ActionType.READ_CLIPBOARD


class AnalyzeAndOrganizeAction(BaseModel):
    """Ação: Organizar diretório com base em lógica de IA"""
    action: Literal[ActionType.ANALYZE_AND_ORGANIZE] = ActionType.ANALYZE_AND_ORGANIZE
    path: str = Field(..., description="Caminho do diretório")
    mapping: Dict[str, str] = Field(..., description="Mapeamento {arquivo: subpasta}")


class GetProcessesAction(BaseModel):
    """Ação: Listar processos do sistema para otimização"""
    action: Literal[ActionType.GET_PROCESSES] = ActionType.GET_PROCESSES
    limit: int = Field(10, description="Número de processos a listar")


class SetProcessPriorityAction(BaseModel):
    """Ação: Alterar prioridade de um processo"""
    action: Literal[ActionType.SET_PROCESS_PRIORITY] = ActionType.SET_PROCESS_PRIORITY
    pid: int = Field(..., description="ID do processo")
    level: str = Field(..., description="Nível: IDLE, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH, REALTIME")


class SetPowerPlanAction(BaseModel):
    """Ação: Alterar plano de energia (GAMER, BALANCED, POWER_SAVER)"""
    action: Literal[ActionType.SET_POWER_PLAN] = ActionType.SET_POWER_PLAN
    mode: str = Field(..., description="Plano desejado")


class GetHardwareSuggestionsAction(BaseModel):
    """Ação: Obter sugestões de otimização de hardware da IA"""
    action: Literal[ActionType.GET_HARDWARE_SUGGESTIONS] = ActionType.GET_HARDWARE_SUGGESTIONS


# ============================================================================
# MODELO DE RESPOSTA DO AGENTE
# ============================================================================

# Union de todos os tipos de ações
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
]


class AgentResponse(BaseModel):
    """
    Resposta estruturada completa do agente.
    
    O LLM deve retornar JSON neste formato:
    {
        "thought": "Raciocínio sobre o que fazer",
        "actions": [
            {"action": "type_text", "text": "Olá"},
            {"action": "press_key", "key": "enter"}
        ],
        "final_answer": "Mensagem para o usuário"
    }
    """
    thought: str = Field(..., min_length=1, description="Raciocínio/pensamento do agente")
    actions: List[ActionUnion] = Field(default_factory=list, description="Lista de ações a executar")
    final_answer: str = Field(..., min_length=1, description="Resposta final para o usuário")
    
    @validator('actions')
    def validate_actions_limit(cls, v):
        """Limita número de ações para evitar loops infinitos"""
        if len(v) > 10:
            logger.warning(f"Ações limitadas de {len(v)} para 10")
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
            # 🆕 PROTEÇÃO: Resposta vazia ou None
            if not raw_response or not raw_response.strip():
                logger.warning("⚠️ LLM retornou resposta vazia")
                return AgentResponse(
                    thought="Resposta vazia do modelo",
                    actions=[],
                    final_answer="Desculpe, não consegui processar sua pergunta. Tente novamente."
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
            
            # 🔒 PROTEÇÃO PÓS-EXTRAÇÃO: Se markdown tinha bloco vazio
            if not raw_response or not raw_response.strip():
                logger.warning("⚠️ LLM retornou bloco de código vazio")
                return AgentResponse(
                    thought="Modelo retornou bloco vazio",
                    actions=[],
                    final_answer="Desculpe, não consegui processar sua pergunta. Tente novamente."
                )
            
            # Parse JSON
            data = json.loads(raw_response)
            
            # Validar com Pydantic
            return AgentResponse(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido do LLM: {e}")
            logger.debug(f"Raw response (primeiros 500 chars): {raw_response[:500] if raw_response else 'NONE'}")
            
            # 🆕 RESILIÊNCIA: Se não é JSON, tenta tratar como texto puro
            # Limpa possíveis tags markdown remanescentes
            import re
            clean_text = re.sub(r'```(?:json)?|```', '', raw_response).strip()
            
            return AgentResponse(
                thought="Resposta não estruturada (Fallback para Texto)",
                actions=[],
                final_answer=clean_text if clean_text else "Senhor, tive uma falha na estruturação da resposta, mas estou operacional."
            )
            
        except Exception as e:
            logger.error(f"Erro ao validar resposta: {e}")
            
            # Fallback: Tentar extrair resposta de texto plano
            return ResponseParser._fallback_text_parse(raw_response)
    
    @staticmethod
    def _fallback_text_parse(text: str) -> AgentResponse:
        """Fallback: Parser de texto plano se JSON falhar"""
        # Se houver [ACTION: ...], tentar parsear com regex (legado)
        if "[ACTION:" in text:
            logger.warning("Usando fallback regex para ações (não estruturado)")
            return ResponseParser._legacy_regex_parse(text)
        
        # Resposta pura sem ações
        return AgentResponse(
            thought="Resposta direta sem raciocínio estruturado",
            actions=[],
            final_answer=text.strip()
        )
    
    @staticmethod
    def _legacy_regex_parse(text: str) -> AgentResponse:
        """Parser legado por regex (fallback)"""
        import re
        
        actions = []
        action_strings = re.findall(r'\[ACTION: (.*?)\]', text)
        
        for action_str in action_strings:
            try:
                # Tentar converter regex para estruturado
                if "click_at" in action_str:
                    coords = re.findall(r'\d+', action_str)
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
                logger.warning(f"Falha ao converter ação legada: {action_str} - {e}")
        
        # Remover tags de ação do texto
        clean_text = re.sub(r'\[ACTION: .*?\]', '', text).strip()
        
        return AgentResponse(
            thought="Raciocínio não estruturado (legado)",
            actions=actions,
            final_answer=clean_text if clean_text else "Ações executadas."
        )


# ============================================================================
# GERADOR DE SCHEMA PARA LLM
# ============================================================================

def get_actions_schema() -> Dict[str, Any]:
    """
    Gera schema JSON das ações disponíveis para passar ao LLM.
    
    Usado para instruir o LLM sobre o formato esperado.
    """
    return {
        "type": "object",
        "required": ["thought", "final_answer"],
        "properties": {
            "thought": {
                "type": "string",
                "description": "Seu raciocínio sobre o que fazer"
            },
            "actions": {
                "type": "array",
                "description": "Lista de ações a executar (opcional)",
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
                    ]
                }
            },
            "final_answer": {
                "type": "string",
                "description": "Sua resposta final para o usuário"
            }
        }
    }


def get_example_responses() -> List[Dict[str, Any]]:
    """Exemplos de respostas válidas para few-shot learning"""
    return [
        {
            "user": "Abra o Notepad e escreva 'Olá'",
            "response": {
                "thought": "Preciso abrir o Notepad e depois digitar o texto",
                "actions": [
                    {"action": "open_program", "program": "notepad"},
                    {"action": "wait", "seconds": 1.0},
                    {"action": "type_text", "text": "Olá"}
                ],
                "final_answer": "Notepad aberto e texto digitado com sucesso."
            }
        },
        {
            "user": "Qual o conteúdo do arquivo config.yaml?",
            "response": {
                "thought": "Preciso ler o arquivo config.yaml",
                "actions": [
                    {"action": "read_file", "path": "config/config.yaml"}
                ],
                "final_answer": "Vou ler o arquivo para você."
            }
        },
        {
            "user": "Como está o tempo hoje?",
            "response": {
                "thought": "Esta é uma pergunta que requer conhecimento atual, preciso buscar",
                "actions": [
                    {"action": "search_web", "query": "clima hoje"}
                ],
                "final_answer": "Deixe-me verificar o clima para você."
            }
        }
    ]
