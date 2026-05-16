"""Tests for UnifiedMemory system."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock

@pytest.fixture
def mock_memory():
    with patch('app.unified_memory.chromadb', None), \
         patch('app.unified_memory.SentenceTransformer', None), \
         patch('app.unified_memory.db_manager') as mock_db:
        from app.unified_memory import UnifiedMemory
        mem = UnifiedMemory()
        mock_conn = MagicMock()
        mock_db.get_connection.return_value.__enter__.return_value = mock_conn
        yield mem, mock_conn

@pytest.mark.asyncio
async def test_add_memory_returns_false_for_duplicate(mock_memory, test_user_id, test_memory_content):
    mem, mock_conn = mock_memory
    mock_conn.execute.return_value.fetchone.return_value = {"id": 1}
    result = await mem.add_memory(test_user_id, test_memory_content, "fact", "conversation")
    assert result is False

@pytest.mark.asyncio
async def test_add_memory_returns_true_for_new(mock_memory, test_user_id):
    mem, mock_conn = mock_memory
    mock_conn.execute.return_value.fetchone.return_value = None
    result = await mem.add_memory(test_user_id, "new content", "fact", "conversation")
    assert result is True

@pytest.mark.asyncio
async def test_get_all_returns_memories(mock_memory, test_user_id):
    mem, mock_conn = mock_memory
    mock_conn.execute.return_value.fetchall.return_value = [
        {"content": "memory1", "updated_at": "2026-01-01"},
        {"content": "memory2", "updated_at": "2026-01-02"},
    ]
    result = await mem.get_all(test_user_id)
    assert len(result) == 2
    assert result[0]["content"] == "memory1"

def test_is_vault_available_returns_false():
    with patch('app.unified_memory.JARVIS_VAULT_DIR', None):
        from app.unified_memory import memory
        assert memory.is_vault_available() is False
