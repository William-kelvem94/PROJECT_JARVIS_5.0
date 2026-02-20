import sys
sys.path.insert(0,'.')
try:
    import src.core.vision.vision_process as vp
    print("vision_process import OK")
except Exception as e:
    print("vision_process FAIL:", e)
