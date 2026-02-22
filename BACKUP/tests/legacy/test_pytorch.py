"""
🔬 Test PyTorch Installation
Quick diagnostic for torch/torchvision
"""

import sys


def run_pytorch_diagnostic():
    print("=" * 70)
    print("[DIAGNOSTIC] PYTORCH DIAGNOSTIC TEST")
    print("=" * 70)

    # Test 1: Can we import torch?
    print("\n[TEST 1] Importing torch...")
    try:
        import torch

        print("[OK] torch imported")
        print(f"   Version: {torch.__version__}")
        print(f"   Location: {torch.__file__}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        raise

    # Test 2: Can we import torchvision?
    print("\n[TEST 2] Importing torchvision...")
    try:
        import torchvision

        print("[OK] torchvision imported")
        print(f"   Version: {torchvision.__version__}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        raise

    # Test 3: Basic tensor operations
    print("\n[TEST 3] Basic tensor operations...")
    try:
        x = torch.tensor([1, 2, 3, 4, 5], dtype=torch.float32)
        y = x * 2
        assert y.sum().item() == 30, "Tensor math failed"
        print("[OK] tensor math works")
        print(f"   Input: {x}")
        print(f"   Output: {y}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        raise

    # Test 4: CUDA availability
    print("\n[TEST 4] CUDA availability...")
    if torch.cuda.is_available():
        print("[OK] CUDA AVAILABLE")
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA Version: {torch.version.cuda}")
    else:
        print("[INFO] CPU-only mode (no CUDA)")

    # Test 5: Can we create a simple model?
    print("\n[TEST 5] Creating simple neural network...")
    try:
        import torch.nn as nn

        class TestModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(10, 1)

            def forward(self, x):
                return self.fc(x)

        model = TestModel()
        test_input = torch.randn(1, 10)
        output = model(test_input)
        print("[OK] neural network works")
        print(f"   Input shape: {test_input.shape}")
        print(f"   Output shape: {output.shape}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        raise

    print("\n" + "=" * 70)
    print("[DONE] ALL TESTS PASSED - PyTorch is working correctly!")
    print("=" * 70)


# Only run diagnostics when executed directly; pytest will simply import
# this module
if __name__ == "__main__":
    run_pytorch_diagnostic()
