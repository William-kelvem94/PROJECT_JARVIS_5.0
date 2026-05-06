"""
JARVIS 5.0 - Singleton Registry
Ponto central de criação de singletons para evitar instâncias duplicadas.
Importe daqui ao invés de criar novas instâncias.
"""
from loguru import logger

from .security.sentinel_core import SentinelSecurity
from .security.sentinel_parser import SentinelParser
from .security.blackbox import BlackBox

# ── Security Singletons ──────────────────────────────────────────────────────
_sentinel_parser: SentinelParser | None = None
_sentinel: SentinelSecurity | None = None
_blackbox: BlackBox | None = None


def get_sentinel_parser() -> SentinelParser:
    global _sentinel_parser
    if _sentinel_parser is None:
        _sentinel_parser = SentinelParser()
        logger.info("[Dependencies] SentinelParser singleton criado.")
    return _sentinel_parser


def get_sentinel() -> SentinelSecurity:
    global _sentinel
    if _sentinel is None:
        _sentinel = SentinelSecurity()
        logger.info("[Dependencies] SentinelSecurity singleton criado.")
    return _sentinel


def get_blackbox() -> BlackBox:
    global _blackbox
    if _blackbox is None:
        sentinel = get_sentinel()
        system_key = sentinel.derive_system_key()
        import os
        db_path = os.environ.get(
            "JARVIS_BLACKBOX_PATH",
            "data/blackbox.db"
        )
        _blackbox = BlackBox(db_path=db_path, encryption_key=system_key)
        sentinel.blackbox = _blackbox
        logger.info("[Dependencies] BlackBox singleton criado.")
    return _blackbox
