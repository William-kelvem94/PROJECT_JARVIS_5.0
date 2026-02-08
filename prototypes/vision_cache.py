import cv2
import numpy as np
import time
import hashlib

class VisionCache:
    """
    Vision Cache P1 Prototype
    Optimizes screen processing by skipping identical or near-identical frames.
    """
    def __init__(self, threshold=0.98, resize_dim=(64, 64)):
        self.threshold = threshold
        self.resize_dim = resize_dim
        self.last_frame_hash = None
        self.last_frame_data = None
        self.hits = 0
        self.misses = 0

    def calculate_hash(self, frame):
        """Calculates a fast perceptual hash (D-Hash)."""
        # Convert to grayscale and resize
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (self.resize_dim[0] + 1, self.resize_dim[1]))
        
        # Difference between adjacent pixels
        diff = resized[:, 1:] > resized[:, :-1]
        return hashlib.md5(diff.tobytes()).hexdigest()

    def compare_frames(self, frame1, frame2):
        """Calculates Structural Similarity or simple MSE."""
        if frame1 is None or frame2 is None:
            return 0.0
            
        # Downsample for speed
        f1 = cv2.resize(frame1, (128, 128))
        f2 = cv2.resize(frame2, (128, 128))
        
        # Mean Squared Error
        err = np.sum((f1.astype("float") - f2.astype("float")) ** 2)
        err /= float(f1.shape[0] * f1.shape[1] * 3)
        
        # Convert error to similarity (approximate)
        # Max error is 255^2, so we normalize
        similarity = 1 - (err / (255**2))
        return similarity

    def should_process(self, frame):
        """
        Determines if the frame has changed enough to warrant processing.
        """
        start_time = time.time()
        
        # Step 1: Fast Hashing
        current_hash = self.calculate_hash(frame)
        
        if current_hash == self.last_frame_hash:
            self.hits += 1
            return False, 0, time.time() - start_time
            
        # Step 2: Finer comparison if hash is different
        similarity = self.compare_frames(frame, self.last_frame_data)
        
        if similarity > self.threshold:
            self.hits += 1
            return False, similarity, time.time() - start_time
            
        # Significant change detected
        self.misses += 1
        self.last_frame_hash = current_hash
        self.last_frame_data = frame.copy()
        return True, similarity, time.time() - start_time

if __name__ == "__main__":
    # Quick internal test
    print("VisionCache module loaded.")
