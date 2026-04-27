import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, patch


class TestChatPipeline:
    """Testes para o pipeline de chat."""

    @pytest.mark.asyncio
    async def test_chat_reply_saves_memory(self):
        """Deve chamar add_memory e save_session após resposta."""
        async def async_iter():
            yield "Olá"

        with patch('app.chat_pipeline.memory') as mock_memory:
            mock_memory.get_context = AsyncMock(return_value="")
            mock_memory.add_memory = AsyncMock()
            mock_memory.save_session = AsyncMock()

            with patch('app.chat_pipeline.brain') as mock_brain:
                mock_brain.reason_stream = AsyncMock(return_value=async_iter())

                from app.chat_pipeline import chat_reply
                result = await chat_reply("test_user", "Oi")
                assert result == "Olá"
                mock_memory.add_memory.assert_called_once()
                mock_memory.save_session.assert_called_once()
