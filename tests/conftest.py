import pytest
import sys
from pathlib import Path

# Adiciona src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_config():
    return {
        "debug": True,
        "log_level": "DEBUG",
        "models_path": "./models",
        "data_path": "./data",
    }
