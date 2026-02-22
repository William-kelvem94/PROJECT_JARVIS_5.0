import multiprocessing, time
from src.core.infrastructure.ipc_event_bridge import IPCEventBridge

q_to = multiprocessing.Queue()
q_from = multiprocessing.Queue()
bridge = IPCEventBridge(q_from, q_to)
bridge.start()
print('bridge started, pending len =', len(bridge._pending_remote_events))
# Give the bridge thread a moment to spin up
time.sleep(0.6)
print('bridge thread warmup done')
# Put an event into the inbox before event_bus.start()
print('putting item into inbox')
q_from.put({'type': 'vision.ready', 'data': {'mock': True, 'available': True}})
# Wait for the bridge thread to process
time.sleep(1.0)
print('after put, pending len =', len(bridge._pending_remote_events))
print('pending item:', list(bridge._pending_remote_events))
bridge.stop()
