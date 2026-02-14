"""
JARVIS 5.0 - Plugin: Advanced File Search
========================================
Habilidade de busca profunda em arquivos usando o MetaCache.
"""

import logging
from src.utils.file_indexer import file_indexer

logger = logging.getLogger(__name__)

async def search_files(query: str):
    """Procura por arquivos e retorna lista formatada"""
    results = file_indexer.search(query)
    
    if not results:
        return "Desculpe Senhor, não encontrei nenhum arquivo correspondente no meu cache central."
        
    # Limitar a 5 resultados para não poluir
    count = len(results)
    response = f"Encontrei {count} arquivos relacionados a '{query}':\n"
    for r in results[:5]:
        response += f"- {r}\n"
    
    if count > 5:
        response += "... e outros arquivos."
        
    return response

# Dicionário de ações que o ActionController/AIAgent pode chamar
# No JARVIS 5.0, vamos integrar isso ao action_handler dinamicamente
ACTIONS = {
    "search_local_files": {
        "function": search_files,
        "description": "Busca arquivos no computador usando metadados e índice local"
    }
}
