import os
import json
from pathlib import Path
from typing import Tuple

from .engineer_brain import brain
from .mem0 import AsyncMemoryClient
from .config import settings

async def _load_kb_summary(max_files: int = 5) -> str:
    kb_path = getattr(settings, "jarvis_kb_path", "")
    if not kb_path or not os.path.isdir(kb_path):
        return "Nenhuma KB configurada."

    summaries = []
    for root, _, files in os.walk(kb_path):
        for filename in sorted(files):
            if filename.lower().endswith((".md", ".txt")):
                filepath = os.path.join(root, filename)
                try:
                    text = Path(filepath).read_text("utf-8").replace("\n", " ").strip()
                    summaries.append(f"{filename}: {text[:300]}")
                except Exception:
                    continue
            if len(summaries) >= max_files:
                break
        if len(summaries) >= max_files:
            break

    return "\n".join(summaries) if summaries else "KB vazia."

async def get_memory_context(user_id: str) -> str:
    memory_client = AsyncMemoryClient()
    results = await memory_client.get_all(user_id=user_id)
    if not results:
        return "Sem memórias registradas."
    return "\n".join([f"- {item.get('memory')}" for item in results if item.get('memory')])

async def chat_reply(user_id: str, user_message: str) -> str:
    memory_client = AsyncMemoryClient()
    await memory_client.add([{"role": "user", "content": user_message}], user_id=user_id)

    memory_context = await get_memory_context(user_id)
    kb_summary = await _load_kb_summary()

    prompt = (
        f"Você é o JARVIS, assistente técnico e confiável. Responda ao usuário com clareza, honestidade e brevidade. "
        f"Não invente fatos. Use o contexto disponível quando possível.\n\n"
        f"Usuário: {user_message}\n\n"
        f"Memórias do usuário:\n{memory_context}\n\n"
        f"Base de Conhecimento:\n{kb_summary}\n\n"
        f"Responda com um parágrafo direto, mencionando se precisar de mais detalhes."
    )

    # Cérebro WILL-JARVIS / Local Engine (Nuvem Desabilitada por Padrão)
    logger.info("Encaminhando pipeline de chat para a Engenharia Local Inteligente.")
    return await brain.reason(prompt, context=memory_context)
