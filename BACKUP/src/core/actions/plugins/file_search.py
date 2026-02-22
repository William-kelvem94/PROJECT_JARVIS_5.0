"""
JARVIS 5.0 - Plugin: Advanced File Search
========================================
Habilidade de busca profunda em arquivos usando o MetaCache.
"""

import logging
import asyncio
from src.utils.file_indexer import file_indexer

logger = logging.getLogger(__name__)


async def search_files(query: str):
    """Procura por arquivos e retorna lista formatada"""
    results = await asyncio.to_thread(file_indexer.search, query)

    if not results:
        return "Desculpe Senhor, não encontrei nenhum arquivo correspondente no meu cache central."

    # Limitar a 5 resultados para não poluir
    count = len(results)
    response_lines = [f"Encontrei {count} arquivos relacionados a '{query}':\n"]
    for file_path in results[:5]:
        response_lines.append(f"- {file_path}\n")

    if count > 5:
        response_lines.append("... e outros arquivos.")

    return "".join(response_lines)


# Dicionário de ações que o ActionController/AIAgent pode chamar
# No JARVIS 5.0, vamos integrar isso ao action_handler dinamicamente
ACTIONS = {
    "search_local_files": {
        "function": search_files,
        "description": "Busca arquivos no computador usando metadados e índice local",
    }
}
