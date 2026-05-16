"""Tests for SmartRouter - LLM routing with fallback hierarchy."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_detect_complexity_fast_for_simple_query():
    from app.smart_router import router
    complexity = await router._detect_complexity("Hello")
    assert complexity == "fast"

@pytest.mark.asyncio
async def test_detect_complexity_deep_for_complex_keywords():
    from app.smart_router import router
    complexity = await router._detect_complexity("Preciso de uma análise de arquitetura")
    assert complexity == "deep"

@pytest.mark.asyncio
async def test_detect_complexity_fast_under_high_ram():
    with patch('psutil.virtual_memory') as mock_mem:
        mock_mem.return_value.percent = 95
        from app.smart_router import router
        complexity = await router._detect_complexity("Arquitetura complexa")
        assert complexity == "fast"

@pytest.mark.asyncio
async def test_reason_stream_fallback_on_all_failures():
    from app.smart_router import router
    with patch.object(router, '_call_gemini', side_effect=Exception("offline")):
        with patch.object(router, '_call_local', side_effect=Exception("offline")):
            with patch.object(router, '_call_openrouter', side_effect=Exception("offline")):
                result = ""
                async for chunk in router.reason_stream("test", "system"):
                    result += chunk
                assert "Todos os modelos" in result or "falharam" in result
