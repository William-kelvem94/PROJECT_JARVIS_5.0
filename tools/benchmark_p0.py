import time
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def run_benchmarks():
    print("\n" + "═"*60)
    print(" JARVIS 5.0 - PHASE 1 (P0) PERFORMANCE BENCHMARK ".center(60, "═"))
    print("═"*60)

    # 1. OCR Latency Check
    try:
        from core.vision_system import get_vision_system
        vision = get_vision_system(Path("data"))
        # Force load models
        vision._load_ocr_background()
        
        print("\n[BENCHMARK] OCR Latency (GPU-Accelerated)...")
        # Dummy image extraction test
        import numpy as np
        dummy_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        latencies = []
        for i in range(5):
            start = time.time()
            _ = vision.ocr_reader.readtext(dummy_img)
            latencies.append(time.time() - start)
            print(f"  Attempt {i+1}: {latencies[-1]*1000:.0f}ms")
            
        avg = sum(latencies) / len(latencies) * 1000
        status = "✅ PASS" if avg < 500 else "⚠️  FAIL (Target <500ms)"
        print(f"\n>> OCR AVG: {avg:.0f}ms | {status}")
        
    except Exception as e:
        print(f"❌ OCR Benchmark Error: {e}")

    # 2. Boot Analysis (Requires parsing logs or manual tracking)
    print("\n[INFO] Boot Time Target: <6s")
    print("      (Check main app logs for real-world profiling)")
    
    print("\n" + "═"*60 + "\n")

if __name__ == "__main__":
    run_benchmarks()
