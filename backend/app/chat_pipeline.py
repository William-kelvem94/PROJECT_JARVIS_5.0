import asyncio
import re
from loguru import logger
from .engineer_brain import brain
from .unified_memory import memory
from .persona import persona
from .system_tools import SystemTools

tools = SystemTools()

async def chat_reply(user_id: str, user_message: str) -> str:
    """Resposta simples (síncrona para a API)."""
    context = await memory.get_context(user_id, query=user_message)
    persona_context = persona.get_system_prompt()
    full_prompt = f"{persona_context}\nUsuário: {user_message}\nContexto: {context}"
    
    reply = await brain.reason(full_prompt)
    
    # Salva na memória
    await memory.add_memory(user_id, user_message, source="user")
    await memory.add_memory(user_id, reply, source="jarvis")
    
    return reply

async def chat_stream(user_id: str, user_message: str):
    """Pipeline de chat com streaming, memória e execução de ferramentas."""
    context = await memory.get_context(user_id, query=user_message)
    persona_context = persona.get_system_prompt()
    
    # Injeção de personalidade e diretrizes
    system_prompt = f"{persona_context}\nResponda de forma natural, técnica e extremamente eficiente como o JARVIS 5.0."
    
    full_prompt = f"Contexto Sensorial/Memória: {context}\nUsuário: {user_message}"
    
    full_reply = ""
    async for chunk in brain.reason_stream(full_prompt, context=system_prompt):
        full_reply += chunk
        yield chunk

    # Salva na memória unificada
    await memory.add_memory(user_id, user_message, source="user")
    await memory.add_memory(user_id, full_reply, source="jarvis")

    # Execução de ferramentas automáticas (TOOL:func(args))
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
                logger.info(f"🛠️ Ferramenta executada: {func_name}")
        except Exception as e:
            logger.error(f"Erro na ferramenta {func_name}: {e}")
