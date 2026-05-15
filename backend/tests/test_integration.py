from unittest.mock import AsyncMock

import pytest

from backend.app import chat_pipeline
from backend.app.engineer_brain import brain


async def mock_llm_stream(*_, **__):
    yield "JARVIS is online and ready."


@pytest.mark.asyncio
async def test_full_voice_llm_tts_pipeline(monkeypatch):
    monkeypatch.setattr(
        brain,
        "reason_stream",
        mock_llm_stream,
    )

    response = []
    async for chunk in chat_pipeline.chat_stream(
        user_id="TestUser",
        user_message="Hello",
    ):
        response.append(chunk)

    assert any("online" in part.lower() for part in response)


@pytest.mark.asyncio
async def test_chat_reply_with_error_on_empty_message(monkeypatch):
    with pytest.raises(Exception):
        await chat_pipeline.chat_reply(
            user_id="TestUser",
            user_message="",
        )
