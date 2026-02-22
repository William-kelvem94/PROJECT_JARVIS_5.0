import multiprocessing, time
from src.core.vision.vision_process import run_vision_service
import os

os.environ['JARVIS_VISION_MOCK'] = '1'
q_to = multiprocessing.Queue()
q_from = multiprocessing.Queue()
p = multiprocessing.Process(target=run_vision_service, args=(q_to,q_from), daemon=True)
p.start()
try:
    # Wait for child to initialize and put events on outbox
    item = q_from.get(timeout=3)
    print('PARENT: received from child queue:', item)
except Exception as e:
    print('PARENT: no item on queue:', e)
finally:
    p.terminate()
    p.join()
