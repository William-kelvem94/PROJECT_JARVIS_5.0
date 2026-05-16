from unittest.mock import AsyncMock

import pytest

from backend.app import chat_pipeline
from backend.app.engineer_brain import brain


async def mock_llm_stream(*_, **__):
    yield "JARVIS is online and ready."


@pytest.mark.asyncio
async def test_full_voice_llm_tts_pipeline(monkeypatch, test_message):
    monkeypatch.setattr(
        brain,
        "reason_stream",
        mock_llm_stream,
    )

    response = []
    async for chunk in chat_pipeline.chat_stream(
        user_id=test_message["user_name"],
        user_message=test_message["message"],
    ):
        response.append(chunk)

    assert any("online" in part.lower() for part in response)


@pytest.mark.asyncio
async def test_chat_reply_with_error_on_empty_message(monkeypatch, test_message):
    with pytest.raises(Exception):
        await chat_pipeline.chat_reply(
            user_id=test_message["user_name"],
            user_message="",
        )
