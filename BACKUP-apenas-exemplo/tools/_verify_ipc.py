import sys
sys.path.insert(0,'.')
from src.core.infrastructure.ipc_event_bridge import IPCEventBridge
import inspect

print("Signature:", inspect.signature(IPCEventBridge.__init__))
try:
    print("Trying instantiation...")
    from multiprocessing import Queue
    IPCEventBridge(Queue(), Queue(), event_bus=None)
    print("SUCCESS")
except Exception as e:
    print("FAIL:", e)
