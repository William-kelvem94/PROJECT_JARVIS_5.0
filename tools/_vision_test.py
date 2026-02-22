import sys, logging
logging.disable(logging.CRITICAL)
sys.path.insert(0,'.')
out = []
try:
    import src.core.vision.vision_system as m
    import inspect
    sig = inspect.signature(m.VisionSystem.__init__)
    out.append('SIG: ' + str(sig))
    from pathlib import Path
    v = m.get_vision_system(Path('data'))
    out.append('OK: ' + type(v).__name__)
except Exception as e:
    import traceback
    out.append('FAIL: ' + type(e).__name__ + ' ' + str(e)[:500])
    out.append(traceback.format_exc())

with open('data/logs/vision_test.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
