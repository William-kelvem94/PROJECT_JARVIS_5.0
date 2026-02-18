import os, multiprocessing

os.environ['JARVIS_VISION_MOCK'] = '1'

def child():
    from src.core.config.system_manifest import system_manifest
    print('CHILD: system_manifest.vision.mock_camera =', system_manifest.vision.mock_camera)

p = multiprocessing.Process(target=child)
p.start()
p.join()
print('parent done')