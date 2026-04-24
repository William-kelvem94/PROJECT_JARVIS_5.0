from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# 1. CARGA IMEDIATA DO AMBIENTE (Crucial para os imports subsequentes)
base_dir = Path(__file__).resolve().parents[2]
load_dotenv(base_dir / '.env')
load_dotenv(base_dir / 'env' / '.env', override=False)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import psutil
import asyncio
from loguru import logger
from typing import Dict, Any
from contextlib import asynccontextmanager

# O uvicorn deve rodar este aplicativo como pacote app.main.
# Removendo a insercao manual de sys.path para evitar importacao de módulos como top-level.

from .config import settings
from . import routes
from . import voice_websocket
from .perception.perception_manager import perception_manager
from .autonomous_brain import autonomous_brain
from .telemetry_server import start_telemetry_server
from .utils.second_brain_connector import second_brain
from .utils.obsidian_graph import ObsidianGraph

_start_time = datetime.datetime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[Startup] JARVIS 5.0 iniciando...")
    logger.info("[Startup] JARVIS 5.0 iniciando...")
    # Inicia Percepção Local
    perception_manager.start()
    
    # Tarefa de Telemetria (Heartbeat de Hardware para o HUD)
    async def hardware_telemetry():
        from utils.db_manager import db_manager
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                status = "warning" if ram > 85 else "success"
                
                # Salva no SQLite em vez de JSONL para telemetria (muito mais eficiente para dados ruidosos)
                with db_manager.get_connection() as conn:
                    conn.execute(
                        "INSERT INTO telemetry (cpu_usage, ram_usage, status, timestamp) VALUES (?, ?, ?, ?)",
                        (cpu, ram, status, datetime.datetime.now().isoformat())
                    )
                
                # Opcional: Manter apenas os últimos 1000 registros para não crescer infinitamente
                if datetime.datetime.now().minute % 10 == 0: # Limpa a cada 10 min
                     with db_manager.get_connection() as conn:
                        conn.execute("DELETE FROM telemetry WHERE id NOT IN (SELECT id FROM telemetry ORDER BY id DESC LIMIT 1000)")
                        
            except Exception as e:
                logger.error(f"[Telemetry] Erro: {e}")
            await asyncio.sleep(15) # Aumentado para 15s para poupar recursos

    asyncio.create_task(hardware_telemetry())
    
    # Inicia o Modo Autônomo (Background Thinking)
    asyncio.create_task(autonomous_brain.start_background_thinking())

    # Inicia Dashboard de Telemetria (Porta 8001)
    start_telemetry_server()
    
    # Constrói o Grafo do Obsidian inicial
    obsidian_graph = ObsidianGraph(second_brain.vault_path)
    asyncio.create_task(asyncio.to_thread(obsidian_graph.build_graph))
    
    yield
    logger.info("[Shutdown] Finalizando serviços...")
    perception_manager.stop()

app = FastAPI(lifespan=lifespan)

# Configuração de CORS Dinâmica
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(voice_websocket.router)

@app.get("/status") # type: ignore
def status_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "timestamp": datetime.datetime.now().isoformat()
    }

