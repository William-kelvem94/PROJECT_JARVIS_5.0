import os
import datetime
import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .config import settings
from . import routes
from .utils.dream_processor import dream_processor
import asyncio
from loguru import logger

# Carrega variáveis de ambiente de arquivos .env, incluindo caminho absoluto para garantir consistência de cwd
from pathlib import Path
base_dir = Path(__file__).resolve().parents[2]  # PROJECT_JARVIS_5.0
load_dotenv(base_dir / '.env')
load_dotenv(base_dir / 'env' / '.env', override=False)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Carrega Knowledge Base no startup
    from .kb_loader import load_kb
    kb_count = await load_kb()
    
    # Inicia o processamento de sonhos em background
    asyncio.create_task(dream_processor.dream_loop())
    logger.info(f"[Startup] KB carregada ({kb_count} fatos). Ciclo de Evolução iniciado.")

# Allow CORS from frontend origin (adjust as needed)
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url] if frontend_url != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include API routes
app.include_router(routes.router)

@app.get("/health")
def health_check():
    """Lightweight health check used by the process monitor."""
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime_seconds": int((datetime.datetime.now() - _start_time).total_seconds()),
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
    }

@app.get("/status")
def status_check():
    """Detailed status — checks connectivity to LiveKit and local memory."""
    checks = {}

    # Local memory
    try:
        from .local_memory import local_memory
        stats = local_memory.get_stats("Chefe")
        checks["local_memory"] = {"ok": True, "total_memories": stats.get("total_memories", 0)}
    except Exception as e:
        checks["local_memory"] = {"ok": False, "error": str(e)}

    # LiveKit env vars present
    checks["livekit_configured"] = bool(
        os.getenv("LIVEKIT_URL") and os.getenv("LIVEKIT_API_KEY") and os.getenv("LIVEKIT_API_SECRET")
    )
    checks["gemini_configured"] = bool(os.getenv("GOOGLE_API_KEY"))

    return {
        "status": "ok",
        "checks": checks,
        "env": {
            "LIVEKIT_URL": os.getenv("LIVEKIT_URL"),
            "LIVEKIT_API_KEY": bool(os.getenv("LIVEKIT_API_KEY")),
            "LIVEKIT_API_SECRET": bool(os.getenv("LIVEKIT_API_SECRET")),
            "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
            "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
            "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
        },
        "timestamp": datetime.datetime.now().isoformat(),
    }

_start_time = datetime.datetime.now()
