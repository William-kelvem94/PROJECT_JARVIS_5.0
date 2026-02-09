import cv2
import numpy as np
import time
from vision_cache import VisionCache

def generate_simulated_frame(mode="static", noise=0):
    """Generates a dummy frame for testing."""
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    # Add a "UI element"
    cv2.rectangle(frame, (100, 100), (500, 500), (0, 255, 0), -1)
    cv2.putText(frame, "JARVIS P1 CACHE TEST", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    if mode == "dynamic":
        # Simulate cursor movement
        cursor_pos = (int(time.time() * 100) % 1920, int(time.time() * 50) % 1080)
        cv2.circle(frame, cursor_pos, 10, (0, 0, 255), -1)
        
    if noise > 0:
        actual_noise = np.random.normal(0, noise, frame.shape).astype(np.uint8)
        frame = cv2.add(frame, actual_noise)
        
    return frame

def run_benchmark():
    cache = VisionCache(threshold=0.99)
    total_frames = 100
    
    print(f"🚀 Starting Benchmark: {total_frames} frames simulation...")
    print("-" * 50)
    
    start_sim = time.time()
    
    # Scene 1: Static Screen (e.g., reading a doc)
    print("Scene 1: Static Screen (50 frames)")
    static_frame = generate_simulated_frame(mode="static")
    for _ in range(50):
        should_proc, sim, lat = cache.should_process(static_frame)
        
    # Scene 2: Minor changes (e.g., cursor blinking)
    print("Scene 2: Minor variations (30 frames)")
    for i in range(30):
        # Slightly vary the frame with noise
        varied_frame = generate_simulated_frame(mode="static", noise=1 if i % 2 == 0 else 0)
        should_proc, sim, lat = cache.should_process(varied_frame)
        
    # Scene 3: High Activity (e.g., coding/scrolling)
    print("Scene 3: High Activity (20 frames)")
    for _ in range(20):
        dynamic_frame = generate_simulated_frame(mode="dynamic")
        should_proc, sim, lat = cache.should_process(dynamic_frame)
        
    end_sim = time.time()
    
    print("-" * 50)
    print(f"✅ Benchmark Finished in {end_sim - start_sim:.4f}s")
    print(f"📊 Results:")
    print(f"   - Total Frames: {total_frames}")
    print(f"   - Cache HITS (Skipped): {cache.hits} ({cache.hits/total_frames*100:.1f}%)")
    print(f"   - Cache MISSES (Processed): {cache.misses} ({cache.misses/total_frames*100:.1f}%)")
    print(f"   - Optimization: ~{cache.hits/total_frames*100:.1f}% reduction in AI processing workload")
    print("-" * 50)

if __name__ == "__main__":
    run_benchmark()
