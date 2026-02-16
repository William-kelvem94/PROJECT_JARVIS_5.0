"""
Ferramenta de Busca na Web
Permite que o Jarvis busque informaÃ§Ãµes no Google de forma autÃ´noma.
"""

import logging
from typing import List

# from src.core.security.security_manager import security_manager (Removido para evitar import circular)

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
            logger.warning(
                "Biblioteca googlesearch-python nÃ£o instalada. Busca na web desativada."
            )

    def search_google(self, query: str, num_results: int = 3) -> List[str]:
        """Realiza uma busca no Google e retorna URLs"""
        if not SEARCH_AVAILABLE:
            logger.error("Busca indisponÃ­vel: biblioteca ausente.")
            return []

        # 1. Gatekeeper: Validar permissÃ£o (Lazy Import para evitar ciclo)
        try:
            from src.core.security.security_manager import security_manager

            if not security_manager.validate_web_search(query):
                logger.warning("Busca na web cancelada pelo Gatekeeper.")
                return ["Busca cancelada por falta de permissÃ£o."]
        except (ImportError, AttributeError, Exception) as e:
            logger.error(
                f"Erro ao carregar Gatekeeper: {e}. Busca bloqueada por seguranÃ§a."
            )
            return ["Busca bloqueada: Erro crÃ­tico no motor de seguranÃ§a."]

        logger.info(f"Buscando no Google: '{query}'")

        results = []
        try:
            # advanced=True retornaria objetos Result, mas a lib padrÃ£o retorna strings
            for url in search(query, num_results=num_results, advanced=True):
                # Extrair tÃ­tulo e descriÃ§Ã£o se available, ou apenas URL
                results.append(
                    f"TÃ­tulo: {url.title}\nURL: {url.url}\nDescriÃ§Ã£o: {url.description}"
                )
        except Exception as e:
            logger.error(f"Erro na busca Google: {e}")
            return [f"Erro ao buscar: {str(e)}"]

        return results


# InstÃ¢ncia global
web_search_tool = WebSearchTool()
