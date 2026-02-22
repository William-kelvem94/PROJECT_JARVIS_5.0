import os
import time
import asyncio
import multiprocessing

from src.core.config.system_manifest import system_manifest
from src.core.vision.vision_system import VisionSystem
from src.core.vision.vision_process import run_vision_service
from src.core.infrastructure.ipc_event_bridge import IPCEventBridge
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority

from src.core.vision.camera_controller import CameraController


def test_mock_camera_capture_and_non_blocking_start():
    """VisionSystem should use MockVideoCapture when configured and start quickly."""
    # Ensure mock mode in-process
    system_manifest.vision.mock_camera = True

    v = VisionSystem(use_multiprocessing=False)

    start = time.time()
    v.start_monitoring()
    duration = time.time() - start

    # start_monitoring must return quickly (non-blocking)
    assert duration < 0.5, f"start_monitoring blocked for {duration}s"

    # capture a frame (should be immediate and non-empty)
    frame = v.capture_webcam_frame()
    assert frame is not None
    assert hasattr(frame, "shape")

    # shape should be consistent with manifest resolution (may be rotated by
    # different backends)
    width, height = system_manifest.vision.resolution
    assert frame.shape[2] == 3

    v.stop_monitoring()


def test_camera_controller_mock_nonblocking():
    """CameraController should use MockVideoCapture when mock is enabled and not block."""
    system_manifest.vision.mock_camera = True

    c = CameraController()
    start = time.time()
    c.start_monitoring()
    assert time.time() - start < 0.5

    ctx = c.capture_context()
    assert "timestamp" in ctx
    assert isinstance(ctx.get("face_detected"), bool)

    c.stop_monitoring()


def test_vision_service_ipc_responds_quickly_with_mock_camera():
    """Start run_vision_service in a subprocess with mock camera (via env) and verify IPC RTTs are low."""
    # Ensure child process sees mock camera env var
    os.environ["JARVIS_VISION_MOCK"] = "1"

    multiprocessing.freeze_support()

    queue_to_vision = multiprocessing.Queue()
    queue_from_vision = multiprocessing.Queue()

    vision_process = multiprocessing.Process(
        target=run_vision_service,
        args=(queue_to_vision, queue_from_vision),
        name="VisionTestProcess",
        daemon=True,
    )
    vision_process.start()

    async def _run_ipc_test():
        local_bridge = IPCEventBridge(queue_from_vision, queue_to_vision, event_bus)
        local_bridge.start()

        await event_bus.start()

        results = []
        ready_received = []

        async def on_echo(event):
            request_ts = event.data.get("request_ts")
            if request_ts:
                rtt = (asyncio.get_event_loop().time() - request_ts) * 1000
                results.append(rtt)

        async def on_ready(event):
            ready_received.append(event.data)

        event_bus.subscribe([EventType.VISION_SCREEN_ANALYSIS], on_echo)
        event_bus.subscribe([EventType.VISION_READY], on_ready)

        # Allow service to boot
        await asyncio.sleep(1.0)

        # Ensure we received a VISION_READY event
        wait_start = time.time()
        while len(ready_received) < 1 and (time.time() - wait_start) < 2:
            await asyncio.sleep(0.05)

        assert len(ready_received) >= 1
        assert ready_received[0].get("mock") is True
        assert ready_received[0].get("available") is True

        # Send a few pings
        for i in range(8):
            ts = asyncio.get_event_loop().time()
            event_bus.publish(
                EventType.VISION_ANALYZE,
                {"payload": f"ping_{i}", "ts": ts},
                priority=EventPriority.HIGH,
            )
            await asyncio.sleep(0.05)

        # Wait for responses
        wait_start = time.time()
        while len(results) < 8 and (time.time() - wait_start) < 3:
            await asyncio.sleep(0.05)

        # Cleanup
        local_bridge.stop()
        await event_bus.stop()

        return results

    results = asyncio.run(_run_ipc_test())

    # Ensure we received all echoes and RTTs are small (mock camera => no
    # hardware delay)
    assert len(results) == 8, f"Expected 8 echoes, got {len(results)}"
    assert sum(results) / len(results) < 300.0

    vision_process.terminate()
    vision_process.join(timeout=1)
