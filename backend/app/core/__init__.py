"""
JARVIS 5.0 - Core Module
Fachada para o pipeline de chat, persona e base de conhecimento.

Uso:
    from app.core import chat_stream, chat_reply
    from app.core import persona, PersonaManager
    from app.core import AGENT_INSTRUCTION, SESSION_INSTRUCTION
    from app.core import load_kb
"""
# Re-exports from original locations (backward compatible)
from app.chat_pipeline import chat_stream, chat_reply         # noqa: F401
from app.persona import persona, PersonaManager               # noqa: F401
from app.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION  # noqa: F401
from app.kb_loader import load_kb                             # noqa: F401

__all__ = [
    # chat_pipeline
    "chat_stream", "chat_reply",
    # persona
    "persona", "PersonaManager",
    # prompts
    "AGENT_INSTRUCTION", "SESSION_INSTRUCTION",
    # kb_loader
    "load_kb",
]
