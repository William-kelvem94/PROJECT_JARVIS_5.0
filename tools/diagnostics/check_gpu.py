import torch
import sys


def check_gpu():
    print(f"Python Version: {sys.version}")
    print(f"PyTorch Version: {torch.__version__}")

    if torch.cuda.is_available():
        print("✅ CUDA Available: True")
        print(f"   Device Count: {torch.cuda.device_count()}")
        print(f"   Current Device: {torch.cuda.current_device()}")
        print(f"   Device Name: {torch.cuda.get_device_name(0)}")
    else:
        print("❌ CUDA Available: False")
        print("   Running on CPU (Adaptive Mode Active)")


if __name__ == "__main__":
    check_gpu()
