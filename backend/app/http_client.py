"""
Shared HTTP client session for all brain modules.
Single aiohttp.ClientSession reused across the app (keep-alive, connection pool).
"""
import aiohttp
from loguru import logger

_session: aiohttp.ClientSession | None = None

def get_http_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
        logger.debug("[HTTP Client] Session created")
    return _session
