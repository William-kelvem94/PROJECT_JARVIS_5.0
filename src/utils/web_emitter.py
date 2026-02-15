import asyncio
import logging
import json

logger = logging.getLogger(__name__)

# ReferÃªncia global para o servidor web (opcional, se precisarmos de acesso direto)
_web_server_ref = None

def set_web_server(server):
    global _web_server_ref
    _web_server_ref = server

# Global Signal Bus
_subscribers = []

def register_subscriber(callback):
    """Registra uma funÃ§Ã£o callback(event_type, data)"""
    if callback not in _subscribers:
        _subscribers.append(callback)

def _notify_subscribers(event_type: str, data: dict):
    """Notifica todos os subscribers locais (Desktop UI)"""
    for callback in _subscribers:
        try:
            callback(event_type, data)
        except Exception as e:
            logger.error(f"Erro no subscriber {callback}: {e}")

async def emit_log(message: str, level: str = "INFO"):
    """Envia log para Web e HUD"""
    # 1. Web
    from src.web.web_server import broadcast_message
    await broadcast_message({
        "type": "log",
        "message": message,
        "level": level
    })
    # 2. Desktop HUD
    _notify_subscribers("log", {"message": message, "level": level})

async def emit_telemetry(cpu: float, memory: float):
    """Envia telemetria para Web e HUD"""
    data = {"cpu": cpu, "memory": memory}
    # 1. Web
    from src.web.web_server import broadcast_message
    await broadcast_message({
        "type": "telemetry",
        **data
    })
    # 2. Desktop HUD
    _notify_subscribers("telemetry", data)

async def emit_status(status: str, details: str = "", model: str = None, tier: str = "balanced"):
    """
    Novo: Emite mudanÃ§a de status cognitivo
    Ex: status="thinking", details="Analisando logs...", model="llama3", tier="ultra"
    """
    data = {
        "status": status,
        "details": details,
        "model": model,
        "tier": tier
    }
    # 1. Web
    from src.web.web_server import broadcast_message
    await broadcast_message({
        "type": "status",
        **data
    })
    # 2. Desktop HUD
    _notify_subscribers("status", data)

def emit_status_sync(status: str, details: str = "", model: str = None, tier: str = "balanced"):
    """VersÃ£o sÃ­ncrona para emit_status"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(emit_status(status, details, model, tier))
        else:
            loop.run_until_complete(emit_status(status, details, model, tier))
    except Exception:
        # Fallback se nÃ£o houver loop
        _notify_subscribers("status", {
            "status": status, "details": details, "model": model, "tier": tier
        })

def emit_context(app_name: str, window_title: str):
    """Novo: Emite mudanÃ§a de contexto (Janela Ativa)"""
    data = {"app": app_name, "title": window_title}
    _notify_subscribers("context", data)

def emit_log_sync(message: str, level: str = "INFO"):
    """VersÃ£o sÃ­ncrona para ser chamada de qualquer lugar"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(emit_log(message, level))
        else:
            loop.run_until_complete(emit_log(message, level))
    except Exception:
        _notify_subscribers("log", {"message": message, "level": level})

def emit_telemetry_sync(cpu: float, memory: float):
    """VersÃ£o sÃ­ncrona para telemetria"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(emit_telemetry(cpu, memory))
        else:
            loop.run_until_complete(emit_telemetry(cpu, memory))
    except Exception:
        _notify_subscribers("telemetry", {"cpu": cpu, "memory": memory})
