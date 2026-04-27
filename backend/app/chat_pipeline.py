"""
JARVIS 5.0 - Pipeline de Chat
Gerencia o fluxo completo: entrada do usuário -> LLM -> TTS -> resposta
"""

import asyncio
from loguru import logger
from .engineer_brain import brain
from .unified_memory import memory
from .persona import persona
from .utils.note_writer import note_writer


async def _maybe_write_note(user_id: str, user_message: str, full_reply: str):
    if not user_message or not full_reply:
        return

    action_text = user_message.lower()
    if any(keyword in action_text for keyword in ["nota", "memória", "memo", "note", "summarize", "resuma"]):
        title = f"JARVIS note - {user_id}"
        body = f"User message: {user_message}\n\nAssistant reply:\n{full_reply}"
        note_writer.create_note(title, body)


async def chat_reply(user_id: str, user_message: str):
    """
    Processa uma mensagem e retorna a resposta textual.
    Não faz TTS – apenas a parte de raciocínio.
    """
    context = await memory.get_context(user_id, user_message)

    if not user_message or not user_message.strip():
        raise ValueError("A mensagem do usuário não pode ficar vazia.")

    full_reply = ""
    try:
        async for chunk in brain.reason_stream(user_message, context):
            if isinstance(chunk, str) and not chunk.startswith("Erro"):
                full_reply += chunk
    except Exception as e:
        logger.error(f"Erro no raciocínio: {e}")
        full_reply = "Desculpe, meu cérebro está com dificuldades técnicas."

    if not full_reply:
        full_reply = "Não consegui formular uma resposta para isso agora."

    try:
        await asyncio.gather(
            memory.add_memory(user_id, user_message, source="jarvis_chat"),
            memory.save_session(
                user_id,
                [{"role": "user", "content": user_message}, {"role": "assistant", "content": full_reply}],
                f"Chat: {user_message[:30]}",
            ),
        )
        await _maybe_write_note(user_id, user_message, full_reply)
        logger.debug(f"Memória salva para {user_id}")
    except Exception as e:
        logger.warning(f"Falha ao salvar memória (não crítico): {e}")

    return full_reply


async def chat_stream(user_id: str, user_message: str):
    """
    Versão streaming: retorna chunks de texto conforme o LLM gera,
    ideal para WebSocket ou SSE.
    """
    context = await memory.get_context(user_id, user_message)
    chunks = []

    try:
        async for chunk in brain.reason_stream(user_message, context):
            if isinstance(chunk, str):
                chunks.append(chunk)
                yield chunk
    except Exception as e:
        logger.error(f"Erro no streaming: {e}")
        yield "Desculpe, ocorreu um erro no processamento."

    full_reply = "".join(chunks)

    try:
        await asyncio.gather(
            memory.add_memory(user_id, user_message, source="jarvis_voice"),
            memory.save_session(
                user_id,
                [{"role": "user", "content": user_message}, {"role": "assistant", "content": full_reply}],
                f"Conversa: {user_message[:25]}",
            ),
            _maybe_write_note(user_id, user_message, full_reply),
        )
    except Exception as e:
        logger.warning(f"Falha ao salvar sessão (não crítico): {e}")
