import os
import json
import asyncio
import re
from pathlib import Path
from typing import Tuple

from loguru import logger
from .engineer_brain import brain
from .unified_memory import memory
from .system_tools import SystemTools

tools = SystemTools()

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
    from .unified_memory import memory
    from .engineer_brain import brain
    
    context = await memory.get_context(user_id, query=user_message)
    
    prompt = user_message
    
    full_reply = ""
    async for chunk in brain.reason_stream(prompt, context=context):
        full_reply += chunk
        yield chunk
        
    # Pós-processamento de Ferramentas (Tags [TOOL: function(args)])
    tool_calls = re.findall(r"\[TOOL:\s*(.*?)\((.*?)\)\]", full_reply)
    for func_name, args in tool_calls:
        try:
            logger.info(f"🛠️ Executando Ferramenta: {func_name}({args})")
            # Tenta encontrar o método na classe tools
            func = getattr(tools, func_name, None)
            if func:
                # Limpa aspas dos argumentos se existirem
                clean_args = [a.strip().strip("'").strip('"') for a in args.split(",") if a.strip()]
                if asyncio.iscoroutinefunction(func):
                    await func(*clean_args)
                else:
                    func(*clean_args)
        except Exception as e:
            logger.error(f"Falha ao executar ferramenta {func_name}: {e}")

    # Ao final, salva na memória em background
    await asyncio.gather(
        memory.add_memory(user_id, user_message, source="jarvis_voice"),
        memory.save_session(user_id, [], f"Conversa Técnica: {user_message[:25]}"),
    )
