import sys, logging, traceback, time
logging.disable(logging.CRITICAL)
sys.path.insert(0,'.')
out = []

steps = [
    ('import psutil', lambda: __import__('psutil')),
    ('import win32gui', lambda: __import__('win32gui')),
    ('import win32com.client', lambda: __import__('win32com.client')),
    ('import pycaw', lambda: __import__('pycaw.pycaw', fromlist=['AudioUtilities'])),
    ('import wmi', lambda: __import__('wmi')),
    ('SystemIntegrator()', lambda: __import__('src.core.actions.system_integrator', fromlist=['SystemIntegrator']).SystemIntegrator()),
    ('get_system_integrator()', lambda: __import__('src.core.actions.system_integrator', fromlist=['get_system_integrator']).get_system_integrator()),
]

for name, fn in steps:
    t0 = time.time()
    try:
        fn()
        elapsed = time.time() - t0
        out.append(f'OK ({elapsed:.2f}s): {name}')
    except Exception as e:
        elapsed = time.time() - t0
        out.append(f'FAIL ({elapsed:.2f}s): {name} -> {type(e).__name__}: {str(e)[:200]}')

with open('data/logs/integrator_test.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
