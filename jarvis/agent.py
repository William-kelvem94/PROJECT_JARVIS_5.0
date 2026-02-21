import os
import sys
import json
import time
import threading
import logging
import datetime
import queue
from typing import Optional

logger = logging.getLogger(__name__)

from .config import (
    HOTWORD, OLLAMA_MODEL, INTERACTIONS_LOG, LISTEN_TIMEOUT, 
    CONTEXT_WINDOW, SYSTEM_PROMPT, DEVICE_LANGUAGE, LANGUAGE_VALIDATION
)
from .config_manager import config
from .commands import registry, command
from .errors import errors
from .plugin_manager import plugin_manager
from .rag import rag
from .listener import listen_for_hotword, record_chunk, STT
from .ollama_client import query_ollama
from .tts import TTS
from .conversation import ConversationMemory
from .lang_utils import get_device_language, detect_language, code_to_name
from . import dashboard_server

# Integração com o novo Learning Engine (Fase Profissional)
try:
    from .learning.learning_engine import get_learning_engine, initialize_learning_systems
    HAS_LEARNING_ENGINE = True
except ImportError:
    HAS_LEARNING_ENGINE = False
    logger.warning("⚠️ Learning Engine não encontrado no namespace .learning")

class JarvisAgent:
    def __init__(self, model: str = None, auto_setup: bool = True):
        # 1. Configurações Básicas
        self.model = model or config.get("OLLAMA_MODEL")
        self.device_lang = config.get("DEVICE_LANGUAGE") or "pt-br"
        self.lang_validate = config.get("LANGUAGE_VALIDATION")
        self.debug = False

        # 2. Inicialização de Componentes Críticos (ANTES do Dashboard)
        # TTS e STT
        self.tts = TTS(lang=self.device_lang)
        self.stt = STT()
        
        # Sistema de Mensageria Assíncrona (Performance)
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        self.is_speaking = False
        
        # Memória e RAG
        interactions_log = INTERACTIONS_LOG
        self.memory = ConversationMemory(path=interactions_log, window=config.get("CONTEXT_WINDOW"))
        os.makedirs(os.path.dirname(interactions_log), exist_ok=True)
        
        # Cérebro Local (DistilGPT2) - Carregamento pesado
        from .local_brain import LocalBrain
        try:
            from .dashboard_server import log_task
            log_task("🧠 Inicializando Cérebro Local (DistilGPT2)...")
        except: pass
        self.local_brain = LocalBrain() if config.get("USE_LOCAL_BRAIN") else None
        
        # Pré-carregamento do RAG para evitar delay na primeira fala
        try:
            log_task("📚 Sincronizando Base de Conhecimento (RAG)...")
            rag._load_model()
        except: pass

        # Plugins
        plugin_manager.load_plugins(self)

        # 2.5 Inicialização do Learning Engine (Sistema de Aprendizado Autônomo)
        self.learning_engine = None
        if HAS_LEARNING_ENGINE:
            try:
                # O projeto root é o diretório pai do jarvis
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.learning_engine = initialize_learning_systems(project_root)
                logger.info("🧠 Learning Engine integrado com sucesso ao Agente.")
            except Exception as e:
                logger.error(f"❌ Falha ao integrar Learning Engine: {e}")

        # 3. Inicia o Servidor do Dashboard (APÓS componentes estarem prontos)
        dashboard_server.start_dashboard(agent=self)

        # 4. Diagnóstico final
        from . import bootstrap
        try:
            self.startup_report = bootstrap.run_startup_checks(autoinstall=auto_setup)
        except Exception as e:
            self.startup_report = {"error": str(e)}
            errors.report("agent_init", e)

        # Auto-teste básico
        try:
            self.self_test()
        except Exception as e:
            errors.report("self_test", e)

    def self_test(self):
        print("[JARVIS] Executando diagnóstico térmico e sináptico...")
        try:
            greeting = self._startup_greeting()
            print(f"[JARVIS] {greeting}")
            self._speak(greeting)
        except Exception as e:
            errors.report("tts_test", e)

    def _log_interaction(self, user_text: str, assistant_text: str, system: bool = False):
        entry = {"ts": time.time(), "user": user_text, "assistant": assistant_text, "system": system}
        with open(INTERACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        if not system:
            try:
                self.memory.add(user_text, assistant_text)
                # Indexação RAG para memória de longo prazo
                rag.add_entry(f"Usuário: {user_text}\nAssistente: {assistant_text}")
                
                # NOVO: Registro no motor de aprendizado contínuo para Gap Analysis
                if self.learning_engine:
                    self.learning_engine.record_interaction(user_text, assistant_text)
                    
            except Exception as e:
                errors.report("memory", e)

    def _speech_worker(self):
        """Processa a fila de fala sem bloquear o pensamento do agente."""
        from . import listener
        while True:
            text = self.speech_queue.get()
            if text is None: break
            try:
                self.is_speaking = True
                listener.set_pause_listening(True)
                self.tts.speak(text)
            except Exception as e:
                logger.error(f"Erro no speech worker: {e}")
            finally:
                self.is_speaking = False
                listener.set_pause_listening(False)
                self.speech_queue.task_done()

    def _speak(self, text: str):
        """Enfileira a fala para processamento assíncrono."""
        self.speech_queue.put(text)

    def _startup_greeting(self) -> str:
        hour = datetime.datetime.now().hour
        part = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        return f"{part}, senhor. Sistemas 100% operacionais. Como posso ajudar?"

    def handle_command(self, text: str) -> None:
        if not text or len(text.strip()) < 2: return
        print(f"\n[USUÁRIO] {text}")
        try:
            from .dashboard_server import log_task
            log_task(f"📡 Processando entrada: {text}")
        except: pass
        
        # 1. Comandos Modulares (Registry)
        cmd_info = registry.find_command(text)
        if cmd_info:
            func, args = cmd_info
            try:
                log_task(f"⚙️ Executando comando interno: {func.__name__}")
                func(self, args if args else text)
                return
            except Exception as e:
                errors.report("command_execution", e)
                return

        # 2. Pesquisa RAG (Memória Relevante)
        try: log_task("🔍 Consultando memórias de longo prazo (RAG)...")
        except: pass
        relevant_memories = rag.search(text)
        long_term_context = ""
        if relevant_memories:
            long_term_context = "\n[CONTEXTO DE LONGO PRAZO]:\n" + "\n".join(relevant_memories)

        # 3. Lógica do LLM
        history_prompt = self.memory.as_prompt(config.get("SYSTEM_PROMPT"), max_items=config.get("CONTEXT_WINDOW"))
        
        # Prompt final reforçado em PT-BR
        prompt = (
            f"{history_prompt}\n"
            f"{long_term_context}\n\n"
            f"Instrução: Responda obrigatoriamente em Português do Brasil.\n"
            f"Usuário: {text}\n"
            f"Jarvis:"
        )

        resp = None
        # Tenta cérebro local primeiro se habilitado
        if self.local_brain:
            try: 
                log_task("🧠 Gerando resposta via Cérebro Local (Neural)...")
                resp = self.local_brain.reply(text, history_prompt)
                if resp and len(resp.strip()) < 5: 
                    log_task("⚠️ Resposta local muito curta, alternando para Ollama.")
                    resp = None 
            except Exception as e: 
                log_task(f"❌ Erro no Cérebro Local: {e}")
                errors.report("local_brain", e)

        # Fallback para Ollama
        if not resp:
            try: 
                log_task(f"🌐 Consultando núcleo expansivo (Ollama: {self.model})...")
                resp = query_ollama(self.model, prompt)
            except Exception as e: 
                log_task(f"❌ Erro no Ollama: {e}")
                resp = f"Desculpe, senhor. Erro no núcleo de IA: {e}"

        if resp:
            log_task("✅ Resposta gerada com sucesso.")
            print(f"[JARVIS] {resp}")
            self._log_interaction(text, resp)
            self._speak(resp)

    def run(self):
        print("[SISTEMA] Aguardando comando de voz ('Jarvis'...)")
        while True:
            try:
                cmd = listen_for_hotword(config.get("HOTWORD"), stt=self.stt)
                if cmd is None:
                    # Hotword detectada mas sem comando embutido -> escuta o resto
                    data = record_chunk(seconds=config.get("LISTEN_TIMEOUT") or 10)
                    text = self.stt.transcribe_bytes(data)
                    if text: self.handle_command(text)
                else:
                    # Hotword + comando na mesma frase
                    self.handle_command(cmd)
            except KeyboardInterrupt:
                print("\n[SISTEMA] Encerrando Jarvis...")
                break
            except Exception as e:
                errors.report("voice_loop", e)
                time.sleep(1)

# --- Comandos Base Reescritos ---

@command(["mostrar painel", "abrir dashboard", "ver interface", "ver sistema"])
def cmd_open_dashboard(agent, _):
    agent._speak("Interface de comando já operacional.")

@command(["pesquisar", "buscar", "procure", "quem é", "o que é"], is_prefix=True)
def cmd_search(agent, query):
    agent._speak(f"Consultando bancos de dados globais sobre {query}...")
    from . import web_utils
    resp = web_utils.search_online(query)
    agent._log_interaction(f"[PESQUISA]: {query}", resp, system=True)
    agent._speak(resp)

@command(["pesquisa massiva", "prospecção", "estudo profundo"], is_prefix=True)
def cmd_massive_research(agent, query):
    """Dispara o Ciclo de Sonho Massivo sobre um tema específico."""
    agent._speak(f"Iniciando prospecção massiva sobre {query}. Vou minerar Google, HuggingFace e Google Scholar. Isso pode levar um momento.")
    
    if agent.learning_engine:
        def _task():
            # Cria um gap artificial para o motor processar
            gap = {"topic": query, "context": "Solicitação direta do usuário para expansão de conhecimento."}
            agent.learning_engine.dream_cycle.research_engine.conduct_research(gap)
            agent._speak(f"Prospecção sobre {query} concluída, senhor. O Mapa de Conhecimento foi atualizado.")
        
        import threading
        threading.Thread(target=_task, daemon=True).start()
    else:
        agent._speak("Motor de aprendizado não está ativo no momento.")

@command(["limpar memória", "esquecer tudo", "reiniciar"])
def cmd_clear_memory(agent, _):
    agent.memory.clear()
    agent._speak("Memória volátil limpa com sucesso.")

if __name__ == "__main__":
    a = JarvisAgent()
    a.run()
