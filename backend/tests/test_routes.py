from fastapi.testclient import TestClient
import os, sys
# ensure backend directory is on sys.path so 'app' package is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert "cpu" in data
    assert "ram" in data


def test_chat_stub():
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data


