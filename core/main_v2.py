"""
JARVIS v2 - API Principal com Arquitetura Modular
Integra todos os módulos através do FastAPI
"""

from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.jarvis_v2 import JarvisV2
from core.logger import logger
from modules.processing.orchestrator import MessageType
import os
import json
import asyncio

app = FastAPI(
    title="JARVIS IA v2",
    description="Assistente IA Local Modular com Ollama",
    version="5.0"
)

# CORS para permitir acesso da interface web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar JARVIS v2
try:
    jarvis = JarvisV2(auto_detect_capabilities=True)
    logger.info("✅ JARVIS v2 inicializado")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar JARVIS v2: {e}")
    jarvis = None

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
        return HTMLResponse("<h1>JARVIS IA v2 - Interface não encontrada</h1>")

# API de status
@app.get("/api/status")
async def get_status():
    """Retorna o status completo do sistema."""
    if not jarvis:
        return JSONResponse({
            "status": "error",
            "message": "JARVIS não inicializado"
        }, status_code=503)
    
    status = jarvis.get_status()
    
    # Adicionar status do Ollama
    if jarvis.llm:
        try:
            models = jarvis.llm.list_models()
            status["ollama"] = {
                "connected": True,
                "models": models
            }
        except:
            status["ollama"] = {
                "connected": False
            }
    
    return JSONResponse({
        "status": "online",
        "version": "2.0",
        **status
    })

# API para listar modelos
@app.get("/api/models")
async def list_models():
    """Lista todos os modelos disponíveis no Ollama."""
    if not jarvis or not jarvis.llm:
        raise HTTPException(status_code=503, detail="Ollama não está conectado")
    models = jarvis.llm.list_models()
    return JSONResponse({"models": models})

# API para baixar modelo
@app.post("/api/models/pull")
async def pull_model(model_name: str):
    """Baixa um modelo do Ollama."""
    if not jarvis or not jarvis.llm:
        raise HTTPException(status_code=503, detail="Ollama não está conectado")
    success = jarvis.llm.pull_model(model_name)
    if success:
        return JSONResponse({"message": f"Modelo {model_name} baixado com sucesso!"})
    else:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar modelo {model_name}")

# API de chat
@app.post("/api/chat")
async def chat(request: Request):
    """Endpoint REST para chat."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Mensagem vazia")
        
        # Processar mensagem
        result = await jarvis.process(message, MessageType.TEXT)
        
        return JSONResponse({
            "response": result.get("response", ""),
            "intent": result.get("intent", {}),
            "actions": result.get("actions", [])
        })
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API para adicionar conhecimento ao RAG
@app.post("/api/knowledge")
async def add_knowledge(request: Request):
    """Adiciona conhecimento ao banco RAG."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        data = await request.json()
        text = data.get("text", "")
        metadata = data.get("metadata", {})
        
        if not text:
            raise HTTPException(status_code=400, detail="Texto vazio")
        
        result = jarvis.add_knowledge(text, metadata)
        
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro ao adicionar conhecimento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API para buscar no RAG
@app.get("/api/knowledge/search")
async def search_knowledge(query: str, n_results: int = 5):
    """Busca conhecimento no banco RAG."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        results = jarvis.vector_store.search(query, n_results=n_results)
        return JSONResponse({
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        logger.error(f"Erro ao buscar conhecimento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API para obter capacidades do sistema
@app.get("/api/capabilities")
async def get_capabilities():
    """Retorna capacidades detectadas do sistema."""
    if not jarvis or not jarvis.capability_detector:
        raise HTTPException(status_code=503, detail="Detector de capacidades não disponível")
    
    return JSONResponse(jarvis.capability_detector.get_capabilities())

# WebSocket do chat com streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para chat em tempo real com streaming."""
    await websocket.accept()
    logger.info("Cliente WebSocket conectado")
    
    if not jarvis:
        await websocket.send_json({
            "type": "error",
            "content": "JARVIS não inicializado"
        })
        await websocket.close()
        return
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                # Tentar parsear como JSON
                message_data = json.loads(data)
                message = message_data.get('content', data)
                message_type_str = message_data.get('type', 'text')
            except:
                message = data
                message_type_str = 'text'
            
            # Converter tipo de mensagem
            message_type = MessageType.TEXT
            if message_type_str == 'voice':
                message_type = MessageType.VOICE
            
            logger.info(f"Mensagem recebida ({message_type.value}): {message[:50]}...")
            
            # Processar mensagem
            result = await jarvis.process(message, message_type)
            
            # Enviar resposta
            await websocket.send_json({
                "type": "message",
                "content": result.get("response", ""),
                "intent": result.get("intent", {}),
                "actions": result.get("actions", [])
            })
            
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        try:
            await websocket.close()
        except:
            pass

