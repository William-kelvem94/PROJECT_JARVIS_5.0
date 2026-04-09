from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import datetime
import psutil
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(base_dir))

from . import routes
from .utils.dream_processor import dream_processor
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
    asyncio.create_task(dream_processor.dream_loop())
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

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

