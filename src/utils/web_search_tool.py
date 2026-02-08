"""
Ferramenta de Busca na Web
Permite que o Jarvis busque informações no Google de forma autônoma.
"""

import logging
from typing import List, Dict, Any
from src.core.security.security_manager import security_manager

try:
    from googlesearch import search
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class WebSearchTool:
    """Ferramenta para buscas na web"""

    def __init__(self):
        if not SEARCH_AVAILABLE:
            logger.warning("Biblioteca googlesearch-python não instalada. Busca na web desativada.")

    def search_google(self, query: str, num_results: int = 3) -> List[str]:
        """Realiza uma busca no Google e retorna URLs"""
        if not SEARCH_AVAILABLE:
            logger.error("Busca indisponível: biblioteca ausente.")
            return []

        # 1. Gatekeeper: Validar permissão
        if not security_manager.validate_web_search(query):
            logger.warning("Busca na web cancelada pelo Gatekeeper.")
            return ["Busca cancelada por falta de permissão."]

        logger.info(f"Buscando no Google: '{query}'")
        
        results = []
        try:
            # advanced=True retornaria objetos Result, mas a lib padrão retorna strings
            for url in search(query, num_results=num_results, advanced=True):
                # Extrair título e descrição se available, ou apenas URL
                results.append(f"Título: {url.title}\nURL: {url.url}\nDescrição: {url.description}")
        except Exception as e:
            logger.error(f"Erro na busca Google: {e}")
            return [f"Erro ao buscar: {str(e)}"]

        return results

# Instância global
web_search_tool = WebSearchTool()
