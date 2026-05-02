import os
import json
import asyncio
import re
from pathlib import Path
from typing import AsyncGenerator
from loguru import logger

from app.engineer_brain import brain
from app.unified_memory import memory
from app.system_tools import SystemTools
from app.persona import persona

tools = SystemTools()

async def chat_reply(user_id: str, user_message: str) -> str:
    """Resposta simples (legado)."""
    context = await memory.get_context(user_id, query=user_message)
    prompt = f"Usuario: {user_message}\n\nContexto: {context}"
    reply = await brain.reason(prompt)
    await memory.add_memory(user_id, user_message, source="user")
    return reply

async def chat_stream(user_id: str, user_message: str) -> AsyncGenerator[str, None]:
    """Streaming completo com personalidade JARVIS + cumprimento."""
    context = await memory.get_context(user_id, query=user_message)
    
    # Personalidade + Cumprimento automatico
    persona_context = persona.get_system_prompt()
    
    full_prompt = f"""
{persona_context}

Usuario: {user_message}
Contexto sensorial e memoria: {context}

Responda como JARVIS 6.1: direto, sarcastico quando necessario, sempre educado e util.
Comece com cumprimento se for a primeira mensagem do dia.
"""

    full_reply = ""
    async for chunk in brain.reason_stream(full_prompt, context=context):
        full_reply += chunk
        yield chunk

    # Execucao de ferramentas automaticas
    tool_calls = re.findall(r"\[TOOL:\s*(.*?)\((.*?)\)\]", full_reply)
    for func_name, args_str in tool_calls:
        try:
            func = getattr(tools, func_name, None)
            if func:
                clean_args = [a.strip().strip("'\"") for a in args_str.split(",") if a.strip()]
                if asyncio.iscoroutinefunction(func):
                    await func(*clean_args)
                else:
                    func(*clean_args)
        except Exception as e:
            logger.error(f"Erro na ferramenta {func_name}: {e}")

    # Salva tudo na memoria
    asyncio.create_task(memory.add_memory(user_id, user_message, source="user"))
    asyncio.create_task(memory.save_session(user_id, [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": full_reply}
    ], f"Conversa: {user_message[:30]}"))
