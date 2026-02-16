import logging
import asyncio
import json
import re
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import uvicorn
import glob

logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS 5.0 - Control Dashboard")

# Segurança básica
security = HTTPBearer()
API_KEY = secrets.token_urlsafe(32)  # Gerar chave única por sessão
logger.info(f"🔑 API Key gerada: {API_KEY[:8]}...")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica a API key no header Authorization"""
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

def sanitize_input(text: str) -> str:
    """Sanitiza input para prevenir XSS e injection"""
    if not isinstance(text, str):
        return ""
    # Remove tags HTML e caracteres perigosos
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[;&|`$]', '', text)
    return text.strip()

# Caminho para os arquivos estÃ¡ticos
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Lista de clientes WebSocket conectados
connected_clients = set()

# Rota para o Dashboard Principal
@app.get("/")
async def get_dashboard():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        # Criar um index bÃ¡sico provisÃ³rio se nÃ£o existir
        return HTMLResponse("<h1>JARVIS Web Dashboard - Aguardando Front-end</h1>")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# API para dados de treinamento
@app.get("/api/training-data")
async def get_training_data(api_key: str = Depends(verify_api_key)):
    """Retorna dados de treinamento disponÃ­veis"""
    try:
        # Caminho para dados de treinamento
        training_dir = Path(__file__).parent.parent.parent / "data" / "learning" / "training_data"
        
        if not training_dir.exists():
            return JSONResponse(content=[], status_code=200)
        
        training_files = list(training_dir.glob("*.json"))
        training_data = []
        
        for file_path in training_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Sanitizar dados antes de retornar
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, str):
                                data[key] = sanitize_input(value)
                    training_data.append(data)
            except Exception as e:
                logger.error(f"Erro ao carregar {file_path}: {e}")
        
        return JSONResponse(content=training_data)
    
    except Exception as e:
        logger.error(f"Erro ao carregar dados de treinamento: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# WebSocket para Logs e Telemetria em Tempo Real
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Manter a conexÃ£o viva (ping/pong implÃ­cito do FastAPI)
            data = await websocket.receive_text()
            # Opcional: processar comandos vindos da web
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# FunÃ§Ã£o auxiliar para broadcast de mensagens (chamada pelo main.py)
async def broadcast_message(message: dict):
    if not connected_clients:
        return
    msg_json = json.dumps(message)
    # Criar lista para evitar RuntimeError: set size changed during iteration
    for client in list(connected_clients):
        try:
            await client.send_text(msg_json)
        except Exception:
            connected_clients.remove(client)

def start_server(host="0.0.0.0", port=5000):
    logger.info(f"ðŸŒ Iniciando Web Dashboard em http://{host}:{port}")
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    return server
