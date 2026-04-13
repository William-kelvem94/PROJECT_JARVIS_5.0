import asyncio
from livekit import agents
from .base import BaseTool

class BrowserTools(BaseTool):
    @agents.llm.function_tool(description="Navega para uma URL no navegador autônomo.")
    async def browser_navigate(self, url: str):
        from ..browser_engine import browser_manager
        try:
            result = await browser_manager.navigate(url)
            asyncio.create_task(self._log_activity("Navegador", f"Acessando: {url}", "info"))
            return result
        except Exception as e:
            return f"Erro: {e}"

    @agents.llm.function_tool(description="Tira um screenshot do navegador.")
    async def browser_screenshot(self):
        from ..browser_engine import browser_manager
        try:
            path = await browser_manager.get_screenshot()
            return f"Screenshot salvo em '{path}'."
        except Exception as e:
            return f"Erro: {e}"

    @agents.llm.function_tool(description="Extrai o texto da página atual.")
    async def browser_get_page_content(self):
        from ..browser_engine import browser_manager
        try:
            content = await browser_manager.get_page_content()
            return content[:5000] # Limite para não estourar contexto
        except Exception as e:
            return f"Erro: {e}"
            
    @agents.llm.function_tool(description="Clica em um elemento da página.")
    async def browser_click(self, selector: str = None, x: int = None, y: int = None):
        from ..browser_engine import browser_manager
        return await browser_manager.click(selector=selector, x=x, y=y)
