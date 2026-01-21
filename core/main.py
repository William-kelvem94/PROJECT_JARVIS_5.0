from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.local_llm import LocalLLM
from core.config import Config
from core.logger import logger
from core.command_processor import CommandProcessor
from core.training_manager import TrainingManager
from core.auto_trainer import AutoTrainer
from core.training_orchestrator import TrainingOrchestrator
from core.web_search import WebSearchIntegration, ResearchAssistant
from core.system_controller import UniversalSystemController, get_system_controller
from core.continuous_training_system import ContinuousTrainingSystem, get_continuous_training_system
from plugins.system_plugin import SystemPlugin
from plugins.file_plugin import FilePlugin
from modules.llm.streaming_llm import StreamingLLM
from modules.memory.persistent_memory import PersistentMemory
from enterprise.ai.continuous_learning import ContinuousLearningLoop
from core.knowledge_base import KnowledgeBase
from core.huggingface_integration import HuggingFaceIntegration
from modules.rag.vector_store import VectorStore
import os
import json
import asyncio

app = FastAPI(title="JARVIS IA", description="Assistente IA Local com Ollama", version="5.0")

# Variáveis globais para treinamento
training_manager = None
auto_trainer = None
training_orchestrator = None
memory = None

# Variáveis globais para pesquisa web
web_search = None
research_assistant = None

# Variáveis globais para controle de sistema e treinamento contínuo
system_controller = None
continuous_training = None

# CORS para permitir acesso da interface web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregar configurações
try:
    config = Config()
    llm_provider = config.get("llm_provider", "ollama")
    ollama_model = os.getenv('OLLAMA_MODEL', config.get("ollama_model", "codellama:7b"))
except Exception as e:
    logger.warning(f"Erro ao carregar config: {e}")
    llm_provider = "ollama"
    ollama_model = "codellama:7b"

# Inicializar LLM com Ollama
try:
    llm = LocalLLM(model=ollama_model)
    streaming_llm = StreamingLLM(llm)
    logger.info(f"JARVIS inicializado com modelo: {ollama_model}")
    
    # Pré-carregar o modelo para evitar demora na primeira requisição
    logger.info("Pré-carregando modelo (isso pode levar 20-30 segundos)...")
    try:
        # Fazer uma requisição de teste para forçar o carregamento do modelo
        test_response = llm.generate("test", max_tokens=5)
        logger.info("✅ Modelo pré-carregado com sucesso!")
    except Exception as preload_error:
        logger.warning(f"Modelo não pôde ser pré-carregado: {preload_error}. Será carregado na primeira requisição.")
except Exception as e:
    logger.error(f"Erro ao inicializar LLM: {e}")
    llm = None
    streaming_llm = None

# Inicializar plugins
system_plugin = SystemPlugin()
file_plugin = FilePlugin()
command_processor = CommandProcessor()

# Inicializar sistema de memória e aprendizado
memory = PersistentMemory()
learning_loop = ContinuousLearningLoop()

# Inicializar Knowledge Base (sistema de conhecimento persistente)
try:
    vector_store = VectorStore()
    knowledge_base = KnowledgeBase(vector_store=vector_store, memory=memory)
    logger.info("✅ Knowledge Base inicializada")
except Exception as e:
    logger.warning(f"Erro ao inicializar Knowledge Base: {e}")
    knowledge_base = None

# Inicializar integração com HuggingFace
try:
    hf_integration = HuggingFaceIntegration()
    logger.info("✅ Integração HuggingFace inicializada")
except Exception as e:
    logger.warning(f"Erro ao inicializar HuggingFace: {e}")
    hf_integration = None

# Inicializar sistema de treinamento
try:
    training_manager = TrainingManager(memory=memory)
    auto_trainer = AutoTrainer(
        training_manager=training_manager,
        learning_loop=learning_loop,
        memory=memory,
        base_model=ollama_model
    )
    # Inicializar Training Orchestrator
    training_orchestrator = TrainingOrchestrator(
        memory=memory,
        ollama_base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    )
    logger.info("✅ Sistema de treinamento inicializado")
except Exception as e:
    logger.warning(f"Erro ao inicializar sistema de treinamento: {e}")
    training_manager = None
    auto_trainer = None
    training_orchestrator = None

# Inicializar Web Search e Research Assistant
try:
    web_search = WebSearchIntegration(
        enable_duckduckgo=True,
        enable_wikipedia=True
    )
    research_assistant = ResearchAssistant(web_search)
    logger.info("✅ Web Search e Research Assistant inicializados")
except Exception as e:
    logger.warning(f"Erro ao inicializar web search: {e}")
    web_search = None
    research_assistant = None

# Inicializar System Controller
try:
    system_controller = get_system_controller()
    logger.info("✅ System Controller inicializado")
except Exception as e:
    logger.warning(f"Erro ao inicializar system controller: {e}")
    system_controller = None

# Inicializar Continuous Training System
try:
    if training_orchestrator and memory:
        continuous_training = get_continuous_training_system(training_orchestrator, memory)
        logger.info("✅ Continuous Training System inicializado")
except Exception as e:
    logger.warning(f"Erro ao inicializar continuous training: {e}")
    continuous_training = None

@app.on_event("startup")
async def startup_event():
    """Inicia tarefas em background na inicialização."""
    if training_orchestrator:
        # Iniciar auto-treinamento via orchestrator
        await training_orchestrator.start_auto_training()
        logger.info("🔄 Training Orchestrator e auto-treinamento iniciados")
    
    # Iniciar continuous training loop
    if continuous_training:
        asyncio.create_task(continuous_training.start_continuous_training_loop())
        logger.info("🔄 Continuous Training Loop iniciado")

# Servir arquivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
static_subdir = os.path.join(static_dir, 'static')
if os.path.exists(static_dir) and os.path.exists(static_subdir):
    app.mount("/static", StaticFiles(directory=static_subdir), name="static")
elif os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Servir o index.html na raiz
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return HTMLResponse("<h1>JARVIS IA - Interface não encontrada</h1>")

# API de status
@app.get("/api/status")
async def get_status():
    """Retorna o status do sistema e modelos disponíveis."""
    try:
        models = llm.list_models() if llm else []
        return JSONResponse({
            "status": "online",
            "llm_provider": llm_provider,
            "current_model": ollama_model,
            "available_models": models,
            "ollama_connected": llm is not None
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# API para listar modelos
@app.get("/api/models")
async def list_models():
    """Lista todos os modelos disponíveis no Ollama."""
    if not llm:
        raise HTTPException(status_code=503, detail="Ollama não está conectado")
    models = llm.list_models()
    return JSONResponse({"models": models})

# API para baixar modelo
@app.post("/api/models/pull")
async def pull_model(model_name: str):
    """Baixa um modelo do Ollama."""
    if not llm:
        raise HTTPException(status_code=503, detail="Ollama não está conectado")
    success = llm.pull_model(model_name)
    if success:
        return JSONResponse({"message": f"Modelo {model_name} baixado com sucesso!"})
    else:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar modelo {model_name}")

# API de treinamento
@app.get("/api/training/status")
async def get_training_status():
    """Retorna status do sistema de treinamento."""
    if not training_manager:
        return JSONResponse({"status": "disabled", "message": "Sistema de treinamento não disponível"})
    
    status = training_manager.get_training_status()
    auto_status = auto_trainer.get_status() if auto_trainer else None
    
    return JSONResponse({
        "training_status": status,
        "auto_trainer": auto_status
    })

@app.post("/api/training/start")
async def start_training(request: Request):
    """Inicia treinamento do modelo."""
    if not training_manager:
        raise HTTPException(status_code=503, detail="Sistema de treinamento não disponível")
    
    try:
        data = await request.json()
        base_model = data.get("base_model", ollama_model)
        custom_name = data.get("custom_name", "jarvis-custom")
        force = data.get("force", False)
        
        # Executar em background
        result = await asyncio.to_thread(
            training_manager.train_model,
            base_model=base_model,
            custom_model_name=custom_name,
            force_retrain=force
        )
        
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro ao iniciar treinamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/training/incremental")
async def start_incremental_training(request: Request):
    """Inicia treinamento incremental."""
    if not training_manager or not auto_trainer:
        raise HTTPException(status_code=503, detail="Sistema de treinamento não disponível")
    
    try:
        result = await auto_trainer.schedule_training(
            reason="manual",
            incremental=True
        )
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro no treinamento incremental: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Novos endpoints do Training Orchestrator
@app.post("/api/training/workflow")
async def start_training_workflow(request: Request):
    """Inicia workflow completo de treinamento (full, incremental, quick)."""
    if not training_orchestrator:
        raise HTTPException(status_code=503, detail="Training Orchestrator não disponível")
    
    try:
        data = await request.json()
        training_type = data.get("type", "full")  # full, incremental, quick
        custom_config = data.get("config", None)
        
        result = await training_orchestrator.start_training_workflow(
            training_type=training_type,
            custom_config=custom_config
        )
        
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro no workflow de treinamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/comprehensive-status")
async def get_comprehensive_training_status():
    """Retorna status completo e detalhado do sistema de treinamento."""
    if not training_orchestrator:
        return JSONResponse({"status": "disabled", "message": "Training Orchestrator não disponível"})
    
    status = training_orchestrator.get_comprehensive_status()
    return JSONResponse(status)

@app.get("/api/training/configs")
async def list_training_configs():
    """Lista todas as configurações de treinamento disponíveis."""
    if not training_orchestrator:
        raise HTTPException(status_code=503, detail="Training Orchestrator não disponível")
    
    configs = training_orchestrator.list_available_configs()
    return JSONResponse({"configs": configs})

@app.post("/api/training/config/load")
async def load_training_config(request: Request):
    """Carrega uma configuração de treinamento específica."""
    if not training_orchestrator:
        raise HTTPException(status_code=503, detail="Training Orchestrator não disponível")
    
    try:
        data = await request.json()
        config_name = data.get("name", "default")
        
        result = training_orchestrator.load_configuration(config_name)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/training/config/update")
async def update_training_config(request: Request):
    """Atualiza configuração de treinamento."""
    if not training_orchestrator:
        raise HTTPException(status_code=503, detail="Training Orchestrator não disponível")
    
    try:
        data = await request.json()
        config_updates = data.get("updates", {})
        save_as = data.get("save_as", "default")
        
        result = training_orchestrator.update_configuration(config_updates, save_as)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/training/dataset/prepare")
async def prepare_training_dataset(request: Request):
    """Prepara dataset para treinamento."""
    if not training_orchestrator:
        raise HTTPException(status_code=503, detail="Training Orchestrator não disponível")
    
    try:
        data = await request.json()
        include_new_only = data.get("include_new_only", False)
        
        result = training_orchestrator.dataset_preparation.prepare_dataset(
            include_new_only=include_new_only
        )
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro ao preparar dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/dataset/stats")
async def get_dataset_stats():
    """Retorna estatísticas do dataset disponível."""
    if not training_orchestrator:
        raise HTTPException(status_code=503, detail="Training Orchestrator não disponível")
    
    stats = training_orchestrator.dataset_preparation.get_statistics()
    return JSONResponse(stats)


# API de Knowledge Base
@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """Retorna estatísticas da base de conhecimento."""
    if not knowledge_base:
        return JSONResponse({"status": "disabled", "message": "Knowledge Base não disponível"})
    
    stats = knowledge_base.get_stats()
    return JSONResponse(stats)

@app.post("/api/knowledge/learn")
async def trigger_learning(request: Request):
    """Dispara aprendizado automático das interações."""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge Base não disponível")
    
    try:
        data = await request.json()
        limit = data.get("limit", 100)
        
        result = await asyncio.to_thread(
            knowledge_base.auto_learn_from_interactions,
            limit=limit
        )
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro ao aprender: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """Busca conhecimento armazenado."""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge Base não disponível")
    
    results = knowledge_base.search_knowledge(query, n_results=limit)
    return JSONResponse({"query": query, "results": results})

# API de HuggingFace
@app.get("/api/huggingface/models/search")
async def search_hf_models(query: str, task: str = None, limit: int = 10):
    """Busca modelos no HuggingFace."""
    if not hf_integration:
        raise HTTPException(status_code=503, detail="Integração HuggingFace não disponível")
    
    models = hf_integration.search_models(query, task, limit)
    return JSONResponse({"query": query, "models": models})

@app.get("/api/huggingface/models/ollama-compatible")
async def get_ollama_compatible_models(query: str = "llm", limit: int = 20):
    """Busca modelos compatíveis com Ollama."""
    if not hf_integration:
        raise HTTPException(status_code=503, detail="Integração HuggingFace não disponível")
    
    models = hf_integration.get_ollama_compatible_models(query, limit)
    return JSONResponse({"models": models})

@app.get("/api/huggingface/models/{model_id}")
async def get_hf_model_info(model_id: str):
    """Obtém informações de um modelo do HuggingFace."""
    if not hf_integration:
        raise HTTPException(status_code=503, detail="Integração HuggingFace não disponível")
    
    info = hf_integration.get_model_info(model_id)
    download_info = hf_integration.download_model_info(model_id)
    return JSONResponse({"info": info, "download": download_info})

@app.post("/api/huggingface/models/suggest")
async def suggest_models(request: Request):
    """Sugere modelos baseado em descrição de tarefa."""
    if not hf_integration:
        raise HTTPException(status_code=503, detail="Integração HuggingFace não disponível")
    
    try:
        data = await request.json()
        task_description = data.get("task", "")
        
        suggestions = hf_integration.suggest_model_for_task(task_description)
        return JSONResponse({"suggestions": suggestions})
    except Exception as e:
        logger.error(f"Erro ao sugerir modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API de Web Search e Research
@app.get("/api/research/search")
async def web_search_endpoint(query: str, num_results: int = 5):
    """Realiza busca na web."""
    if not web_search:
        raise HTTPException(status_code=503, detail="Web search não disponível")
    
    try:
        results = web_search.search(query, num_results)
        return JSONResponse(results)
    except Exception as e:
        logger.error(f"Erro na busca web: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research/query")
async def research_query(request: Request):
    """Realiza pesquisa completa sobre um tópico."""
    if not research_assistant:
        raise HTTPException(status_code=503, detail="Research assistant não disponível")
    
    try:
        data = await request.json()
        query = data.get("query")
        deep_search = data.get("deep_search", False)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query é obrigatório")
        
        results = research_assistant.research(query, deep_search)
        return JSONResponse(results)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na pesquisa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/research/status")
async def research_status():
    """Retorna status do sistema de pesquisa."""
    return JSONResponse({
        "web_search_available": web_search is not None and web_search.is_available(),
        "research_assistant_available": research_assistant is not None,
        "providers": [p.__class__.__name__ for p in web_search.providers] if web_search else []
    })

# API de Controle de Sistema
@app.get("/api/system/info")
async def get_system_info(target: str = 'local'):
    """Retorna informações do sistema (local ou android)."""
    if not system_controller:
        raise HTTPException(status_code=503, detail="System controller não disponível")
    
    try:
        if target == 'all':
            info = system_controller.get_all_system_info()
        else:
            info = system_controller.get_system_info(target)
        return JSONResponse(info)
    except Exception as e:
        logger.error(f"Erro ao obter info do sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/command")
async def execute_system_command(request: Request):
    """Executa comando no sistema."""
    if not system_controller:
        raise HTTPException(status_code=503, detail="System controller não disponível")
    
    try:
        data = await request.json()
        command = data.get("command")
        target = data.get("target", "local")
        
        if not command:
            raise HTTPException(status_code=400, detail="Comando é obrigatório")
        
        result = system_controller.execute_command(command, target)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar comando: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/open-app")
async def open_application(request: Request):
    """Abre aplicativo."""
    if not system_controller:
        raise HTTPException(status_code=503, detail="System controller não disponível")
    
    try:
        data = await request.json()
        app_name = data.get("app_name")
        target = data.get("target", "local")
        
        if not app_name:
            raise HTTPException(status_code=400, detail="app_name é obrigatório")
        
        result = system_controller.open_application(app_name, target)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao abrir aplicativo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/processes")
async def list_processes(target: str = 'local'):
    """Lista processos em execução."""
    if not system_controller:
        raise HTTPException(status_code=503, detail="System controller não disponível")
    
    try:
        processes = system_controller.get_running_processes(target)
        return JSONResponse({"processes": processes})
    except Exception as e:
        logger.error(f"Erro ao listar processos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/kill-process")
async def kill_process(request: Request):
    """Encerra processo."""
    if not system_controller:
        raise HTTPException(status_code=503, detail="System controller não disponível")
    
    try:
        data = await request.json()
        process_name = data.get("process_name")
        target = data.get("target", "local")
        
        if not process_name:
            raise HTTPException(status_code=400, detail="process_name é obrigatório")
        
        result = system_controller.kill_process(process_name, target)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao encerrar processo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/screenshot")
async def take_screenshot(request: Request):
    """Tira screenshot."""
    if not system_controller:
        raise HTTPException(status_code=503, detail="System controller não disponível")
    
    try:
        data = await request.json()
        path = data.get("path", f"./screenshots/screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        target = data.get("target", "local")
        
        # Criar diretório se não existir
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        result = system_controller.take_screenshot(path, target)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao tirar screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API de Treinamento Contínuo
@app.get("/api/continuous-training/status")
async def get_continuous_training_status():
    """Retorna status do sistema de treinamento contínuo."""
    if not continuous_training:
        return JSONResponse({"status": "disabled", "message": "Continuous training não disponível"})
    
    status = continuous_training.get_status()
    return JSONResponse(status)

@app.post("/api/continuous-training/force")
async def force_continuous_training(request: Request):
    """Força treinamento imediato."""
    if not continuous_training:
        raise HTTPException(status_code=503, detail="Continuous training não disponível")
    
    try:
        data = await request.json()
        training_type = data.get("type", "incremental")
        
        result = await continuous_training.force_training(training_type)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao forçar treinamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/continuous-training/enable")
async def enable_continuous_training():
    """Habilita treinamento contínuo."""
    if not continuous_training:
        raise HTTPException(status_code=503, detail="Continuous training não disponível")
    
    continuous_training.enable()
    return JSONResponse({"success": True, "message": "Treinamento contínuo habilitado"})

@app.post("/api/continuous-training/disable")
async def disable_continuous_training():
    """Desabilita treinamento contínuo."""
    if not continuous_training:
        raise HTTPException(status_code=503, detail="Continuous training não disponível")
    
    continuous_training.disable()
    return JSONResponse({"success": True, "message": "Treinamento contínuo desabilitado"})

@app.get("/api/models/registry")
async def get_model_registry():
    """Lista todos os modelos registrados."""
    if not continuous_training:
        raise HTTPException(status_code=503, detail="Continuous training não disponível")
    
    models = continuous_training.model_registry.list_models()
    return JSONResponse({
        "models": models,
        "best_model": continuous_training.model_registry.get_best_model(),
        "active_model": continuous_training.model_registry.get_active_model()
    })

@app.post("/api/models/compare")
async def compare_models(request: Request):
    """Compara dois modelos."""
    if not continuous_training:
        raise HTTPException(status_code=503, detail="Continuous training não disponível")
    
    try:
        data = await request.json()
        model_a = data.get("model_a")
        model_b = data.get("model_b")
        
        if not model_a or not model_b:
            raise HTTPException(status_code=400, detail="model_a e model_b são obrigatórios")
        
        comparison = continuous_training.model_registry.compare_models(model_a, model_b)
        return JSONResponse(comparison)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao comparar modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API de chat
@app.post("/api/chat")
async def chat(request: Request):
    """Endpoint REST para chat."""
    if not llm:
        raise HTTPException(status_code=503, detail="LLM não disponível")
    
    try:
        data = await request.json()
        prompt = data.get("message", "")
        
        # Processar comandos primeiro
        command = command_processor.process(prompt)
        if command:
            result = await execute_command(command)
            if result:
                return JSONResponse(result)
        
        # Salvar mensagem do usuário
        if memory:
            memory.save_conversation("user", prompt)
        
        system = data.get("system", "Você é JARVIS, um assistente de IA inteligente e útil.")
        response = llm.generate(prompt, system=system)
        
        # Salvar resposta do assistente
        if memory:
            memory.save_conversation("assistant", response, metadata={
                "model_used": ollama_model
            })
        
        # Monitorar qualidade
        if auto_trainer:
            await auto_trainer.monitor_interaction(
                user_query=prompt,
                assistant_response=response
            )
        
        return JSONResponse({"response": response})
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_command(command: dict):
    """Executa comandos do sistema."""
    try:
        cmd_type = command['type']
        args = command['args']
        
        if cmd_type == 'open_app':
            app_name = args[0] if args else command['original'].split()[-1]
            result = system_plugin.open_app(app_name)
            return {"type": "action", **result}
        
        elif cmd_type == 'read_file':
            file_path = args[0] if args else None
            if not file_path:
                return None
            result = file_plugin.read_file(file_path)
            return {"type": "action", **result}
        
        elif cmd_type == 'list_files':
            directory = args[0] if args else None
            result = file_plugin.list_directory(directory)
            return {"type": "action", **result}
        
        elif cmd_type == 'organize_files':
            directory = args[0] if args else None
            result = file_plugin.organize_files(directory)
            return {"type": "action", **result}
        
        elif cmd_type == 'system_info':
            result = system_plugin.get_system_info()
            return {"type": "action", **result}
        
        elif cmd_type == 'execute_command':
            cmd = args[0] if args else None
            if not cmd:
                return None
            result = system_plugin.execute_command(cmd)
            return {"type": "action", **result}
        
        return None
    except Exception as e:
        logger.error(f"Erro ao executar comando: {e}")
        return {
            "type": "action",
            "success": False,
            "action": "Erro",
            "result": str(e)
        }

# WebSocket do chat com streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para chat em tempo real com streaming."""
    await websocket.accept()
    logger.info("Cliente WebSocket conectado")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                # Tentar parsear como JSON
                message_data = json.loads(data)
                message = message_data.get('content', data)
            except:
                message = data
            
            logger.info(f"Mensagem recebida: {message}")
            
            if not llm or not streaming_llm:
                await websocket.send_json({
                    "type": "message",
                    "content": "Erro: LLM não disponível. Verifique a conexão com Ollama."
                })
                continue
            
            # Salvar mensagem do usuário na memória persistente
            if memory:
                memory.save_conversation("user", message)
            
            # Processar comandos primeiro
            command = command_processor.process(message)
            if command:
                result = await execute_command(command)
                if result:
                    await websocket.send_json(result)
                    # Continuar com resposta do LLM também (não fazer continue)
            
            # Buscar conhecimento relevante da base de conhecimento
            context = ""
            if knowledge_base:
                context = knowledge_base.get_context_for_query(message, max_results=3)
            
            # Verificar se deve usar pesquisa web
            web_context = ""
            if research_assistant and research_assistant.should_use_web_search(message):
                try:
                    web_context = research_assistant.generate_research_context(
                        message,
                        include_sources=True
                    )
                    logger.info("Adicionando contexto de pesquisa web")
                except Exception as e:
                    logger.error(f"Erro ao buscar na web: {e}")
            
            # Gerar resposta do LLM com STREAMING REAL
            system_prompt = """Você é JARVIS, um assistente de IA inteligente e útil.
Você pode controlar o computador do usuário, abrir aplicativos, organizar arquivos e muito mais.
Seja direto, útil e amigável. Use emojis quando apropriado."""
            
            # Adicionar contexto se disponível
            if context:
                system_prompt += f"\n\nContexto relevante do conhecimento aprendido:\n{context}"
            
            # Adicionar contexto da web se disponível
            if web_context:
                system_prompt += f"\n\n{web_context}"
            
            stream_started = False
            accumulated_response = ""
            
            try:
                # Enviar início do streaming (frontend já mostra indicador de typing)
                await websocket.send_json({
                    "type": "stream_start",
                    "content": ""
                })
                stream_started = True
                
                # Stream tokens conforme são gerados com timeout de segurança
                try:
                    # Usar wait_for para compatibilidade com Python < 3.11
                    async def stream_tokens():
                        nonlocal accumulated_response
                        async for token in streaming_llm.generate_stream_async(
                            message, 
                            system=system_prompt, 
                            max_tokens=200, 
                            temperature=0.7
                        ):
                            accumulated_response += token
                            # Enviar token incremental usando tipo que frontend espera
                            await websocket.send_json({
                                "type": "stream",
                                "content": token
                            })
                    
                    await asyncio.wait_for(stream_tokens(), timeout=120.0)  # Timeout de 120 segundos para dar tempo do modelo carregar
                    
                except asyncio.TimeoutError:
                    logger.error("Timeout no streaming de tokens")
                    if accumulated_response:
                        # Se já tiver algum conteúdo, enviar o que foi gerado
                        accumulated_response += "\n\n⏱️ Tempo limite atingido durante a geração."
                    else:
                        accumulated_response = "⏱️ A resposta está demorando muito. O modelo pode estar processando... Tente novamente."
                
                # Garantir que stream_end sempre seja enviado
                final_response = accumulated_response if accumulated_response else "❌ Erro: Nenhuma resposta foi gerada."
                
                # Salvar resposta do assistente na memória
                if memory:
                    memory.save_conversation("assistant", final_response, metadata={
                        "model_used": ollama_model,
                        "streaming": True
                    })
                
                # Monitorar qualidade e disparar auto-treinamento se necessário
                if auto_trainer and accumulated_response:
                    await auto_trainer.monitor_interaction(
                        user_query=message,
                        assistant_response=final_response
                    )
                
                # Extrair e armazenar conhecimento aprendido
                if knowledge_base and accumulated_response:
                    knowledge_base.extract_and_store_knowledge(
                        user_query=message,
                        assistant_response=final_response
                    )
                
                await websocket.send_json({
                    "type": "stream_end",
                    "content": final_response
                })
                
            except asyncio.TimeoutError:
                logger.error("Timeout ao gerar resposta")
                if stream_started:
                    # Se streaming já começou, finalizar
                    await websocket.send_json({
                        "type": "stream_end",
                        "content": accumulated_response if accumulated_response else "⏱️ A resposta está demorando muito. Tente novamente em alguns segundos."
                    })
                else:
                    await websocket.send_json({
                        "type": "message",
                        "content": "⏱️ A resposta está demorando muito. O modelo pode estar processando... Tente novamente em alguns segundos."
                    })
            except Exception as stream_error:
                logger.error(f"Erro no streaming: {stream_error}")
                
                # Garantir que stream_end seja enviado se streaming começou
                if stream_started:
                    error_msg = str(stream_error)
                    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        error_content = "⏱️ O modelo está demorando muito para responder. Na primeira vez, o modelo precisa ser carregado (leva ~20-30 segundos). Tente novamente em alguns segundos."
                    else:
                        error_content = accumulated_response if accumulated_response else f"❌ Erro ao processar: {error_msg}"
                    
                    await websocket.send_json({
                        "type": "stream_end",
                        "content": error_content
                    })
                else:
                    # Fallback para método não-streaming apenas se streaming não começou
                    try:
                        resposta = llm.generate(message, system=system_prompt, max_tokens=200, temperature=0.7)
                        await websocket.send_json({
                            "type": "message",
                            "content": resposta
                        })
                    except Exception as fallback_error:
                        logger.error(f"Erro no fallback: {fallback_error}")
                        error_msg = str(fallback_error)
                        if "timeout" in error_msg.lower():
                            await websocket.send_json({
                                "type": "message",
                                "content": "⏱️ O modelo está demorando muito. Na primeira requisição, o modelo precisa ser carregado (leva ~20-30 segundos). Aguarde alguns segundos e tente novamente."
                            })
                        else:
                            await websocket.send_json({
                                "type": "message",
                                "content": "❌ Erro ao processar sua mensagem. Verifique se o Ollama está rodando corretamente."
                            })
            
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        try:
            await websocket.close()
        except:
            pass
