"""
API Principal do JARVIS COMPLETO
Expõe o JARVIS completo via FastAPI para uso através da web
"""

from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.logger import logger
import os
import json
import asyncio

# Importar JARVIS Completo
from jarvis_complete import JarvisComplete

# Configuração do FastAPI
app = FastAPI(
    title="JARVIS Completo API",
    description="Assistente Pessoal Virtual Completo - API",
    version="5.0-COMPLETE",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar JARVIS Completo
logger.info("🚀 Inicializando JARVIS COMPLETO...")
try:
    jarvis = JarvisComplete(
        enable_voice=False,  # Desabilitar voz no servidor (usar via endpoint separado)
        enable_security=True,
        enable_semantic_memory=True
    )
    logger.info("✅ JARVIS COMPLETO inicializado com sucesso!")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar JARVIS COMPLETO: {e}")
    jarvis = None

# Servir arquivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), 'web')
if os.path.exists(static_dir):
    static_subdir = os.path.join(static_dir, 'static')
    if os.path.exists(static_subdir):
        app.mount("/static", StaticFiles(directory=static_subdir), name="static")
    else:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Servir index.html
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Página principal do JARVIS."""
    index_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JARVIS Completo</title>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    padding: 40px;
                    backdrop-filter: blur(10px);
                }
                h1 {
                    text-align: center;
                    font-size: 3em;
                    margin-bottom: 10px;
                }
                .subtitle {
                    text-align: center;
                    font-size: 1.2em;
                    opacity: 0.9;
                    margin-bottom: 40px;
                }
                .chat-box {
                    background: rgba(255,255,255,0.2);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    max-height: 400px;
                    overflow-y: auto;
                }
                .message {
                    margin: 10px 0;
                    padding: 15px;
                    border-radius: 10px;
                }
                .user-message {
                    background: rgba(102, 126, 234, 0.5);
                    text-align: right;
                }
                .jarvis-message {
                    background: rgba(118, 75, 162, 0.5);
                }
                .input-box {
                    display: flex;
                    gap: 10px;
                }
                input {
                    flex: 1;
                    padding: 15px;
                    border: none;
                    border-radius: 10px;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    font-size: 16px;
                }
                input::placeholder {
                    color: rgba(255,255,255,0.6);
                }
                button {
                    padding: 15px 30px;
                    border: none;
                    border-radius: 10px;
                    background: rgba(255,255,255,0.3);
                    color: white;
                    font-size: 16px;
                    cursor: pointer;
                    transition: background 0.3s;
                }
                button:hover {
                    background: rgba(255,255,255,0.4);
                }
                .status {
                    text-align: center;
                    margin: 20px 0;
                    opacity: 0.8;
                }
                .links {
                    text-align: center;
                    margin-top: 20px;
                }
                .links a {
                    color: white;
                    text-decoration: none;
                    margin: 0 15px;
                    opacity: 0.8;
                    transition: opacity 0.3s;
                }
                .links a:hover {
                    opacity: 1;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 JARVIS Completo</h1>
                <div class="subtitle">Seu Assistente Pessoal Virtual</div>
                
                <div class="status" id="status">Conectando...</div>
                
                <div class="chat-box" id="chatBox"></div>
                
                <div class="input-box">
                    <input type="text" id="messageInput" placeholder="Digite seu comando...">
                    <button onclick="sendMessage()">Enviar</button>
                </div>
                
                <div class="links">
                    <a href="/api/docs">📚 API Docs</a>
                    <a href="/api/status">📊 Status</a>
                </div>
            </div>
            
            <script>
                const chatBox = document.getElementById('chatBox');
                const messageInput = document.getElementById('messageInput');
                const statusDiv = document.getElementById('status');
                
                // Verificar status
                async function checkStatus() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        if (data.pronto_para_uso) {
                            statusDiv.textContent = '✅ JARVIS Online e Pronto';
                            statusDiv.style.color = '#4ade80';
                        } else {
                            statusDiv.textContent = '⚠️ JARVIS Parcialmente Online';
                            statusDiv.style.color = '#fbbf24';
                        }
                    } catch (e) {
                        statusDiv.textContent = '❌ JARVIS Offline';
                        statusDiv.style.color = '#f87171';
                    }
                }
                
                // Enviar mensagem
                async function sendMessage() {
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    // Adicionar mensagem do usuário
                    addMessage(message, 'user');
                    messageInput.value = '';
                    
                    // Mostrar "pensando"
                    const thinkingDiv = addMessage('Pensando...', 'jarvis');
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message})
                        });
                        
                        const data = await response.json();
                        
                        // Remover "pensando" e adicionar resposta
                        thinkingDiv.remove();
                        addMessage(data.response, 'jarvis');
                        
                    } catch (e) {
                        thinkingDiv.textContent = 'Erro ao processar comando';
                    }
                }
                
                function addMessage(text, type) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${type}-message`;
                    messageDiv.textContent = text;
                    chatBox.appendChild(messageDiv);
                    chatBox.scrollTop = chatBox.scrollHeight;
                    return messageDiv;
                }
                
                // Enter para enviar
                messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') sendMessage();
                });
                
                // Verificar status ao carregar
                checkStatus();
                setInterval(checkStatus, 30000);
                
                // Mensagem de boas-vindas
                setTimeout(() => {
                    addMessage('Olá! Eu sou o JARVIS, seu assistente pessoal virtual. Como posso ajudar?', 'jarvis');
                }, 500);
            </script>
        </body>
        </html>
        """)

# ========== API ENDPOINTS ==========

@app.get("/api/status")
async def get_status():
    """Retorna status completo do JARVIS."""
    if not jarvis:
        return JSONResponse({
            "status": "error",
            "message": "JARVIS não inicializado",
            "pronto_para_uso": False
        }, status_code=503)
    
    status = jarvis.get_status()
    return JSONResponse({
        "status": "online",
        "version": "5.0-COMPLETE",
        **status
    })

@app.post("/api/chat")
async def chat(request: Request):
    """Endpoint principal de chat - processa comandos."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Mensagem vazia")
        
        # Processar comando com JARVIS
        response = await jarvis.process_command(message)
        
        return JSONResponse({
            "response": response,
            "timestamp": str(asyncio.get_event_loop().time())
        })
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-task")
async def execute_task(request: Request):
    """Executa tarefa complexa."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        data = await request.json()
        task_description = data.get("task", "")
        
        # Executar tarefa
        response = await jarvis.process_command(task_description)
        
        return JSONResponse({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Erro ao executar tarefa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/history")
async def get_memory_history(limit: int = 50):
    """Retorna histórico de conversas."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        history = jarvis.memory.get_conversation_history(limit=limit)
        return JSONResponse({
            "history": history,
            "total": len(history)
        })
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/stats")
async def get_memory_stats():
    """Retorna estatísticas da memória."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        stats = jarvis.memory.get_stats()
        return JSONResponse(stats)
    except Exception as e:
        logger.error(f"Erro ao buscar stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/file/organize")
async def organize_files(request: Request):
    """Organiza arquivos em uma pasta."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        data = await request.json()
        path = data.get("path", ".")
        
        # Executar organização
        result = jarvis.file_manager.organize_files_by_type(path)
        
        return JSONResponse({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Erro ao organizar arquivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def list_tasks():
    """Lista tarefas."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        tasks = jarvis.task_manager.list_tasks()
        return JSONResponse({
            "tasks": tasks,
            "total": len(tasks)
        })
    except Exception as e:
        logger.error(f"Erro ao listar tarefas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks")
async def create_task(request: Request):
    """Cria nova tarefa."""
    if not jarvis:
        raise HTTPException(status_code=503, detail="JARVIS não disponível")
    
    try:
        data = await request.json()
        title = data.get("title", "")
        description = data.get("description", "")
        
        jarvis.task_manager.create_task(title, description)
        
        return JSONResponse({
            "success": True,
            "message": f"Tarefa '{title}' criada"
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket para chat em tempo real
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicação em tempo real."""
    await websocket.accept()
    logger.info("WebSocket conectado")
    
    try:
        while True:
            # Receber mensagem
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")
            
            if not message:
                continue
            
            # Processar com JARVIS
            response = await jarvis.process_command(message)
            
            # Enviar resposta
            await websocket.send_json({
                "response": response,
                "timestamp": str(asyncio.get_event_loop().time())
            })
            
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
    finally:
        logger.info("WebSocket desconectado")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "jarvis_ready": jarvis is not None
    })

# Startup event
@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar o servidor."""
    logger.info("="*60)
    logger.info("🚀 JARVIS COMPLETO - Servidor Iniciado")
    logger.info("="*60)
    logger.info("📍 Acesse: http://localhost:8000")
    logger.info("📚 API Docs: http://localhost:8000/api/docs")
    logger.info("📊 Status: http://localhost:8000/api/status")
    logger.info("="*60)
    
    if jarvis:
        status = jarvis.get_status()
        logger.info("✅ JARVIS Status:")
        for key, value in status.items():
            logger.info(f"   • {key}: {value}")
    else:
        logger.error("❌ JARVIS não inicializado corretamente!")
    
    logger.info("="*60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
