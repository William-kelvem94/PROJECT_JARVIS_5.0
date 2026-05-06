"""
JARVIS 5.0 - API Module
Fachada para routers FastAPI e servidores de suporte.

Uso:
    from app.api import system_bridge_router
    from app.api import voice_router
    from app.api import telemetry_app, start_telemetry_server
    from app.api import broadcast_state, broadcast_chunk
"""
# Re-exports from original locations (backward compatible)
from app.system_bridge import router as system_bridge_router  # noqa: F401
from app.voice_websocket import (                             # noqa: F401
    router as voice_router,
    broadcast_state,
    broadcast_chunk,
)
from app.telemetry_server import (                            # noqa: F401
    app as telemetry_app,
    start_telemetry_server,
)

__all__ = [
    # system_bridge
    "system_bridge_router",
    # voice_websocket
    "voice_router", "broadcast_state", "broadcast_chunk",
    # telemetry_server
    "telemetry_app", "start_telemetry_server",
]
