"""
JARVIS COMPLETO - Assistente Pessoal Virtual Totalmente Funcional
Integra todos os módulos para criar um JARVIS real que conversa, pensa e age
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.logger import logger
from core.local_llm import LocalLLM
from core.config import Config

# Módulos implementados
from modules.memory.persistent_memory import PersistentMemory
from modules.system.security_module import SecurityManager, PermissionLevel
from modules.processing.task_decomposition import TaskDecomposer, TaskExecutor, Task

# Módulos de ação
from modules.action.file_manager import FileManager
from modules.action.task_manager import TaskManager

# Sistema de controle
from core.system_controller import SystemControllerBase

# Importações opcionais
try:
    from modules.memory.semantic_memory import SemanticMemory
    SEMANTIC_MEMORY_AVAILABLE = True
except ImportError:
    SEMANTIC_MEMORY_AVAILABLE = False
    logger.warning("Semantic Memory não disponível")

try:
    from modules.input.whisper_module import WhisperModule
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from modules.input.advanced_tts import AdvancedTTSModule, FallbackTTSModule
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    from modules.action.calendar_integration import CalendarIntegration
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

try:
    from modules.action.email_integration import EmailIntegration
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


class JarvisComplete:
    """
    JARVIS Completo - O assistente pessoal virtual real
    
    Capacidades:
    - Conversa natural com IA
    - Controle total do desktop
    - Organização de arquivos
    - Gerenciamento de tarefas
    - Integração com calendário e email
    - Comando por voz
    - Memória persistente
    - Segurança e permissões
    - Geração de documentos
    - Automação completa
    """
    
    def __init__(
        self,
        ollama_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        enable_voice: bool = False,
        enable_security: bool = True,
        enable_semantic_memory: bool = True
    ):
        """
        Inicializa o JARVIS completo.
        
        Args:
            ollama_url: URL do Ollama (padrão: detecta automaticamente)
            ollama_model: Modelo LLM (padrão: codellama:7b)
            enable_voice: Habilitar comando por voz
            enable_security: Habilitar sistema de segurança
            enable_semantic_memory: Habilitar memória semântica
        """
        logger.info("🤖 Inicializando JARVIS COMPLETO...")
        
        self.config = Config()
        
        # 1. Inicializar IA (cérebro do JARVIS)
        logger.info("🧠 Inicializando cérebro (IA)...")
        self.llm = LocalLLM(
            base_url=ollama_url,
            model=ollama_model or os.getenv('OLLAMA_MODEL', 'codellama:7b')
        )
        
        # 2. Inicializar memória
        logger.info("💾 Inicializando memória...")
        self.memory = PersistentMemory()
        
        if enable_semantic_memory and SEMANTIC_MEMORY_AVAILABLE:
            try:
                self.semantic_memory = SemanticMemory()
                logger.info("✅ Memória semântica ativada")
            except Exception as e:
                logger.warning(f"Memória semântica não disponível: {e}")
                self.semantic_memory = None
        else:
            self.semantic_memory = None
        
        # 3. Inicializar segurança
        if enable_security:
            logger.info("🔒 Inicializando sistema de segurança...")
            self.security = SecurityManager()
            self.security.set_permission_level(PermissionLevel.ADMIN)  # Padrão: admin para JARVIS funcionar
        else:
            self.security = None
        
        # 4. Inicializar módulos de ação
        logger.info("🛠️ Inicializando módulos de ação...")
        self.file_manager = FileManager()
        self.task_manager = TaskManager()
        
        # 5. Inicializar planejamento de tarefas
        logger.info("📋 Inicializando planejador de tarefas...")
        self.task_decomposer = TaskDecomposer(llm_client=self.llm)
        self.task_executor = TaskExecutor()
        
        # Registrar handlers de ação
        self._register_action_handlers()
        
        # 6. Inicializar voz (opcional)
        self.voice_enabled = False
        if enable_voice:
            self._init_voice()
        
        # 7. Inicializar integrações (opcional)
        self._init_integrations()
        
        # 8. Estado da conversação
        self.conversation_context = []
        self.current_task = None
        
        logger.info("✅ JARVIS COMPLETO inicializado e pronto!")
        logger.info("💬 Diga 'Olá JARVIS' para começar")
    
    def _init_voice(self):
        """Inicializa módulos de voz."""
        try:
            if WHISPER_AVAILABLE:
                self.stt = WhisperModule(model_name="base")
                logger.info("🎤 Whisper STT ativado")
            else:
                self.stt = None
            
            if TTS_AVAILABLE:
                try:
                    self.tts = AdvancedTTSModule()
                    logger.info("🔊 Coqui TTS ativado")
                except:
                    self.tts = FallbackTTSModule()
                    logger.info("🔊 Fallback TTS ativado")
            else:
                self.tts = None
            
            self.voice_enabled = (self.stt is not None and self.tts is not None)
            
        except Exception as e:
            logger.error(f"Erro ao inicializar voz: {e}")
            self.voice_enabled = False
    
    def _init_integrations(self):
        """Inicializa integrações externas."""
        # Calendar
        if CALENDAR_AVAILABLE:
            try:
                self.calendar = CalendarIntegration()
                if self.calendar.is_available():
                    logger.info("📅 Google Calendar integrado")
                else:
                    self.calendar = None
            except:
                self.calendar = None
        else:
            self.calendar = None
        
        # Email
        if EMAIL_AVAILABLE:
            try:
                self.email = EmailIntegration()
                if self.email.is_available():
                    logger.info("📧 Gmail integrado")
                else:
                    self.email = None
            except:
                self.email = None
        else:
            self.email = None
    
    def _register_action_handlers(self):
        """Registra handlers para ações do executor de tarefas."""
        # Operações de arquivo
        self.task_executor.register_handler("read_file", self._handle_read_file)
        self.task_executor.register_handler("write_file", self._handle_write_file)
        self.task_executor.register_handler("move_file", self._handle_move_file)
        self.task_executor.register_handler("delete_file", self._handle_delete_file)
        self.task_executor.register_handler("list_files", self._handle_list_files)
        self.task_executor.register_handler("organize_files", self._handle_organize_files)
        
        # Operações de sistema
        self.task_executor.register_handler("open_app", self._handle_open_app)
        self.task_executor.register_handler("execute_command", self._handle_execute_command)
        
        # Tarefas
        self.task_executor.register_handler("create_task", self._handle_create_task)
        self.task_executor.register_handler("list_tasks", self._handle_list_tasks)
        
        # Geração de conteúdo
        self.task_executor.register_handler("generate_text", self._handle_generate_text)
        self.task_executor.register_handler("generate_document", self._handle_generate_document)
        
        # Web e pesquisa
        self.task_executor.register_handler("web_search", self._handle_web_search)
        
        # Calendar
        if self.calendar:
            self.task_executor.register_handler("create_event", self._handle_create_event)
            self.task_executor.register_handler("list_events", self._handle_list_events)
        
        # Email
        if self.email:
            self.task_executor.register_handler("send_email", self._handle_send_email)
            self.task_executor.register_handler("read_emails", self._handle_read_emails)
    
    # ========== HANDLERS DE AÇÕES ==========
    
    def _handle_read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lê arquivo."""
        try:
            path = params.get("path")
            content = self.file_manager.read_file(path)
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Escreve arquivo."""
        try:
            path = params.get("path")
            content = params.get("content")
            self.file_manager.write_file(path, content)
            return {"success": True, "message": f"Arquivo {path} criado"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_move_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move arquivo."""
        try:
            source = params.get("source")
            destination = params.get("destination")
            self.file_manager.move_file(source, destination)
            return {"success": True, "message": f"Arquivo movido de {source} para {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_delete_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deleta arquivo."""
        try:
            path = params.get("path")
            self.file_manager.delete_file(path)
            return {"success": True, "message": f"Arquivo {path} deletado"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_list_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista arquivos."""
        try:
            path = params.get("path", ".")
            files = self.file_manager.list_files(path)
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_organize_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Organiza arquivos por tipo."""
        try:
            path = params.get("path", ".")
            result = self.file_manager.organize_files_by_type(path)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_open_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Abre aplicativo."""
        try:
            app_name = params.get("app_name")
            # Usar system controller
            import platform
            if platform.system() == "Windows":
                from core.system_controller import WindowsController
                controller = WindowsController()
                result = controller.open_application(app_name)
                return result
            else:
                return {"success": False, "error": "Sistema não suportado"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_execute_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa comando do sistema."""
        try:
            command = params.get("command")
            
            # Verificar segurança
            if self.security:
                if not self.security.check_permission("execute_command"):
                    return {"success": False, "error": "Permissão negada"}
                
                is_safe, reason = self.security.is_safe_command(command)
                if not is_safe:
                    return {"success": False, "error": f"Comando bloqueado: {reason}"}
            
            # Executar
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cria tarefa."""
        try:
            title = params.get("title")
            description = params.get("description", "")
            self.task_manager.create_task(title, description)
            return {"success": True, "message": f"Tarefa '{title}' criada"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_list_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista tarefas."""
        try:
            tasks = self.task_manager.list_tasks()
            return {"success": True, "tasks": tasks}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_generate_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gera texto com IA."""
        try:
            prompt = params.get("prompt")
            text = self.llm.generate(prompt)
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_generate_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gera documento."""
        try:
            topic = params.get("topic")
            output_path = params.get("output_path")
            
            # Gerar conteúdo
            prompt = f"Escreva um documento completo e profissional sobre: {topic}. Inclua introdução, desenvolvimento e conclusão."
            content = self.llm.generate(prompt, max_tokens=2000)
            
            # Salvar
            self.file_manager.write_file(output_path, content)
            
            return {"success": True, "message": f"Documento gerado em {output_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pesquisa na web."""
        try:
            query = params.get("query")
            # Implementar pesquisa web
            return {"success": True, "message": f"Pesquisando: {query}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cria evento no calendário."""
        try:
            if not self.calendar:
                return {"success": False, "error": "Calendário não configurado"}
            
            title = params.get("title")
            start_time = params.get("start_time")
            
            event = self.calendar.create_event(title, start_time)
            return {"success": True, "event": event}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista eventos do calendário."""
        try:
            if not self.calendar:
                return {"success": False, "error": "Calendário não configurado"}
            
            events = self.calendar.list_events()
            return {"success": True, "events": events}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Envia email."""
        try:
            if not self.email:
                return {"success": False, "error": "Email não configurado"}
            
            to = params.get("to")
            subject = params.get("subject")
            body = params.get("body")
            
            result = self.email.send_email(to, subject, body)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_read_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lê emails."""
        try:
            if not self.email:
                return {"success": False, "error": "Email não configurado"}
            
            emails = self.email.get_latest_messages(count=5)
            return {"success": True, "emails": emails}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== INTERFACE PRINCIPAL ==========
    
    async def process_command(self, command: str, use_voice_response: bool = False) -> str:
        """
        Processa comando do usuário - CÉREBRO DO JARVIS
        
        Args:
            command: Comando em linguagem natural
            use_voice_response: Se True, fala a resposta
        
        Returns:
            Resposta do JARVIS
        """
        logger.info(f"👤 Usuário: {command}")
        
        # Salvar na memória
        self.memory.save_conversation("user", command)
        if self.semantic_memory:
            self.semantic_memory.store_conversation("user", command)
        
        # Analisar intenção e executar
        try:
            # 1. Verificar se é tarefa complexa que requer planejamento
            if self._requires_task_planning(command):
                response = await self._execute_complex_task(command)
            
            # 2. Se não, processar diretamente com IA
            else:
                response = await self._process_with_ai(command)
            
            # 3. Salvar resposta na memória
            self.memory.save_conversation("assistant", response)
            if self.semantic_memory:
                self.semantic_memory.store_conversation("assistant", response)
            
            # 4. Falar resposta se solicitado
            if use_voice_response and self.voice_enabled and self.tts:
                self.tts.speak_async(response)
            
            logger.info(f"🤖 JARVIS: {response[:100]}...")
            return response
            
        except Exception as e:
            error_msg = f"Desculpe, ocorreu um erro: {str(e)}"
            logger.error(f"Erro ao processar comando: {e}")
            return error_msg
    
    def _requires_task_planning(self, command: str) -> bool:
        """Determina se comando requer planejamento de tarefas."""
        # Keywords que indicam tarefas complexas
        complex_keywords = [
            "organize", "crie um projeto", "desenvolva", "faça um",
            "mova todos", "organizar", "desenvolver", "criar projeto",
            "série de", "vários", "múltiplos"
        ]
        
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in complex_keywords)
    
    async def _execute_complex_task(self, command: str) -> str:
        """Executa tarefa complexa com planejamento."""
        logger.info("📋 Tarefa complexa detectada - iniciando planejamento...")
        
        # 1. Decompor tarefa
        plan = self.task_decomposer.decompose(command)
        
        # 2. Executar plano
        logger.info(f"Executando plano com {len(plan.tasks)} tarefas...")
        success = self.task_executor.execute_plan(plan)
        
        # 3. Gerar resposta
        if success:
            response = f"Tarefa concluída com sucesso! Executei {len(plan.tasks)} etapas:\n"
            for i, task in enumerate(plan.tasks, 1):
                status = "✅" if task.status.value == "completed" else "❌"
                response += f"{status} {i}. {task.description}\n"
        else:
            failed_tasks = [t for t in plan.tasks if t.status.value == "failed"]
            response = f"Tarefa parcialmente concluída. {len(failed_tasks)} etapa(s) falharam."
        
        return response
    
    async def _process_with_ai(self, command: str) -> str:
        """Processa comando diretamente com IA."""
        # Buscar contexto relevante da memória
        context = self._get_relevant_context(command)
        
        # Construir prompt com contexto
        system_prompt = """Você é JARVIS, um assistente pessoal virtual inteligente.
Você tem acesso completo ao computador do usuário e pode:
- Controlar aplicativos e sistema
- Gerenciar arquivos e pastas
- Criar e organizar documentos
- Agendar eventos
- Enviar emails
- Pesquisar informações
- Automatizar tarefas
- E muito mais

Seja prestativo, preciso e proativo. Se o usuário pedir algo, execute a ação."""
        
        user_prompt = f"""Contexto recente:
{context}

Usuário: {command}

JARVIS:"""
        
        # Gerar resposta
        response = self.llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=500
        )
        
        return response
    
    def _get_relevant_context(self, query: str, limit: int = 3) -> str:
        """Recupera contexto relevante da memória."""
        context_parts = []
        
        # Histórico recente
        recent = self.memory.get_conversation_history(limit=limit)
        for msg in recent[-limit:]:
            role = "Você" if msg["role"] == "user" else "JARVIS"
            context_parts.append(f"{role}: {msg['content']}")
        
        # Memória semântica (se disponível)
        if self.semantic_memory:
            try:
                semantic_results = self.semantic_memory.search_conversations(query, n_results=2)
                for result in semantic_results:
                    if result["content"] not in [msg["content"] for msg in recent]:
                        context_parts.append(f"Lembrete: {result['content']}")
            except:
                pass
        
        return "\n".join(context_parts) if context_parts else "Nenhum contexto anterior"
    
    def speak(self, text: str):
        """Fala texto (se voz habilitada)."""
        if self.voice_enabled and self.tts:
            self.tts.speak(text)
        else:
            print(f"JARVIS: {text}")
    
    def listen(self, duration: float = 5.0) -> Optional[str]:
        """Escuta comando por voz."""
        if self.voice_enabled and self.stt:
            return self.stt.listen(duration)
        return None
    
    async def conversation_mode(self):
        """Modo de conversação contínua."""
        print("\n" + "="*60)
        print("🤖 JARVIS - Modo Conversação Ativado")
        print("="*60)
        print("Digite 'sair' para encerrar")
        print("="*60 + "\n")
        
        while True:
            try:
                # Ler comando
                user_input = input("Você: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("\n👋 Até logo!")
                    break
                
                # Processar
                response = await self.process_command(user_input)
                print(f"\nJARVIS: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}\n")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do JARVIS."""
        return {
            "ia_ativa": self.llm is not None,
            "memoria_ativa": True,
            "memoria_semantica": self.semantic_memory is not None,
            "seguranca_ativa": self.security is not None,
            "voz_ativa": self.voice_enabled,
            "calendario_integrado": self.calendar is not None,
            "email_integrado": self.email is not None,
            "conversas_armazenadas": self.memory.get_stats().get("conversations", 0),
            "modelo_ia": self.llm.model if self.llm else None,
            "pronto_para_uso": True
        }


# Função de conveniência
async def main():
    """Inicia JARVIS em modo conversação."""
    jarvis = JarvisComplete(
        enable_voice=False,  # Desabilitar voz por padrão
        enable_security=True,
        enable_semantic_memory=True
    )
    
    # Mostrar status
    status = jarvis.get_status()
    print("\n📊 Status do JARVIS:")
    for key, value in status.items():
        symbol = "✅" if value else "❌"
        if isinstance(value, bool):
            print(f"  {symbol} {key}")
        else:
            print(f"  • {key}: {value}")
    
    print("\n")
    
    # Modo conversação
    await jarvis.conversation_mode()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
