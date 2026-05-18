import pytest
import asyncio
import os
import time
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
try:
    from app.unified_memory import memory as memory_client
except ImportError:
    from unittest.mock import AsyncMock
    memory_client = AsyncMock()

client = TestClient(app)

def test_health_check():
    """Verifica se o endpoint de saúde básica está online e retornando métricas."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "online"}
    assert "cpu" in data or "cpu_percent" in data
    assert "ram" in data or "ram_percent" in data

def test_config_validation():
    """Garante que as configurações críticas foram carregadas corretamente."""
    # Se o settings for o Mock (FakeSettings), este teste deve avisar
    if hasattr(settings, "__getattr__"):
        pytest.skip("Settings em modo Mock - Verifique seu arquivo .env")

    assert settings.google_api_key != ""

@pytest.mark.asyncio
async def test_memory_system_stress():
    """Teste de stress simulado no sistema de memória (Mem0)."""
    memory = memory_client
    user_id = f"test_user_{int(time.time())}"
    
    # Inserção rápida de múltiplos fatos
    facts = [
        "O usuário gosta de café preto.",
        "O usuário trabalha com Python.",
        "O usuário mora em São Paulo.",
        "A cor favorita é azul.",
        "O usuário prefere Next.js para o frontend."
    ]
    
    tasks = [memory.add_memory(user_id=user_id, content=f) for f in facts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verifica se não houve falhas massivas
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 0, f"Falhas no sistema de memória: {errors}"
    
    # Recuperação e verificação
    memories = await memory.get_all(user_id=user_id)
    assert len(memories) >= 1

def test_api_concurrency_stress():
    """Testa a capacidade da API FastAPI de lidar com múltiplas requisições de status."""
    import concurrent.futures
    
    def fetch_status():
        return client.get("/health").status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_status) for _ in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    assert all(r == 200 for r in results)
