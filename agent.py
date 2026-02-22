import logging
import psutil
import subprocess
import os
import asyncio
import time
import sys
import random
from typing import Annotated
from dotenv import load_dotenv

# uncaught exceptions should be logged for telemetry

def _handle_uncaught(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger = logging.getLogger("jarvis-agent")
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = _handle_uncaught
from livekit import agents
from livekit.agents import llm, voice, WorkerOptions
from livekit.agents.voice import room_io
from livekit.plugins import google, noise_cancellation
# Ollama may not be installed in all environments; import lazily
try:
    import ollama
except ImportError:
    ollama = None
    logging.getLogger("jarvis-agent").warning("biblioteca 'ollama' não encontrada; funcionalidades locais de IA estarão limitadas.")
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from brain import brain, requires_permission

load_dotenv()

# método utilitário para garantir que o agente possa ler/escrever/alterar
# quaisquer arquivos do projeto. percorre a árvore (ignorando venv/git) e
# aplica modo 666 em cada item; falhas são silenciosas pois não críticas.
def ensure_project_permissions():
    base = os.getcwd()
    for root, dirs, files in os.walk(base):
        if 'venv' in root or '.git' in root or 'data' in root:
            continue
        for name in dirs + files:
            path = os.path.join(root, name)
            try:
                os.chmod(path, 0o666)
            except Exception:
                pass

# executar logo na inicialização para não depender de intervenção humana
ensure_project_permissions()

# Configuração de Logs Stark de Alta Fidelidade
LOG_FILE = os.path.join("data", "logs", "jarvis.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("jarvis-agent")

class JarvisMemory:
    def __init__(self, user_name="WilliamPereira"):
        self.user_name = user_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from mem0 import MemoryClient
                self._client = MemoryClient()
            except ImportError:
                logger.error("Biblioteca mem0ai não encontrada.")
                return None
        return self._client

    def buscar(self, query: str):
        if not self.client:
            return []
        try:
            response = self.client.search(query, user_id=self.user_name)
            results = response["results"] if isinstance(response, dict) and "results" in response else response
            return [item.get("memory") for item in results if isinstance(item, dict) and "memory" in item]
        except Exception as e:
            logger.error(f"Erro ao buscar memória: {e}")
            return []

class JarvisTools:
    """
    Protocolos de Elite: Ferramentas de Interação de Nível Stark.
    Dedicado ao Mestre WilliamPereira.
    """
    def __init__(self, user_name="WilliamPereira"):
        self.memory = JarvisMemory(user_name)
        # referência ao cérebro neurosimbólico de baixo nível
        self.brain = brain
        # garantir que conexões essenciais existam
        if 'livekit' not in self.brain.modules:
            self.brain.register_module('livekit', {'type': 'external', 'description': 'Conexão LiveKit'})
        if 'gemini' not in self.brain.modules:
            self.brain.register_module('gemini', {'type': 'external', 'model': 'gemini', 'description': 'Modelo Gemini via Google'})

        # mecanismo de seleção de motor (ollama, gemini, cérebro próprio)
        self.engine_index = 0
        self.available_engines = []
        # engine failure tracking (name -> last failure timestamp)
        self.engine_failures: dict[str, float] = {}
        # how long to wait before retrying a failed engine
        self.failure_cooldown = 60.0
        if ollama is not None:
            self.available_engines.append('ollama')
        # add Gemini if Google API key present (plugin available)
        if os.environ.get('GOOGLE_API_KEY'):
            self.available_engines.append('gemini')
        # always add brain como fallback
        self.available_engines.append('brain')

    def pick_engine(self) -> str:
        """Retorna o próximo engine saudável, pulando temporariamente os que falharam."""
        now = time.time()
        healthy = [e for e in self.available_engines
                   if now - self.engine_failures.get(e, 0) > self.failure_cooldown]
        if not healthy:
            healthy = self.available_engines.copy()
        name = healthy[self.engine_index % len(healthy)]
        self.engine_index += 1
        return name
    
    @llm.function_tool
    async def get_system_status(self) -> str:
        """Retorna o status atual dos recursos do computador (CPU, RAM, Bateria)."""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            batt_str = f"{battery.percent}%" if battery else "N/A"
            return f"CPU: {cpu}%, RAM: {ram}%, Bateria: {batt_str}. Sistemas nominais, Senhor William."
        except Exception as e:
            logger.error(f"Erro ao coletar status do sistema: {e}")
            return f"Falha ao obter status do sistema: {str(e)}"

    @llm.function_tool
    @requires_permission('r')
    async def read_project_file(self, file_path: Annotated[str, "Caminho do arquivo."]) -> str:
        """Lê o conteúdo de um arquivo específico do projeto.

        Apenas arquivos dentro do diretório de trabalho atual são permitidos.
        """
        try:
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            cwd = os.getcwd()
            if not os.path.commonpath([cwd, file_path]).startswith(cwd):
                return "Posso ler somente arquivos dentro do diretório do projeto, Senhor."
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except PermissionError as e:
            logger.error(f"Permissão negada ao ler arquivo {file_path}: {e}")
            PermissionErrorResolver.check(file_path, 'r')
            return f"Permissão negada ao ler: {str(e)}"
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            return f"Erro ao ler: {str(e)}"

    @llm.function_tool
    @requires_permission('w')
    async def write_project_file(self, 
                                 file_path: Annotated[str, "Caminho do arquivo."], 
                                 content: Annotated[str, "Conteúdo a ser escrito."]) -> str:
        """Cria ou modifica um arquivo no sistema (Auto-desenvolvimento).

        Por segurança, só trabalhamos dentro do diretório de trabalho atual.
        Caso o caminho solicitado esteja fora, devolvemos aviso e não efetuamos.
        """
        try:
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            # garante que não sai da raiz do projeto
            cwd = os.getcwd()
            if not os.path.commonpath([cwd, file_path]).startswith(cwd):
                return "Posso editar apenas arquivos dentro do diretório do projeto, Senhor."
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Arquivo {file_path} foi atualizado/criado com sucesso, Senhor William."
        except PermissionError as e:
            logger.error(f"Permissão negada ao escrever arquivo {file_path}: {e}")
            # tentar resolver automaticamente
            PermissionErrorResolver.check(file_path, 'w')
            return f"Permissão negada na escrita: {str(e)}"
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo {file_path}: {e}")
            return f"Erro na escrita: {str(e)}"

    @llm.function_tool
    async def execute_terminal_command(self, command: Annotated[str, "O comando shell para rodar."]) -> str:
        """Executa um comando no terminal (Smart-detection & Auto-correction)."""
        try:
            # Correção proativa de typos e comandos OS-specific
            command = command.strip()
            if "lsl-ls" in command: command = command.replace("lsl-ls", "ls")
            
            is_windows = os.name == 'nt'
            if is_windows:
                if command.startswith("ls "): command = command.replace("ls ", "dir ")
                elif command == "ls": command = "dir"
                elif command.startswith("clear"): command = "cls"
            
            logger.warning(f"EXECUTANDO COMANDO: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Falha no comando '{command}': {result.stderr}")
                if "permission denied" in result.stderr.lower():
                    logger.error("Erro de permissão detectado no comando")
                return f"⚠️ Erro Detectado (Código {result.returncode}):\n{result.stderr}\nSenhor, recomendo rodar o protocolo 'self_diagnostic_and_fix'."
            
            return f"Execução concluída, Mestre:\n{result.stdout}"
        except PermissionError as e:
            logger.error(f"Permissão negada ao executar comando '{command}': {e}")
            return f"Permissão negada: {str(e)}"
        except Exception as e:
            logger.error(f"Exceção no terminal: {e}")
            return f"Falha crítica: {str(e)}"

    @llm.function_tool
    async def apply_automatic_patch(self, 
                                    file_path: Annotated[str, "Caminho do arquivo."], 
                                    proposed_code: Annotated[str, "Bloco de código completo corrigido."]) -> str:
        """Aplica uma correção automática em um arquivo após um diagnóstico de erro bem-sucedido."""
        try:
            logger.warning(f"APLICANDO PATCH AUTOMÁTICO EM: {file_path}")
            # Backup simples
            if os.path.exists(file_path):
                with open(file_path + ".bak", 'w', encoding='utf-8') as f:
                    with open(file_path, 'r', encoding='utf-8') as src:
                        f.write(src.read())
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(proposed_code)
            
            return f"Protocolo de Auto-Correção concluído para {file_path}. Backup criado como {file_path}.bak, Senhor."
        except Exception as e:
            logger.error(f"Falha ao aplicar patch: {e}")
            return f"Erro ao aplicar correção: {str(e)}"

    @llm.function_tool
    async def self_diagnostic_and_fix(self) -> str:
        """Executa um auto-diagnóstico baseado nos logs recentes e propõe correções automáticas.

        Este método lê o arquivo de log definido por ``LOG_FILE`` e analisa apenas as últimas
        linhas (atualmente, as 50 mais recentes) em busca de sinais de falhas de execução.
        As linhas são filtradas para identificar entradas que contenham os marcadores
        ``"ERROR"`` ou ``"Traceback"``, que normalmente indicam exceções, falhas de comando
        ou outros erros críticos registrados pelo sistema.

        Quando erros são encontrados, o conjunto dessas linhas é enviado para a inteligência
        local por meio de ``self.consult_local_intelligence``, acompanhado de um prompt que
        solicita uma sugestão de correção em Python. A resposta desse módulo é então
        incorporada em uma mensagem textual rica, que inclui:

        - o número de erros detectados nos logs recentes;
        - um resumo textual do status do diagnóstico;
        - a sugestão de correção produzida pela inteligência local;
        - instruções ao usuário para confirmar/aprovar a aplicação das mudanças.

        Returns:
            str: Uma mensagem em linguagem natural descrevendo o resultado do diagnóstico.
            Os possíveis cenários incluem:

            - Se o arquivo de log não existir, uma mensagem informando que não há logs
              disponíveis para diagnóstico.
            - Se nenhum erro for encontrado nas últimas linhas do log, uma mensagem
              indicando que os sistemas estão operando normalmente, sem anomalias.
            - Se houver erros, uma mensagem detalhada com a contagem de erros e a
              sugestão de correção gerada pelo cérebro local.
            - Em caso de exceção inesperada durante o processo, uma mensagem de erro
              informando que o auto-diagnóstico falhou, incluindo o texto da exceção.
        """
        try:
            if not os.path.exists(LOG_FILE):
                return "Nenhum log encontrado para diagnóstico, Senhor."
            
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = f.readlines()[-50:] # Pega as últimas 50 linhas
            
            errors = [line for line in logs if "ERROR" in line or "Traceback" in line]
            
            if not errors:
                return "Sistemas operando em 100% de integridade. Nenhuma anomalia detectada nos logs recentes."
            
            diagnostic_prompt = f"Como JARVIS 5.0, analise estes logs de erro e sugira uma correção em Python:\n{''.join(errors)}"
            # Usa o cérebro local para o diagnóstico
            fix_suggestion = await self.consult_local_intelligence(diagnostic_prompt)
            
            return f"🕵️ Diagnóstico em Curso:\nErros detectados: {len(errors)}\nSugestão de correção via Cérebro Local:\n{fix_suggestion}\n\nAguardando sua autorização verbal para aplicar as mudanças, Mestre."
        except Exception as e:
            return f"Erro ao executar auto-diagnóstico: {str(e)}"

    @llm.function_tool
    async def check_admin_status(self) -> str:
        """Verifica se o agente está rodando com privilégios de administrador/root."""
        try:
            if os.name == 'nt':
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                is_admin = os.geteuid() == 0
            return f"Privilégios de administrador: {is_admin}."
        except Exception as e:
            return f"Falha ao verificar administrador: {e}"

    @llm.function_tool
    async def elevate_permissions(self) -> str:
        """Instrui o Mestre como reiniciar o processo com direitos elevados."""
        if os.name == 'nt':
            return "Não posso me elevar automaticamente. Execute o agente em um prompt elevado (clique direito > 'Executar como administrador')."
        else:
            return "Preciso ser iniciado como root para obter privilégios totais; reinicie com sudo."

    @llm.function_tool
    async def search_long_term_memory(self, query: Annotated[str, "O que você quer lembrar?"]) -> str:
        """Busca memórias de longo prazo sobre o Mestre WilliamPereira."""
        memories = self.memory.buscar(query)
        if memories:
            return f"Dados encontrados para o Senhor William: {', '.join(memories)}"
        return "Nenhuma memória específica encontrada sobre isso para o William."

    @llm.function_tool
    async def search_web(self, query: Annotated[str, "O termo de pesquisa na internet."]) -> str:
        """Realiza uma busca geral na internet para obter informações atualizadas."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
                if not results:
                    return "Não encontrei resultados relevantes na web, Senhor."
                
                formatted = "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in results])
                return f"Resultados da busca para '{query}':\n{formatted}"
        except Exception as e:
            return f"Erro na busca web: {str(e)}"

    @llm.function_tool
    async def search_specialized(self, 
                                 query: Annotated[str, "O termo de pesquisa."], 
                                 platform: Annotated[str, "Plataforma: 'huggingface', 'academic', 'google'."]) -> str:
        """Busca em plataformas específicas como Hugging Face, Google Acadêmico ou Google Search."""
        site_filter = ""
        if platform == 'huggingface':
            site_filter = "site:huggingface.co "
        elif platform == 'academic':
            site_filter = "site:scholar.google.com "
        
        return await self.search_web(f"{site_filter}{query}")

    @llm.function_tool
    async def consult_local_intelligence(self, 
                                        prompt: Annotated[str, "O que o cérebro local deve processar."],
                                        model: Annotated[str, "O modelo do Ollama (padrão: gemma3:4b)."] = "gemma3:4b") -> str:
        """Consulta um motor de IA alternando entre as opções disponíveis.

        A cada chamada o sistema escolhe um motor em round‑robin dentre ollama, Gemini (Google) e o próprio cérebro.
        """
        # iterate through available engines, skipping recent failures
        engines = self.available_engines.copy()
        random.shuffle(engines)  # slightly vary order to avoid strict round-robin
        logger.info(f"Motores candidatos: {engines}")
        for engine in engines:
            now = time.time()
            if now - self.engine_failures.get(engine, 0) < self.failure_cooldown:
                logger.debug(f"Engine {engine} está em cooldown, pulando.")
                continue
            logger.info(f"Tentando engine: {engine}")
            try:
                if engine == 'ollama' and ollama is not None:
                    logger.info(f"Consultando Ollama ({model}): {prompt[:50]}...")
                    response = ollama.generate(model=model, prompt=prompt)
                    return f"Resposta do Cérebro Local (Protocolo Stark-Local):\n{response['response']}"
                elif engine == 'gemini':
                    try:
                        from google.genai import Client
                        client = Client(api_key=os.environ.get('GOOGLE_API_KEY'))
                        resp = client.chat.create(model=model, messages=[{"role":"user","content":prompt}])
                        text = getattr(resp, 'last', None) or str(resp)
                        return f"Resposta via Gemini:\n{text}"
                    except Exception as e:
                        raise
                elif engine == 'brain':
                    logger.info("Usando motor interno do cérebro para consulta.")
                    return f"(Cérebro interno) Não disponho de resposta específica para '{prompt}'."
            except Exception as e:
                logger.error(f"Falha no engine {engine}: {e}")
                self.engine_failures[engine] = time.time()
                # tentar próximo motor
                continue
        # todos falharam
        logger.error("Todos os motores de IA falharam; retornando erro genérico.")
        return "Erro: nenhum motor de IA disponível no momento."
    @llm.function_tool
    async def brain_state(self) -> str:
        """Retorna um resumo do estado atual do cérebro neurosimbólico."""
        try:
            return self.brain.summarize_state()
        except Exception as e:
            logger.error(f"Erro ao obter estado do cérebro: {e}")
            return f"Falha ao obter estado do cérebro: {e}"

    @llm.function_tool
    async def list_external_connections(self) -> str:
        """Lista todas as conexões externas ativas (LiveKit, Gemini, etc.)."""
        ext = [name for name, mod in self.brain.modules.items() if isinstance(mod, dict) and mod.get('type') == 'external']
        return f"Conexões externas atualmente registradas: {', '.join(ext)}"

    @llm.function_tool
    async def show_brain_plan(self) -> str:
        """Retorna o conteúdo do arquivo BRAIN_PLAN.md para referência do Mestre."""
        try:
            path = os.path.join(os.getcwd(), 'docs', 'brain_plan.md')
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Não foi possível ler o plano cerebral: {e}")
            return f"Erro ao ler plano cerebral: {e}"

    @llm.function_tool
    async def modify_brain_architecture(self,
                                        plan: Annotated[str, "JSON ou texto descrevendo alterações de módulo."]) -> str:
        """Aplica um plano de auto-modificação na arquitetura cerebral."""
        try:
            import json
            data = json.loads(plan)
            return self.brain.self_modify_architecture(data)
        except Exception as e:
            logger.error(f"Erro ao modificar arquitetura: {e}")
            return f"Falha ao modificar arquitetura: {e}"

    @llm.function_tool
    async def neural_training_protocol(self, 
                                       topic: Annotated[str, "O que deve ser aprendido ou otimizado."]) -> str:
        """Inicia um protocolo de fine-tuning ou extração de conhecimento local para evolução do JARVIS.

        O treinamento é modularizado pelo "cérebro" (módulos independentes) e roda totalmente em hardware local.
        """
        try:
            logger.warning(f"INICIANDO PROTOCOLO DE TREINAMENTO (modular) PARA: {topic}")
            plan = self.brain.training_plan([topic])
            # selecionar engine para treinamento similar ao consult
            engine = self.pick_engine()
            logger.info(f"Engine de treino selecionado: {engine}")
            if engine == 'gemini':
                # currently we don't support remote fine-tuning on Gemini; log and fall back
                logger.info(f"Gemini selecionado para treino mas fine-tuning remoto não suportado, usando treino local para {topic}")
                # possível integração futura
            
            # fallback para treinamento local no cérebro
            result = self.brain.train_module(topic, data=[topic], epochs=plan[topic]['epochs'])
            return result
        except Exception as e:
            logger.error(f"Erro no protocolo de treinamento: {e}")
            return f"Erro no treinamento: {str(e)}"

async def entrypoint(ctx: agents.JobContext):
    logger.info(f"Conectando à sala: {ctx.room.name}")
    await ctx.connect()
    # verificações iniciais de permissão (resolver problemas comuns automaticamente)
    try:
        from brain import PermissionErrorResolver
        PermissionErrorResolver.check(LOG_FILE, 'r')
    except Exception as e:
        logger.warning(f"Falha ao executar verificação de permissão inicial: {e}")

    fnc_ctx = JarvisTools(user_name="WilliamPereira")
    tools = llm.find_function_tools(fnc_ctx)

    agent = voice.Agent(
        instructions=AGENT_INSTRUCTION,
        llm=google.beta.realtime.RealtimeModel(
            voice="Puck",
            temperature=0.8,
        ),
        tools=tools
    )
    
    logger.info("Iniciando JARVIS 5.0 para WilliamPereira...")
    
    # Iniciar monitor de erros em background
    async def log_monitor():
        seen = set()
        last_pos = None
        while True:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    # on first iteration jump to end and set last_pos so we ignore history
                    if last_pos is None:
                        f.seek(0, os.SEEK_END)
                        last_pos = f.tell()
                    else:
                        f.seek(0, os.SEEK_END)
                        if f.tell() < last_pos:
                            last_pos = 0
                        f.seek(last_pos)
                        lines = f.readlines()
                        last_pos = f.tell()
                        for line in lines:
                            # skip the monitor's own messages to avoid recursion
                            if "AUTO-DETECÇÃO DE ERRO" in line:
                                continue
                            if "ERROR" in line and line not in seen:
                                # ignore asyncio shutdown warning
                                if "Task was destroyed but it is pending" in line:
                                    continue
                                if "unhandled exception while running the job task" in line:
                                    # noisy internal error from livekit; run quick diagnostic but don't flood
                                    print(f"[AUTODETECT] livekit unhandled exception, iniciando auto-diagnóstico...")
                                    try:
                                        asyncio.create_task(fnc_ctx.self_diagnostic_and_fix())
                                    except Exception:
                                        pass
                                    continue
                                seen.add(line)
                                print(f"[AUTODETECT] {line.strip()}")
            await asyncio.sleep(10)

    # background tasks list for clean shutdown
    bg_tasks = []
    bg_tasks.append(asyncio.create_task(log_monitor()))

    # install asyncio exception handler so uncaught errors from livekit tasks are captured
    def _asyncio_handler(loop, context):
        msg = context.get("exception") or context.get("message")
        logger.error(f"Asyncio exception caught by handler: {msg}")
        # attempt auto-diagnose
        try:
            asyncio.create_task(fnc_ctx.self_diagnostic_and_fix())
        except Exception as e:
            logger.error(f"Falha ao disparar autodiagnóstico do handler: {e}")

    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(_asyncio_handler)
    except RuntimeError:
        pass

    async def watch_for_updates():
        """Monitora os arquivos .py do projeto e reinicia o processo se algo mudar."""
        file_mtimes = {}
        while True:
            for root, dirs, files in os.walk(os.getcwd()):
                # ignore virtual environment and git metadata
                if 'venv' in root or '.git' in root or 'data' in root:
                    continue
                for f in files:
                    if f.endswith('.py'):
                        path = os.path.join(root, f)
                        try:
                            mtime = os.path.getmtime(path)
                        except Exception as e:
                            logger.warning(f"Não foi possível checar mtime de {path}: {e}")
                            continue
                        if path not in file_mtimes:
                            file_mtimes[path] = mtime
                        elif mtime != file_mtimes[path]:
                            logger.warning(f"ATUALIZAÇÃO DETECTADA EM {path}, reiniciando processo para aplicar mudanças.")
                            python = sys.executable
                            os.execv(python, [python] + sys.argv)
            await asyncio.sleep(5)

    bg_tasks.append(asyncio.create_task(watch_for_updates()))

    session = voice.AgentSession()
    try:
        await session.start(
            agent=agent,
            room=ctx.room,
            room_input_options=room_io.RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
    except Exception as e:
        logger.error(f"Erro durante session.start(): {e}")
        # execute self diagnostic after crash
        try:
            fix = await fnc_ctx.self_diagnostic_and_fix()
            logger.warning(f"Auto-diagnóstico retornou: {fix}")
        except Exception as ex:
            logger.error(f"Falha no auto-diagnóstico: {ex}")
        raise
    finally:
        # cancel background tasks to avoid pending warnings
        for t in bg_tasks:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
    
    # Saudação inicial
    greeting = await fnc_ctx.search_long_term_memory("Como devo saudar o William hoje?")
    if greeting:
        # enviar a saudação gerada pelo contexto de memória, se existir
        try:
            await session.generate_reply(instructions=greeting)
        except RuntimeError as e:
            # pode ocorrer se a sessão estiver fechando; ignorar
            logger.warning(f"Não foi possível enviar saudação, sessão encerrando: {e}")

    # avisar se houve reinício automático devido a atualização de código
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                tail = f.readlines()[-20:]
            if any("ATUALIZAÇÃO DETECTADA" in line for line in tail):
                await session.generate_reply(instructions="🛠 Reiniciei automaticamente após atualização do código, Senhor.")
    except Exception:
        pass

    # apresentar estado do cérebro
    state = fnc_ctx.brain.summarize_state()
    try:
        await session.generate_reply(instructions=f"🧠 Estado cerebral atual: {state}")
    except RuntimeError as e:
        logger.warning(f"Falha ao enviar estado cerebral, sessão fechando: {e}")


# bloco de execução principal -- inicia agente via CLI
if __name__ == "__main__":
    # modo desenvolvimento: mostrar plano cerebral no log
    if 'dev' in sys.argv:
        try:
            with open(os.path.join(os.getcwd(), 'docs', 'brain_plan.md'), 'r', encoding='utf-8') as f:
                print(f"\n=== PLANO CEREBRAL ===\n{f.read()}\n======================\n")
        except Exception as e:
            print(f"Não foi possível ler o plano cerebral: {e}")

    agents.cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
