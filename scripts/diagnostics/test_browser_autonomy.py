import asyncio
import pytest
from backend.app.browser_engine import browser_manager

@pytest.mark.asyncio
async def test_browser():
    try:
        print("Iniciando teste de navegador...")
        await browser_manager.start()
        
        print("Navegando para o Google...")
        await browser_manager.navigate("https://www.google.com")
        
        print("Tirando screenshot...")
        path = await browser_manager.get_screenshot()
        print(f"Screenshot salvo em: {path}")
        
        print("Fechando navegador...")
        await browser_manager.close()
        print("Teste concluído com sucesso!")
    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_browser())
