from fastapi.testclient import TestClient
import os, sys
# ensure backend directory is on sys.path so 'app' package is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_stub():
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data


def test_livekit_token(monkeypatch):
    # supply dummy credentials so endpoint can generate a token
    monkeypatch.setenv("LIVEKIT_API_KEY", "key123")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "secret456")
    resp = client.get("/livekit-token")
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert isinstance(data["token"], str)
