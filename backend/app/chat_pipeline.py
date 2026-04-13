import os
import json
from pathlib import Path
from typing import Tuple

from loguru import logger
from .engineer_brain import brain
from .unified_memory import memory

async def chat_reply(user_id: str, user_message: str) -> str:
    """Resposta síncrona (legado/padrão)."""
    context = await memory.get_context(user_id, query=user_message)
    
    prompt = (
        f"Usuário: {user_message}\n\n"
        f"Contexto do Sistema:\n{context}\n\n"
        f"Execução: Gere a melhor resposta técnica baseada no contexto acima."
    )
    
    reply = await brain.reason(prompt, context=context)
    
    # Salva na memória
    await memory.add_memory(user_id, user_message, source="user")
    await memory.save_session(user_id, [{"role": "user", "content": user_message}, {"role": "assistant", "content": reply}], f"Sessão: {user_message[:20]}")
    
    return reply

async def chat_stream(user_id: str, user_message: str):
    """Gera a resposta em chunks para streaming de áudio/texto."""
    context = await memory.get_context(user_id, query=user_message)
    
    prompt = user_message
    
    full_reply = ""
    async for chunk in brain.reason_stream(prompt, context=context):
        full_reply += chunk
        yield chunk
        
    # Ao final, salva na memória em background
    import asyncio
    asyncio.create_task(memory.add_memory(user_id, user_message, source="jarvis_voice"))
    asyncio.create_task(memory.save_session(user_id, [], f"Conversa Técnica: {user_message[:25]}"))
