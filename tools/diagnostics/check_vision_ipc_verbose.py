import multiprocessing, time, os
from src.core.vision.vision_process import run_vision_service

os.environ['JARVIS_VISION_MOCK'] = '1'
q_to = multiprocessing.Queue()
q_from = multiprocessing.Queue()
p = multiprocessing.Process(target=run_vision_service, args=(q_to,q_from), name='VisionTestProcess')
p.start()
print('Child started, pid=', p.pid)
for i in range(6):
    print('alive?', p.is_alive())
    try:
        item = q_from.get(timeout=1)
        print('PARENT: received from child queue:', item)
        break
    except Exception as e:
        print('PARENT: no item on queue (attempt', i,')')
        time.sleep(0.2)
print('alive after wait?', p.is_alive())
if not p.is_alive():
    print('exitcode=', p.exitcode)
else:
    print('process still alive, terminating...')
    p.terminate()
    p.join(timeout=2)
    print('joined, exitcode=', p.exitcode)
