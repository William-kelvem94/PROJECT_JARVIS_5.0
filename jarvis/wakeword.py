"""Simple, expandable wake-word detector (trainable) — optional PyTorch backend.

Behavior:
- If PyTorch + librosa are installed and a trained model exists at
  `jarvis/models/wakeword.pth`, `detect()` will use it.
- If dependencies or model are missing, `detect()` falls back to a
  conservative energy-threshold check so the system still works.

Notes:
- This is intentionally minimal so you can expand the architecture later.
"""
import os
import io
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "wakeword.pth")


def _energy_detect(wav_bytes: bytes, threshold: float = 0.01) -> bool:
    """Simple RMS energy-based hotword heuristic (fallback)."""
    try:
        import soundfile as sf
        arr, sr = sf.read(io.BytesIO(wav_bytes))
        if arr.ndim > 1:
            arr = arr.mean(axis=1)
        rms = np.sqrt(np.mean(arr.astype(float) ** 2))
        return rms > threshold
    except Exception:
        # If we can't compute RMS, be conservative and return False
        return False


def detect(wav_bytes: bytes, threshold: float = 0.5) -> bool:
    """Return True only if a trained neural model is present and signals the wakeword.

    - IMPORTANT: do NOT use the energy heuristic by default (to avoid false positives).
    - If no trained model/deps are available, return False so the listener falls back
      to STT-based hotword matching.
    """
    try:
        import torch
        import librosa
        if os.path.exists(MODEL_PATH):
            device = torch.device("cpu")
            model = torch.jit.load(MODEL_PATH, map_location=device)
            # extract features
            y, sr = librosa.load(io.BytesIO(wav_bytes), sr=16000, mono=True)
            mels = librosa.feature.melspectrogram(y, sr=sr, n_mels=64)
            mels_db = librosa.power_to_db(mels)
            x = torch.tensor(mels_db, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            with torch.no_grad():
                out = model(x)
                prob = torch.sigmoid(out).item()
            return prob >= threshold
    except Exception:
        # missing deps or model -> do not trigger
        return False

    return False


# Utilities for training / saving
def model_exists() -> bool:
    return os.path.exists(MODEL_PATH)


def ensure_models_dir():
    d = os.path.dirname(MODEL_PATH)
    os.makedirs(d, exist_ok=True)


if __name__ == "__main__":
    print("Wakeword module — call detect(bytes) from listener. Model exists:", model_exists())
