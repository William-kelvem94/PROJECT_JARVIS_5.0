"""
JARVIS v2 - Arquitetura Modular Completa
Integra todos os módulos em uma única instância
"""

import os
import asyncio
from typing import Optional, Dict, Any

from core.config import Config
from core.logger import logger
from core.local_llm import LocalLLM

# Módulos de Entrada
from modules.input.voice_module import VoiceModule
from modules.input.text_module import TextModule

# Módulo de Processamento
from modules.processing.orchestrator import Orchestrator, MessageType

# Módulos de Ação
from modules.action.rpa_module import RPAModule
from modules.action.file_manager import FileManager
from modules.action.task_manager import TaskManager

# Sistema RAG
from modules.rag.vector_store import VectorStore

# Sistema
from modules.system.capability_detector import CapabilityDetector

# Plugins existentes (para compatibilidade)
from plugins.system_plugin import SystemPlugin
from plugins.file_plugin import FilePlugin


class JarvisV2:
    """
    JARVIS v2 - Assistente IA Modular
    """
    
    def __init__(self, auto_detect_capabilities: bool = True):
        """
        Inicializa o JARVIS v2.
        
        Args:
            auto_detect_capabilities: Se True, detecta capacidades e ajusta modelo
        """
        self.config = Config()
        
        # Detectar capacidades
        if auto_detect_capabilities:
            logger.info("Detectando capacidades do sistema...")
            self.capability_detector = CapabilityDetector()
            capabilities = self.capability_detector.get_capabilities()
            logger.info(self.capability_detector.get_summary())
            
            # Ajustar modelo recomendado
            recommended = capabilities.get("recommended_model", {})
            model_name = recommended.get("model", "llama3:8b")
            logger.info(f"Modelo recomendado: {model_name}")
        else:
            self.capability_detector = None
            model_name = os.getenv('OLLAMA_MODEL', self.config.get("ollama_model", "llama3:8b"))
        
        # Inicializar LLM
        try:
            self.llm = LocalLLM(model=model_name)
            logger.info(f"LLM inicializado: {model_name}")
        except Exception as e:
            logger.error(f"Erro ao inicializar LLM: {e}")
            self.llm = None
        
        # Inicializar módulos de entrada
        self.voice_module = VoiceModule()
        self.text_module = TextModule()
        
        # Inicializar orquestrador
        self.orchestrator = Orchestrator(llm=self.llm)
        
        # Inicializar módulos de ação
        self.rpa_module = RPAModule()
        self.file_manager = FileManager()
        self.task_manager = TaskManager()
        
        # Inicializar RAG
        self.vector_store = VectorStore()
        
        # Plugins existentes (compatibilidade)
        self.system_plugin = SystemPlugin()
        self.file_plugin = FilePlugin()
        
        # Registrar skills no orquestrador
        self._register_skills()
        
        # Registrar handler no módulo de texto
        self.text_module.register_handler(self._handle_text_input)
        
        logger.info("✅ JARVIS v2 inicializado com sucesso!")
    
    def _register_skills(self):
        """Registra todas as skills no orquestrador."""
        
        # Skill: Abrir aplicativo
        async def open_app_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            app_name = params.get("app_name") or message.split()[-1]
            result = self.rpa_module.open_application(app_name)
            return {
                "response": result.get("result", "Aplicativo aberto"),
                "actions": [result]
            }
        
        self.orchestrator.register_skill("open_app", open_app_skill)
        
        # Skill: Ler arquivo
        async def read_file_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            file_path = params.get("file_path")
            if not file_path:
                # Tentar extrair do texto
                words = message.split()
                for i, word in enumerate(words):
                    if word in ["arquivo", "file", "ler", "read"] and i + 1 < len(words):
                        file_path = words[i + 1]
                        break
            
            if file_path:
                result = self.file_manager.read_file(file_path)
                return {
                    "response": result.get("content", "Arquivo lido com sucesso")[:500],
                    "actions": [result]
                }
            return {
                "response": "Por favor, especifique o caminho do arquivo.",
                "actions": []
            }
        
        self.orchestrator.register_skill("read_file", read_file_skill)
        
        # Skill: Listar arquivos
        async def list_files_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            directory = params.get("directory")
            result = self.file_manager.list_directory(directory)
            if result.get("success"):
                items = result.get("items", [])
                response = f"Encontrados {len(items)} itens:\n"
                response += "\n".join([f"- {item['name']} ({item['type']})" for item in items[:10]])
                return {
                    "response": response,
                    "actions": [result]
                }
            return {
                "response": result.get("error", "Erro ao listar arquivos"),
                "actions": []
            }
        
        self.orchestrator.register_skill("list_files", list_files_skill)
        
        # Skill: Organizar arquivos
        async def organize_files_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            directory = params.get("directory")
            result = self.file_manager.organize_files(directory)
            return {
                "response": result.get("result", "Arquivos organizados"),
                "actions": [result]
            }
        
        self.orchestrator.register_skill("organize_files", organize_files_skill)
        
        # Skill: Adicionar tarefa
        async def add_task_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            title = params.get("title") or message
            description = params.get("description")
            result = self.task_manager.add_task(title, description)
            return {
                "response": result.get("result", "Tarefa adicionada"),
                "actions": [result]
            }
        
        self.orchestrator.register_skill("add_task", add_task_skill)
        
        # Skill: Listar tarefas
        async def list_tasks_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            result = self.task_manager.list_tasks()
            tasks = result.get("tasks", [])
            if tasks:
                response = f"Você tem {len(tasks)} tarefas:\n"
                for task in tasks[:5]:
                    status = "✅" if task.get("completed") else "⏳"
                    response += f"{status} {task.get('title', 'Sem título')}\n"
                return {
                    "response": response,
                    "actions": [result]
                }
            return {
                "response": "Nenhuma tarefa encontrada.",
                "actions": []
            }
        
        self.orchestrator.register_skill("list_tasks", list_tasks_skill)
        
        # Skill: Definir alarme
        async def set_alarm_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
            time = params.get("time")
            alarm_message = params.get("message") or "Alarme!"
            result = self.task_manager.set_alarm(time, alarm_message)
            return {
                "response": result.get("result", "Alarme definido"),
                "actions": [result]
            }
        
        self.orchestrator.register_skill("set_alarm", set_alarm_skill)
        
        logger.info(f"✅ {len(self.orchestrator.skills)} skills registradas")
    
    def _handle_text_input(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handler para processar entrada de texto."""
        # Processar de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.orchestrator.process_message(text, MessageType.TEXT, context)
        )
        loop.close()
        return result
    
    async def process(self, message: str, message_type: MessageType = MessageType.TEXT) -> Dict[str, Any]:
        """
        Processa uma mensagem.
        
        Args:
            message: Mensagem do usuário
            message_type: Tipo da mensagem
        
        Returns:
            Resposta processada
        """
        return await self.orchestrator.process_message(message, message_type)
    
    def listen_and_process(self) -> Optional[Dict[str, Any]]:
        """
        Escuta voz e processa.
        
        Returns:
            Resposta processada ou None
        """
        if not self.voice_module.is_available():
            logger.warning("Módulo de voz não disponível")
            return None
        
        # Escutar
        text = self.voice_module.listen()
        if not text:
            return None
        
        # Processar
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.orchestrator.process_message(text, MessageType.VOICE)
        )
        loop.close()
        
        # Falar resposta
        if result.get("response"):
            self.voice_module.speak(result["response"])
        
        return result
    
    def add_knowledge(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Adiciona conhecimento ao banco RAG.
        
        Args:
            text: Texto para adicionar
            metadata: Metadados opcionais
        """
        return self.vector_store.add_document(text, metadata)
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema."""
        return {
            "version": "2.0",
            "llm_available": self.llm is not None,
            "voice_available": self.voice_module.is_available(),
            "rpa_available": self.rpa_module.is_available(),
            "skills_count": len(self.orchestrator.skills),
            "vector_store_stats": self.vector_store.get_stats(),
            "capabilities": self.capability_detector.get_capabilities() if self.capability_detector else None
        }

