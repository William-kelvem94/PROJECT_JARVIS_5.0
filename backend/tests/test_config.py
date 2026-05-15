import sys
import os
import importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import patch


class TestSettings:
    """Testes para o módulo de configuração."""

    @patch.dict('os.environ', {'JARVIS_AI_DEVICE': 'cpu'}, clear=True)
    def test_env_forces_cpu(self):
        """JARVIS_AI_DEVICE=cpu deve forçar modo CPU."""
        import app.config
        importlib.reload(app.config)
        assert app.config.settings.DEVICE_TYPE == "cpu"

    @patch.dict('os.environ', {'JARVIS_AI_DEVICE': 'cuda'}, clear=True)
    def test_env_forces_cuda(self):
        """JARVIS_AI_DEVICE=cuda deve forçar modo CUDA."""
        import app.config
        importlib.reload(app.config)
        assert app.config.settings.DEVICE_TYPE == "cuda"
