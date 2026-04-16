import asyncio
from .base import BaseTool

class BrowserTools(BaseTool):
    async def browser_navigate(self, url: str):
        from ..browser_engine import browser_manager
        try:
            result = await browser_manager.navigate(url)
            asyncio.create_task(self._log_activity("Navegador", f"Acessando: {url}", "info"))
            return result
        except Exception as e:
            return f"Erro: {e}"

    async def browser_screenshot(self):
        from ..browser_engine import browser_manager
        try:
            path = await browser_manager.get_screenshot()
            return f"Screenshot salvo em '{path}'."
        except Exception as e:
            return f"Erro: {e}"

    async def browser_get_page_content(self):
        from ..browser_engine import browser_manager
        try:
            content = await browser_manager.get_page_content()
            return content[:5000] # Limite para não estourar contexto
        except Exception as e:
            return f"Erro: {e}"
            
    async def web_search_no_api(self, query: str):
        from ..browser_engine import browser_manager
        from ..unified_memory import memory
        try:
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            await browser_manager.navigate(search_url)
            content = await browser_manager.get_page_content()
            
            # Log de atividade para o HUD
            asyncio.create_task(self._log_activity("Pesquisa", f"Buscando: {query}", "info"))
            
            # Registro automático no aprendizado do Obsidian
            insight = f"Pesquisa web realizada sobre: {query}. Resultados extraídos da fonte DuckDuckGo."
            await memory.add_memory("jarvis_user", insight, category="aprendizado", source="web_search")
            
            return content[:6000]
        except Exception as e:
            return f"Falha na busca: {e}"

    async def browser_click(self, selector: str = None, x: int = None, y: int = None):
        from ..browser_engine import browser_manager
        return await browser_manager.click(selector=selector, x=x, y=y)
