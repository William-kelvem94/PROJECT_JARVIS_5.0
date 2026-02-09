import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS 5.0 - Control Dashboard")

# Caminho para os arquivos estáticos
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Lista de clientes WebSocket conectados
connected_clients = set()

# Rota para o Dashboard Principal
@app.get("/")
async def get_dashboard():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        # Criar um index básico provisório se não existir
        return HTMLResponse("<h1>JARVIS Web Dashboard - Aguardando Front-end</h1>")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# WebSocket para Logs e Telemetria em Tempo Real
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Manter a conexão viva (ping/pong implícito do FastAPI)
            data = await websocket.receive_text()
            # Opcional: processar comandos vindos da web
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# Função auxiliar para broadcast de mensagens (chamada pelo main.py)
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
    logger.info(f"🌐 Iniciando Web Dashboard em http://{host}:{port}")
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    return server
