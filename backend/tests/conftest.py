import sys
import os
import pytest

# Garantir que 'backend' esteja no path para os imports 'from app...'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_settings():
    """Configurações de teste que não dependem de hardware real."""
    return {
        "LM_STUDIO_URL": "http://localhost:1234/v1/chat/completions",
        "LM_STUDIO_MODEL": "test-model",
        "LM_STUDIO_TIMEOUT": 1,
        "GEMINI_API_KEY": None,
        "GEMINI_MODEL": "gemini-2.0-flash",
        "OPENROUTER_API_KEY": None,
        "OPENROUTER_MODEL": "test-model",
        "GPU_ENABLED": False,
        "JARVIS_WHISPER_MODEL": "tiny",
        "OBSIDIAN_VAULT_PATH": os.path.join(os.path.dirname(__file__), "..", "data", "test_vault"),
    }
