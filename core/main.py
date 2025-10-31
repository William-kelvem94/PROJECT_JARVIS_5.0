from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.local_llm import LocalLLM
from core.config import Config
from core.logger import logger
from core.command_processor import CommandProcessor
from plugins.system_plugin import SystemPlugin
from plugins.file_plugin import FilePlugin
import os
import json
import asyncio

app = FastAPI(title="JARVIS IA", description="Assistente IA Local com Ollama", version="5.0")

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
    logger.info(f"JARVIS inicializado com modelo: {ollama_model}")
except Exception as e:
    logger.error(f"Erro ao inicializar LLM: {e}")
    llm = None

# Inicializar plugins
system_plugin = SystemPlugin()
file_plugin = FilePlugin()
command_processor = CommandProcessor()

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
        
        system = data.get("system", "Você é JARVIS, um assistente de IA inteligente e útil.")
        response = llm.generate(prompt, system=system)
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
            
            if not llm:
                await websocket.send_json({
                    "type": "message",
                    "content": "Erro: LLM não disponível. Verifique a conexão com Ollama."
                })
                continue
            
            # Processar comandos primeiro
            command = command_processor.process(message)
            if command:
                result = await execute_command(command)
                if result:
                    await websocket.send_json(result)
                    # Continuar com resposta do LLM também
                else:
                    continue
            
            # Gerar resposta do LLM com streaming
            system_prompt = """Você é JARVIS, um assistente de IA inteligente e útil.
Você pode controlar o computador do usuário, abrir aplicativos, organizar arquivos e muito mais.
Seja direto, útil e amigável. Use emojis quando apropriado."""
            
            # Resposta rápida otimizada
            resposta = llm.generate(message, system=system_prompt, max_tokens=200, temperature=0.7)
            
            await websocket.send_json({
                "type": "message",
                "content": resposta
            })
            
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        try:
            await websocket.close()
        except:
            pass
