import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.web.web_server import get_training_data


@pytest.mark.asyncio
async def test_get_training_data_success():
    # Mock get_training_dir to return a mocked Path
    with patch("src.web.web_server.get_training_dir") as mock_get_dir:
        mock_path = MagicMock()
        mock_get_dir.return_value = mock_path
        mock_path.exists.return_value = True

        # Mock glob
        file1 = MagicMock()
        file1.__str__.return_value = "file1.json"
        file2 = MagicMock()
        file2.__str__.return_value = "file2.json"

        # glob returns an iterator/generator, so return a list is fine as list() consumes it
        mock_path.glob.return_value = [file1, file2]

        # Patch builtins.open and json.load to simulate file reading
        # We mock json.load to avoid dealing with file handles and read() logic
        with patch("builtins.open") as mock_open:
            with patch("json.load") as mock_json_load:
                mock_json_load.side_effect = [
                    {"id": 1, "content": "file1"},
                    {"id": 2, "content": "file2"},
                ]

                response = await get_training_data(api_key="test")

                assert response.status_code == 200
                body = json.loads(response.body)
                assert len(body) == 2
                assert body[0]["id"] == 1
                assert body[1]["id"] == 2


@pytest.mark.asyncio
async def test_get_training_data_no_dir():
    with patch("src.web.web_server.get_training_dir") as mock_get_dir:
        mock_path = MagicMock()
        mock_get_dir.return_value = mock_path
        mock_path.exists.return_value = False

        response = await get_training_data(api_key="test")

        assert response.status_code == 200
        body = json.loads(response.body)
        assert body == []


@pytest.mark.asyncio
async def test_get_training_data_error_handling():
    with patch("src.web.web_server.get_training_dir") as mock_get_dir:
        mock_path = MagicMock()
        mock_get_dir.return_value = mock_path
        mock_path.exists.return_value = True

        # Simulate an error during glob or directory access
        mock_path.glob.side_effect = Exception("Disk error")

        response = await get_training_data(api_key="test")

        assert response.status_code == 500
        body = json.loads(response.body)
        assert "error" in body
