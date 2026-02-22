import os
import typing
import logging
import asyncio
import json
import re
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import uvicorn
import glob
import aiofiles
import time

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
except ImportError:
    FastAPI = None

# Create FastAPI `app` when fastapi is installed so decorators and imports work
app: typing.Optional["FastAPI"] = None
if FastAPI is not None:
    app = FastAPI(title="JARVIS 5.0 - Control Dashboard")

# Toggle actual server startup via environment variable. Routes remain
# defined for tests/imports.
ENABLE_WEB_SERVER = os.environ.get("JARVIS_ENABLE_WEBSERVER", "0") == "1"

# Segurança básica
security = HTTPBearer()
API_KEY = secrets.token_urlsafe(32)  # Gerar chave única por sessão
logger.info("🔑 API Key gerada com sucesso.")
START_TIME = time.time()


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
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[;&|`$]", "", text)
    return text.strip()


# Caminho para os arquivos estáticos
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Lista de clientes WebSocket conectados
connected_clients = set()


# Rotas só são definidas se app estiver ativo
if app is not None:

    @app.get("/")
    async def get_dashboard():
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            # Criar um index básico provisório se não existir
            return HTMLResponse("<h1>JARVIS Web Dashboard - Aguardando Front-end</h1>")
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())


# Unauthenticated health endpoint used by DeploymentManager / Docker
# HEALTHCHECK
@app.get("/health")
async def health():
    """Lightweight unauthenticated health check for orchestration tools."""
    uptime = time.time() - START_TIME
    return JSONResponse(content={"status": "ok", "uptime_seconds": round(uptime, 2)})


# API para dados de treinamento
@app.get("/api/training-data")
async def get_training_data():
    """Retorna dados de treinamento disponíveis (PÚBLICO para Dashboard Local)"""
    try:
        # Caminho para dados de treinamento
        training_dir = (
            Path(__file__).parent.parent.parent / "data" / "learning" / "training_data"
        )

        if not training_dir.exists():
            return JSONResponse(content=[], status_code=200)

        # Use run_in_executor for glob since it performs filesystem I/O
        pattern = str(training_dir / "*.json")
        training_files = await asyncio.to_thread(glob.glob, pattern)

        async def process_file(file_path):
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    data = json.loads(content)
                    # Sanitizar dados antes de retornar
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, str):
                                data[key] = sanitize_input(value)
                    return data
            except Exception as e:
                logger.error(f"Erro ao carregar {file_path}: {e}")
                return None

        # Process files concurrently
        tasks = [process_file(fp) for fp in training_files]
        results = await asyncio.gather(*tasks)
        training_data = [r for r in results if r is not None]

        return JSONResponse(content=training_data)

    except Exception as e:
        logger.error(f"Erro ao carregar dados de treinamento: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


# WebSocket para Logs, Telemetria e Comandos em Tempo Real
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(f"🔌 Novo HUD conectado via WebSocket: {client_host}")
    connected_clients.add(websocket)
    try:
        # Enviar mensagem de boas vindas
        await websocket.send_text(
            json.dumps(
                {
                    "type": "log",
                    "message": "Conexão Stark estabelecida.",
                    "level": "INFO",
                }
            )
        )

        async def telemetry_loop():
            import psutil

            while True:
                try:
                    cpu = psutil.cpu_percent(interval=0.5)
                    mem = psutil.virtual_memory().percent
                    await websocket.send_text(
                        json.dumps({"type": "telemetry", "cpu": cpu, "memory": mem})
                    )
                    await asyncio.sleep(1.0)
                except Exception as e:
                    logger.error(f"Erro no envio de telemetria: {e}")
                    break

        telemetry_task = asyncio.create_task(telemetry_loop())

        while True:
            try:
                data = await websocket.receive_text()
                # Opcional: processar comandos vindos da web
                # Exemplo: comandos de voz/texto podem ser tratados aqui
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Erro no WebSocket: {e}")
                break

        telemetry_task.cancel()
        try:
            await telemetry_task
        except Exception:
            pass
    finally:
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
    """Start the web dashboard server only if ENABLE_WEB_SERVER is true.

    Returns a uvicorn.Server instance when enabled, otherwise returns None.
    """
    if not ENABLE_WEB_SERVER:
        logger.warning(
            "🌐 Web dashboard disabled (set JARVIS_ENABLE_WEBSERVER=1 to enable)."
        )
        return None

    if app is None:
        raise RuntimeError("FastAPI is not available; cannot start web server.")

    logger.info(f"🌐 Iniciando Web Dashboard em http://{host}:{port}")
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    return server


# Backwards compatibility: some callers expect start_web_server
def start_web_server(*args, **kwargs):
    """Compatibilidade retroativa: chama `start_server`"""
    return start_server(*args, **kwargs)
