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

    # Voz: Fala a resposta localmente
    from .voice.tts_engine import tts_engine
    asyncio.create_task(tts_engine.speak(reply, play_local=True))

    return reply

async def chat_stream(user_id: str, user_message: str):
    """Pipeline de chat com streaming, memória e execução de ferramentas em tempo real."""
    context = await memory.get_context(user_id, query=user_message)
    persona_context = persona.get_system_prompt()

    system_prompt = f"{persona_context}\nResponda de forma natural, técnica e extremamente eficiente como o JARVIS 5.0."
    full_prompt = f"Contexto Sensorial/Memória: {context}\nUsuário: {user_message}"

    full_reply = ""
    buffer = ""

    # Regex para detectar [TOOL:func(args)]
    tool_pattern = re.compile(r"\[TOOL:\s*(.*?)\((.*?)\)\]")

    async for chunk in brain.reason_stream(full_prompt, context=system_prompt):
        full_reply += chunk
        buffer += chunk

        # Verifica se o buffer contém uma chamada de ferramenta completa
        match = tool_pattern.search(buffer)
        if match:
            func_name, args_str = match.groups()
            # Dispara a ferramenta em background IMEDIATAMENTE sem travar o stream
            asyncio.create_task(execute_tool_async(func_name, args_str))
            # Limpa o buffer após encontrar a ferramenta para evitar execuções duplicadas
            buffer = buffer[match.end():]

        yield chunk

    # Salva na memória unificada
    await memory.add_memory(user_id, user_message, source="user")
    await memory.add_memory(user_id, full_reply, source="jarvis")

    # Voz: Fala a resposta completa após o streaming
    from .voice.tts_engine import tts_engine
    asyncio.create_task(tts_engine.speak(full_reply, play_local=True))

async def execute_tool_async(func_name: str, args_str: str):
    """Helper para execução assíncrona de ferramentas disparadas via stream."""
    try:
        func = getattr(tools, func_name, None)
        if func:
            clean_args = [a.strip().strip("'\"") for a in args_str.split(",") if a.strip()]
            if asyncio.iscoroutinefunction(func):
                await func(*clean_args)
            else:
                # Executa funções síncronas em thread para não travar o loop
                await asyncio.to_thread(func, *clean_args)
            logger.info(f"🛠️ Ferramenta executada em tempo real: {func_name}")
        else:
            logger.warning(f"🛠️ Ferramenta não encontrada: {func_name}")
    except Exception as e:
        logger.error(f"Erro na execução da ferramenta {func_name}: {e}")
