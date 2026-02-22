import time
from unittest.mock import patch, MagicMock

from src.core.intelligence.ollama_manager import OllamaManager, ollama_manager


def test_is_server_running_and_list_models_monkeypatched():
    # Simula servidor respondendo e lista de modelos
    with patch("src.core.intelligence.ollama_manager.requests") as mock_requests:
        mock_get = MagicMock()
        mock_get.status_code = 200
        mock_get.json.return_value = {"models": [{"name": "gemma3:4b"}]}
        mock_requests.get = MagicMock(return_value=mock_get)

        assert ollama_manager.is_server_running() is True
        models = ollama_manager.list_models()
        assert "gemma3:4b" in models


def test_ensure_model_loaded_not_installed_returns_false():
    # Garante que se o modelo não estiver instalado, não tenta aquecer
    manager = OllamaManager()

    with patch.object(manager, "is_server_running", return_value=True), patch.object(
        manager, "list_models", return_value=["phi3.5"]
    ):
        assert manager.ensure_model_loaded("nonexistent-model") is False


def test_start_and_stop_keepalive_registers_entry():
    manager = OllamaManager()

    # Inicia keepalive (valor string é aceito)
    started = manager.start_keepalive("gemma3:4b", "5m")
    assert started is True
    # Internally deve registrar a entrada
    assert "gemma3:4b" in manager._keepalive

    # Parar keepalive
    stopped = manager.stop_keepalive("gemma3:4b")
    assert stopped is True
    assert "gemma3:4b" not in manager._keepalive
