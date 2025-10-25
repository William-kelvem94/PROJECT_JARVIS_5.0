"""
Chat functionality tests
"""
import pytest
from fastapi.testclient import TestClient
from app.models.user import User


def test_create_conversation(client: TestClient, auth_headers: dict):
    """Test conversation creation"""
    response = client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={
            "title": "Test Conversation",
            "model_name": "llama2"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert data["model_name"] == "llama2"


def test_list_conversations(client: TestClient, auth_headers: dict):
    """Test listing user conversations"""
    # Create a conversation first
    client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={"title": "Test"}
    )
    
    response = client.get(
        "/api/v1/conversations",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_conversation(client: TestClient, auth_headers: dict):
    """Test getting conversation with messages"""
    # Create conversation
    create_response = client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={"title": "Test"}
    )
    conversation_id = create_response.json()["id"]
    
    # Get conversation
    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id
    assert "messages" in data


def test_delete_conversation(client: TestClient, auth_headers: dict):
    """Test deleting conversation"""
    # Create conversation
    create_response = client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={"title": "Test"}
    )
    conversation_id = create_response.json()["id"]
    
    # Delete conversation
    response = client.delete(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404

