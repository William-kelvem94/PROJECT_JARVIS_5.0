from core.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_backend_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Jarvis IA Conversacional" in response.json()["message"]
