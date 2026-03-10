import asyncio
import os
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

class BrowserEngine:
    _instance = None
    
    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None
        # Organização: Dados do navegador ficam na pasta de dados do backend
        self.user_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "browser_data")
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = BrowserEngine()
        return cls._instance

    async def start(self):
        if self.pw:
            return
            
        logger.info("Iniciando motor de navegação Playwright...")
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.pw = await async_playwright().start()
        
        # Modo Headful para o usuário ver a autonomia
        # Persistent context para manter sessões
        self.context = await self.pw.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False,
            viewport={'width': 1280, 'height': 720},
            args=["--disable-blink-features=AutomationControlled"] # Evitar detecção básica de bot
        )
        
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        logger.info("Navegador pronto para comandos.")

    async def navigate(self, url: str):
        if not self.page: await self.start()
        logger.info(f"Navegando para: {url}")
        await self.page.goto(url, wait_until="networkidle")
        return f"Navegado com sucesso para {url}"

    async def click(self, selector: str = None, x: int = None, y: int = None):
        if not self.page: await self.start()
        if x is not None and y is not None:
            logger.info(f"Clicando em coordenadas: {x}, {y}")
            await self.page.mouse.click(x, y)
        elif selector:
            logger.info(f"Clicando em seletor: {selector}")
            await self.page.click(selector)
        return "Clique executado."

    async def type_text(self, selector: str, text: str):
        if not self.page: await self.start()
        logger.info(f"Digitando '{text}' em {selector}")
        await self.page.fill(selector, text)
        return f"Texto digitado em {selector}"

    async def get_screenshot(self):
        if not self.page: await self.start()
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        path = os.path.join(self.screenshot_dir, filename)
        await self.page.screenshot(path=path)
        logger.info(f"Screenshot salvo em {path}")
        
        # Também atualizamos a 'last_browser_state' para o preview rápido
        latest_path = os.path.join(self.screenshot_dir, "last_browser_state.png")
        import shutil
        shutil.copy(path, latest_path)
        
        return path

    async def scroll(self, direction: str = "down", amount: int = 3):
        if not self.page: await self.start()
        delta = amount * 100
        if direction == "down":
            await self.page.mouse.wheel(0, delta)
        elif direction == "up":
            await self.page.mouse.wheel(0, -delta)
        return f"Rolado {direction} por {amount} passos."

    async def get_page_content(self):
        if not self.page: await self.start()
        try:
            text = await self.page.inner_text("body")
            return text[:8000]  # Limita para não explodir o contexto
        except Exception as e:
            return f"Erro ao extrair conteúdo da página: {e}"

    async def get_current_url(self):
        if not self.page: await self.start()
        return self.page.url

    async def close(self):
        if self.context:
            await self.context.close()
        if self.pw:
            await self.pw.stop()
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None
        logger.info("Navegador encerrado.")

# Instancia global para ser usada pelas ferramentas
browser_manager = BrowserEngine()
