import pytest
import json
import shutil
import os
from pathlib import Path
from src.web.web_server import get_training_data

# Setup data directory path relative to project root (where tests run from)
DATA_REL_PATH = Path("data/learning/training_data")


@pytest.fixture
def setup_training_data():
    if DATA_REL_PATH.exists():
        shutil.rmtree(DATA_REL_PATH)
    DATA_REL_PATH.mkdir(parents=True, exist_ok=True)

    files_created = []
    for i in range(10):
        data = {
            "id": i,
            "content": f"content_{i}",
            "unsafe": "<script>alert(1)</script>",
        }
        file_path = DATA_REL_PATH / f"data_{i}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        files_created.append(data)

    yield files_created

    # Cleanup
    if DATA_REL_PATH.exists():
        shutil.rmtree(DATA_REL_PATH)
    # Try to remove parent dirs if empty
    try:
        os.rmdir("data/learning")
        os.rmdir("data")
    except OSError:
        pass


@pytest.mark.asyncio
async def test_get_training_data_returns_correct_sanitized_data(setup_training_data):
    # Execute
    # We pass a dummy api_key because in direct function call, dependencies are not resolved.
    response = await get_training_data("dummy_key")

    assert response.status_code == 200

    # response.body is bytes
    data = json.loads(response.body.decode())

    assert len(data) == 10

    # Check if data is sanitized
    for item in data:
        assert "<script>" not in item["unsafe"]
        # The regex `re.sub(r'<[^>]+>', '', text)` removes tags.
        # <script>alert(1)</script> -> alert(1)
        assert item["unsafe"] == "alert(1)"

    # Check ids
    ids = sorted([item["id"] for item in data])
    assert ids == list(range(10))


@pytest.mark.asyncio
async def test_get_training_data_empty():
    # Ensure no data exists
    if DATA_REL_PATH.exists():
        shutil.rmtree(DATA_REL_PATH)

    response = await get_training_data("dummy")
    data = json.loads(response.body.decode())
    assert data == []
    assert response.status_code == 200


def test_health_endpoint_is_public_and_returns_ok():
    from fastapi.testclient import TestClient
    from src.web.web_server import app

    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("status") == "ok"
    assert "uptime_seconds" in payload
