import asyncio
import logging
import json

logger = logging.getLogger(__name__)

# Referência global para o servidor web (opcional, se precisarmos de acesso direto)
_web_server_ref = None

def set_web_server(server):
    global _web_server_ref
    _web_server_ref = server

async def emit_log(message: str, level: str = "INFO"):
    """Envia um log para o Dashboard Web"""
    from src.web.web_server import broadcast_message
    await broadcast_message({
        "type": "log",
        "message": message,
        "level": level
    })

async def emit_telemetry(cpu: float, memory: float):
    """Envia dados de telemetria para o Dashboard Web"""
    from src.web.web_server import broadcast_message
    await broadcast_message({
        "type": "telemetry",
        "cpu": cpu,
        "memory": memory
    })

def emit_log_sync(message: str, level: str = "INFO"):
    """Versão síncrona para ser chamada de qualquer lugar"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(emit_log(message, level))
        else:
            loop.run_until_complete(emit_log(message, level))
    except Exception:
        pass

def emit_telemetry_sync(cpu: float, memory: float):
    """Versão síncrona para telemetria"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(emit_telemetry(cpu, memory))
        else:
            loop.run_until_complete(emit_telemetry(cpu, memory))
    except Exception:
        pass
