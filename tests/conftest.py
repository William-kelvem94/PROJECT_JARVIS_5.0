<<<<<<< Updated upstream
import pytest
import sys
from pathlib import Path

=======
import os
import sys
from pathlib import Path

import pytest

# Ensure tests run in test-mode to avoid starting native/background threads
os.environ.setdefault("JARVIS_TEST_MODE", "1")

>>>>>>> Stashed changes
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
