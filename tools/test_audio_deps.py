import torch
import torchaudio
import os
from faster_whisper import WhisperModel

print(f"Torch Version: {torch.__version__}")
print(f"Torchaudio Version: {torchaudio.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

try:
    print("Loading Whisper model (tiny)...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    print("✅ Whisper model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load Whisper: {e}")
