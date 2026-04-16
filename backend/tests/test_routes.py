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
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "cpu_percent" in data
    assert "ram_percent" in data
    assert "uptime_seconds" in data


def test_chat_stub():
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data


