import asyncio
import sys
from PyQt6.QtWidgets import QApplication

from src.interface.stark_dashboard import StarkDashboard
from src.core.infrastructure.async_event_bus import get_event_bus, EventType


def test_stark_dashboard_shows_and_responds_to_approval_request():
    app = QApplication.instance() or QApplication(sys.argv)

    dashboard = StarkDashboard()

    bus = get_event_bus()

    captured_responses = []

    async def _flow():
        # ensure clean event bus state and start dispatcher
        await bus.stop()
        await bus.start()

        # ensure dashboard subscribes to approvals (must succeed inside running loop)
        assert dashboard.start_approval_listener() is True

        # subscribe to approval responses to assert publish from UI
        def _resp_handler(ev):
            captured_responses.append(ev.data)

        bus.subscribe([EventType.ACTION_APPROVAL_RESPONSE], _resp_handler)

        # Also subscribe locally to confirm EventBus dispatch
        approval_requests = []

        def _req_handler(ev):
            approval_requests.append(ev)

        bus.subscribe([EventType.ACTION_APPROVAL_REQUEST], _req_handler)

        # Publish an approval request and use the returned event id as request_id
        req_id = bus.publish(
            EventType.ACTION_APPROVAL_REQUEST,
            {"action": {"action_type": "file_modify", "target": "src/core/main.py"}},
            source="unittest",
        )

        # allow dispatch and UI update (give dispatcher more time)
        await asyncio.sleep(0.5)
        app.processEvents()

        # EventBus should have dispatched the request to subscribers
        assert any(e.id == req_id for e in approval_requests), "EventBus did not dispatch ACTION_APPROVAL_REQUEST to subscribers"

        # Wait for the dashboard to receive and display the pending approval
        found = False
        for _ in range(10):
            if req_id in dashboard._pending_approval_widgets:
                found = True
                break
            await asyncio.sleep(0.05)
            app.processEvents()

        assert found, "StarkDashboard did not register pending approval within timeout"

        # Simulate user clicking APPROVE
        approve_btn = dashboard._pending_approval_widgets[req_id]["approve_button"]
        approve_btn.click()

        # process Qt events and allow bus to dispatch
        app.processEvents()
        await asyncio.sleep(0.1)

        # Ensure response was published
        assert any(d.get("request_id") == req_id and d.get("approved") is True for d in captured_responses)

        # Widget should be removed from UI
        assert req_id not in dashboard._pending_approval_widgets

        await bus.stop()

    asyncio.run(_flow())
