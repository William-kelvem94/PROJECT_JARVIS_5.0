import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestEngineerBrain:
    """Testes para o motor de inferência com fallback."""

    @pytest.fixture
    def brain(self):
        from app.engineer_brain import EngineerBrain
        return EngineerBrain()

    @pytest.mark.asyncio
    async def test_pick_gemini_model_returns_cached(self, brain):
        """Deve retornar modelo cacheado sem nova sondagem."""
        import app.engineer_brain as engineer_brain
        import time
        engineer_brain._gemini_model_cache = "gemini-2.0-flash"
        engineer_brain._gemini_model_cache_ts = time.monotonic()
        result = await brain._pick_gemini_model()
        assert result == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_reason_fallback_yields_text(self, brain):
        """Mesmo com todos os backends offline, deve retornar texto de fallback."""
        brain._lmstudio_available = False
        with patch.object(brain, '_pick_gemini_model', return_value=None):
            chunks = []
            async for chunk in brain.reason_stream("teste"):
                chunks.append(chunk)
            assert len(chunks) > 0
            assert isinstance(chunks[0], str)

    @pytest.mark.asyncio
    async def test_safety_params_under_load(self, brain):
        """Sob carga alta, max_tokens deve ser ajustado."""
        import psutil
        with patch.object(psutil, 'virtual_memory') as mock_mem:
            mock_mem.return_value.percent = 90
            params = await brain._get_safety_params()
            assert params["max_tokens"] == 1024
