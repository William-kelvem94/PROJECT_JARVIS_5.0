"""
JARVIS 5.0 - Ponto de entrada principal do backend
Inicializa todos os serviços: percepção, telemetria, segundo cérebro, loop autônomo.
"""

import sys
import os
import asyncio
import threading
import psutil
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Garantir que backend/app está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes import router
from app.voice_websocket import voice_router
from app.telemetry_server import start_telemetry_server
from app.utils.second_brain_connector import second_brain
from app.utils.obsidian_graph import obsidian_graph
from app.utils.learning_manager import learning_manager
from app.utils.db_manager import db_manager
from app.autonomous_brain import autonomous_brain
from app.perception.perception_manager import perception_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida do servidor."""
    logger.info("[Startup] JARVIS 5.0 iniciando...")

    # Inicializar segundo cérebro e grafo
    obsidian_graph.build_graph(str(second_brain.vault_path))
    logger.info(f"[Startup] Grafo do Obsidian construído com {len(obsidian_graph.graph.nodes)} nós")

    # Inicializar percepção
    perception_manager.start()
    logger.info("[Startup] Percepção iniciada")

    # Inicializar loop autônomo
    threading.Thread(target=autonomous_brain.start_background_thinking, daemon=True).start()

    # Inicializar telemetria (porta 8001)
    start_telemetry_server()

    yield

    # Shutdown
    logger.info("[Shutdown] Encerrando JARVIS...")
    perception_manager.stop()
    autonomous_brain.stop()


app = FastAPI(title="JARVIS 5.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(router)
app.include_router(voice_router, prefix="/ws")


# === Tarefa de fundo: Telemetria e limpeza do banco ===
async def hardware_telemetry():
    """Coleta métricas periódicas e limpa registros antigos."""
    from app.utils.db_manager import db_manager

    while True:
        await asyncio.sleep(15)

        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            db_manager.save_telemetry(cpu, ram)

            # Limpeza a cada 2 minutos, mantém últimos 500 registros
            now = __import__('datetime').datetime.now()
            if now.minute % 2 == 0 and now.second < 20:
                conn = db_manager._get_conn()
                conn.execute(
                    """
                    DELETE FROM telemetry
                    WHERE id NOT IN (
                        SELECT id FROM telemetry ORDER BY id DESC LIMIT 500
                    )
                    """
                )
                conn.commit()
                logger.debug("[Telemetria] Limpeza de registros antigos concluída")
        except Exception as e:
            logger.warning(f"[Telemetria] Erro na coleta: {e}")


@app.on_event("startup")
async def startup():
    asyncio.create_task(hardware_telemetry())
    logger.info("[Telemetria] Coleta de hardware iniciada")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
