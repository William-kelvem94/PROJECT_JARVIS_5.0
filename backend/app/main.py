from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import datetime
import psutil
from dotenv import load_dotenv
from pathlib import Path
import asyncio
from loguru import logger
from typing import Dict, Any
from contextlib import asynccontextmanager

base_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(base_dir))

from . import routes
from . import voice_websocket
from .utils.dream_processor import dream_processor
from .perception.perception_manager import perception_manager
import asyncio
from loguru import logger
from typing import Dict, Any
from contextlib import asynccontextmanager

load_dotenv(base_dir / '.env')
load_dotenv(base_dir / 'env' / '.env', override=False)

_start_time = datetime.datetime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[Startup] JARVIS 5.0 iniciando...")
    # Inicia Percepção Local
    perception_manager.start()
    asyncio.create_task(dream_processor.dream_loop())
    
    # Tarefa de Telemetria (Heartbeat de Hardware para o HUD)
    async def hardware_telemetry():
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                # Se a RAM estiver alta, avisa no log de atividade
                status = "warning" if ram > 85 else "success"
                detail = f"CPU: {cpu}% | RAM: {ram}%"
                if ram > 85: detail += " [MODO ANTIGRAVIDADE ATIVO]"
                
                # Opcional: Enviar via sistema de log que já temos
                from .utils.log_manager import log_manager
                log_manager.save_log({
                    "type": "telemetry",
                    "cpu": cpu,
                    "ram": ram,
                    "status": status,
                    "timestamp": datetime.datetime.now().isoformat()
                })
            except: pass
            await asyncio.sleep(10) # Atualiza a cada 10s para não pesar

    asyncio.create_task(hardware_telemetry())
    
    yield
    logger.info("[Shutdown] Finalizando serviços...")
    perception_manager.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(voice_websocket.router)

@app.get("/health") # type: ignore
def health_check() -> Dict[str, Any]:
    uptime = int((datetime.datetime.now() - _start_time).total_seconds())
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    }

@app.get("/status") # type: ignore
def status_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "livekit": bool(os.getenv("LIVEKIT_URL") and os.getenv("LIVEKIT_API_KEY") and os.getenv("LIVEKIT_API_SECRET")),
        "gemini": bool(os.getenv("GOOGLE_API_KEY")),
        "timestamp": datetime.datetime.now().isoformat()
    }

