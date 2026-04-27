import pytest
import asyncio
from datetime import datetime
from src.evolution.authorization_manager import HumanAuthorizationManager, AuthorizationRequest, ActionRiskLevel, AuthorizationStatus

@pytest.fixture
def auth_manager():
    return HumanAuthorizationManager()

@pytest.mark.asyncio
async def test_authorize_success(auth_manager):
    # Setup
    action = {"descricao": "Test action", "arquivo": "test.py", "codigo_corrigido": "print('test')"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Callback mock
    callback_called = False
    async def mock_callback(req):
        nonlocal callback_called
        callback_called = True

    auth_manager.on_approval(mock_callback)

    # Execute
    result = await auth_manager.authorize(request.id, "Approved for testing")

    # Assert
    assert result is True
    assert request.id not in auth_manager.pending_requests
    assert request in auth_manager.completed_requests
    assert request.status == AuthorizationStatus.APPROVED
    assert request.reason == "Approved for testing"
    assert callback_called is True

@pytest.mark.asyncio
async def test_authorize_not_found(auth_manager):
    result = await auth_manager.authorize("unknown_id")
    assert result is False

@pytest.mark.asyncio
async def test_authorize_already_processed(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    request.status = AuthorizationStatus.APPROVED
    auth_manager.pending_requests[request.id] = request

    # Execute
    result = await auth_manager.authorize(request.id)

    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_authorize_sync_callback(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Callback mock
    callback_called = False
    def mock_callback(req):
        nonlocal callback_called
        callback_called = True

    auth_manager.on_approval(mock_callback)

    # Execute
    result = await auth_manager.authorize(request.id)

    # Assert
    assert result is True
    assert callback_called is True

@pytest.mark.asyncio
async def test_authorize_callback_exception(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Error callback mock
    def error_callback(req):
        raise ValueError("Test error")

    # Valid callback to ensure it continues after error
    callback_called = False
    def valid_callback(req):
        nonlocal callback_called
        callback_called = True

    auth_manager.on_approval(error_callback)
    auth_manager.on_approval(valid_callback)

    # Execute
    result = await auth_manager.authorize(request.id)

    # Assert - should return true despite callback error
    assert result is True
    assert callback_called is True

@pytest.mark.asyncio
async def test_reject_success(auth_manager):
    # Setup
    action = {"descricao": "Test reject action"}
    request = AuthorizationRequest(action, ActionRiskLevel.HIGH)
    auth_manager.pending_requests[request.id] = request

    # Callback mock
    callback_called = False
    async def mock_callback(req):
        nonlocal callback_called
        callback_called = True

    auth_manager.on_rejection(mock_callback)

    # Execute
    result = await auth_manager.reject(request.id, "Rejected for testing")

    # Assert
    assert result is True
    assert request.id not in auth_manager.pending_requests
    assert request in auth_manager.completed_requests
    assert request.status == AuthorizationStatus.REJECTED
    assert request.reason == "Rejected for testing"
    assert callback_called is True

@pytest.mark.asyncio
async def test_reject_not_found(auth_manager):
    result = await auth_manager.reject("unknown_id")
    assert result is False

@pytest.mark.asyncio
async def test_reject_already_processed(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    request.status = AuthorizationStatus.REJECTED
    auth_manager.pending_requests[request.id] = request

    # Execute
    result = await auth_manager.reject(request.id)

    # Assert
    assert result is False

def test_get_statistics(auth_manager):
    # Setup
    action1 = {"descricao": "Action 1"}
    req1 = AuthorizationRequest(action1, ActionRiskLevel.LOW)
    auth_manager.pending_requests[req1.id] = req1

    action2 = {"descricao": "Action 2"}
    req2 = AuthorizationRequest(action2, ActionRiskLevel.HIGH)
    req2.status = AuthorizationStatus.APPROVED
    auth_manager.completed_requests.append(req2)

    action3 = {"descricao": "Action 3"}
    req3 = AuthorizationRequest(action3, ActionRiskLevel.CRITICAL)
    req3.status = AuthorizationStatus.REJECTED
    auth_manager.completed_requests.append(req3)

    # Execute
    stats = auth_manager.get_statistics()

    # Assert
    assert stats["total_requests"] == 3
    assert stats["pending"] == 1
    assert stats["approved"] == 1
    assert stats["rejected"] == 1
    assert stats["expired"] == 0
    assert stats["approval_rate"] == 50.0

def test_assess_risk(auth_manager):
    # High risk - many files
    action_high = {
        "files": ["f1.py", "f2.py", "f3.py", "f4.py", "f5.py", "f6.py"]
    }
    assert auth_manager._assess_risk(action_high) == ActionRiskLevel.HIGH

    # Medium risk - moderate files
    action_med = {
        "files": ["f1.py", "f2.py", "f3.py"]
    }
    assert auth_manager._assess_risk(action_med) == ActionRiskLevel.MEDIUM

    # Low risk
    action_low = {
        "files": ["f1.py"]
    }
    assert auth_manager._assess_risk(action_low) == ActionRiskLevel.LOW

    # Critical risk - protected file
    action_crit = {
        "arquivo": "src/core/infrastructure/db.py"
    }
    assert auth_manager._assess_risk(action_crit) == ActionRiskLevel.CRITICAL

@pytest.mark.asyncio
async def test_start_stop(auth_manager):
    assert auth_manager.running is False

    await auth_manager.start()
    assert auth_manager.running is True
    assert auth_manager._cleanup_task is not None

    # Starting again should return immediately
    await auth_manager.start()

    await auth_manager.stop()
    assert auth_manager.running is False

class MockEvent:
    def __init__(self, data):
        self.data = data

@pytest.mark.asyncio
async def test_handle_diagnostic_plan(auth_manager):
    auth_manager.running = True

    # Mix of low and high risk actions
    plan = {
        "plan": [
            {"descricao": "Low risk", "arquivo": "test.py", "files": ["test.py"]},
            {"descricao": "High risk", "arquivo": "main.py", "files": ["f1.py", "f2.py", "f3.py", "f4.py", "f5.py", "f6.py"]}
        ]
    }

    event = MockEvent(plan)
    await auth_manager._handle_diagnostic_plan(event)

    # Should have 1 pending request for the high risk action
    assert len(auth_manager.pending_requests) == 1

    # Check that it returns when not running
    auth_manager.running = False
    auth_manager.pending_requests.clear()
    await auth_manager._handle_diagnostic_plan(event)
    assert len(auth_manager.pending_requests) == 0

def test_get_requests(auth_manager):
    # Setup
    action = {"descricao": "Test"}
    req = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[req.id] = req

    # Test get_pending_requests
    pending = auth_manager.get_pending_requests()
    assert len(pending) == 1
    assert pending[0]["id"] == req.id

    # Test get_request
    assert auth_manager.get_request(req.id) is not None
    assert auth_manager.get_request("unknown") is None

    # Move to completed
    auth_manager.completed_requests.append(req)
    del auth_manager.pending_requests[req.id]
    assert auth_manager.get_request(req.id) is not None

@pytest.mark.asyncio
async def test_reject_callback_exception(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Error callback mock
    def error_callback(req):
        raise ValueError("Test error")

    auth_manager.on_rejection(error_callback)

    # Execute
    result = await auth_manager.reject(request.id)

    # Assert - should return true despite callback error
    assert result is True

@pytest.mark.asyncio
async def test_reject_sync_callback(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Callback mock
    callback_called = False
    def mock_callback(req):
        nonlocal callback_called
        callback_called = True

    auth_manager.on_rejection(mock_callback)

    # Execute
    result = await auth_manager.reject(request.id)

    # Assert
    assert result is True
    assert callback_called is True

@pytest.mark.asyncio
async def test_authorize_trim_history(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Fill completed history to max
    auth_manager.max_completed_history = 5
    for i in range(5):
        old_req = AuthorizationRequest({"descricao": f"Old {i}"}, ActionRiskLevel.LOW)
        auth_manager.completed_requests.append(old_req)

    # Execute
    result = await auth_manager.authorize(request.id)

    # Assert
    assert result is True
    assert len(auth_manager.completed_requests) == 5
    assert request in auth_manager.completed_requests

@pytest.mark.asyncio
async def test_reject_trim_history(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    auth_manager.pending_requests[request.id] = request

    # Fill completed history to max
    auth_manager.max_completed_history = 5
    for i in range(5):
        old_req = AuthorizationRequest({"descricao": f"Old {i}"}, ActionRiskLevel.LOW)
        auth_manager.completed_requests.append(old_req)

    # Execute
    result = await auth_manager.reject(request.id)

    # Assert
    assert result is True
    assert len(auth_manager.completed_requests) == 5
    assert request in auth_manager.completed_requests

from datetime import timedelta
@pytest.mark.asyncio
async def test_cleanup_expired_requests(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    request.expires_at = datetime.now() - timedelta(minutes=1) # Expired

    auth_manager.pending_requests[request.id] = request

    # Need to run a single iteration of the loop manually, since it's an infinite loop
    # We mock asyncio.sleep to break the loop
    async def mock_sleep(delay):
        auth_manager.running = False

    import copy
    original_sleep = asyncio.sleep
    asyncio.sleep = mock_sleep

    try:
        auth_manager.running = True
        await auth_manager._cleanup_expired_requests()

        # Assert
        assert request.id not in auth_manager.pending_requests
        assert request in auth_manager.completed_requests
        assert request.status == AuthorizationStatus.EXPIRED
    finally:
        asyncio.sleep = original_sleep

@pytest.mark.asyncio
async def test_cleanup_expired_requests_trim_history(auth_manager):
    # Setup
    action = {"descricao": "Test action"}
    request = AuthorizationRequest(action, ActionRiskLevel.LOW)
    request.expires_at = datetime.now() - timedelta(minutes=1) # Expired
    auth_manager.pending_requests[request.id] = request

    auth_manager.max_completed_history = 1
    old_req = AuthorizationRequest({"descricao": "Old"}, ActionRiskLevel.LOW)
    auth_manager.completed_requests.append(old_req)

    async def mock_sleep(delay):
        auth_manager.running = False

    original_sleep = asyncio.sleep
    asyncio.sleep = mock_sleep

    try:
        auth_manager.running = True
        await auth_manager._cleanup_expired_requests()

        # Assert
        assert len(auth_manager.completed_requests) == 1
        assert auth_manager.completed_requests[0] == request
    finally:
        asyncio.sleep = original_sleep

@pytest.mark.asyncio
async def test_cleanup_expired_requests_exception(auth_manager):
    # Setup
    # Create an object that will cause an exception in items()
    class BadDict:
        def items(self):
            raise ValueError("Test error")

    auth_manager.pending_requests = BadDict()

    # Track sleep call
    sleep_called = False
    async def mock_sleep(delay):
        nonlocal sleep_called
        sleep_called = True
        auth_manager.running = False # Break loop

    original_sleep = asyncio.sleep
    asyncio.sleep = mock_sleep

    try:
        auth_manager.running = True
        await auth_manager._cleanup_expired_requests()

        # Assert - exception caught and slept for 60 seconds
        assert sleep_called is True
    finally:
        asyncio.sleep = original_sleep
