import pytest
import asyncio
import os
import time
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.mem0 import AsyncMemoryClient

client = TestClient(app)

def test_health_check():
    """Verifica se o endpoint de saúde básica está online e retornando métricas."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cpu_percent" in data
    assert "ram_percent" in data

def test_config_validation():
    """Garante que as configurações críticas foram carregadas corretamente."""
    # Se o settings for o Mock (FakeSettings), este teste deve avisar
    if hasattr(settings, "__getattr__"):
        pytest.skip("Settings em modo Mock - Verifique seu arquivo .env")
    
    assert settings.livekit_url != ""
    assert settings.google_api_key != ""
    assert "livekit.cloud" in settings.livekit_url or "localhost" in settings.livekit_url

@pytest.mark.asyncio
async def test_memory_system_stress():
    """Teste de stress simulado no sistema de memória (Mem0)."""
    memory = AsyncMemoryClient()
    user_id = f"test_user_{int(time.time())}"
    
    # Inserção rápida de múltiplos fatos
    facts = [
        "O usuário gosta de café preto.",
        "O usuário trabalha com Python.",
        "O usuário mora em São Paulo.",
        "A cor favorita é azul.",
        "O usuário prefere Next.js para o frontend."
    ]
    
    tasks = [memory.add([{"role": "user", "content": f}], user_id=user_id) for f in facts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verifica se não houve falhas massivas
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 0, f"Falhas no sistema de memória: {errors}"
    
    # Recuperação e verificação
    memories = await memory.get_all(user_id=user_id)
    assert len(memories) >= 1

def test_livekit_token_generation():
    """Valida se o gateway de tokens LiveKit está gerando JWTs válidos."""
    response = client.get("/livekit-token")
    if response.status_code == 500:
        pytest.skip("Credenciais LiveKit ausentes para teste de token.")
        
    assert response.status_code == 200
    assert "token" in response.json()
    assert len(response.json()["token"]) > 30

def test_api_concurrency_stress():
    """Testa a capacidade da API FastAPI de lidar com múltiplas requisições de status."""
    import concurrent.futures
    
    def fetch_status():
        return client.get("/status").status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_status) for _ in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    assert all(r == 200 for r in results)
