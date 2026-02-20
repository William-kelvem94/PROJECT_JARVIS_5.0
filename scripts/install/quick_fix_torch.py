"""
🔧 Quick Fix - Install PyTorch Only
Instala apenas torch e torchvision quando faltam
"""

import sys
import subprocess


def check_cuda():
    """Verifica se tem GPU NVIDIA"""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True)
        return result.returncode == 0
    except BaseException:
        return False


def install_pytorch():
    """Instala PyTorch com a configuração correta"""
    print("🧠 Installing PyTorch...")
    print("=" * 60)

    # Remove versões antigas que podem causar conflito
    print("[1/3] Removing old PyTorch installations...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "uninstall",
                "torch",
                "torchvision",
                "torchaudio",
                "-y",
            ],
            capture_output=True,
        )
    except BaseException:
        pass

    print("[2/3] Detecting hardware configuration...")

    # Detecta se tem CUDA
    has_cuda = check_cuda()

    if has_cuda:
        print("    🎮 NVIDIA GPU detected!")
        print("[3/3] Installing PyTorch with CUDA support...")
        # Install PyTorch without torchvision first to avoid NumPy conflicts
        cmd_torch = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torch>=2.4.0",
            "--index-url",
            "https://download.pytorch.org/whl/cu121",
        ]
        cmd_vision = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torchvision>=0.19.0",
            "torchaudio>=2.4.0",
            "--index-url",
            "https://download.pytorch.org/whl/cu121",
            "--no-deps",
        ]

        try:
            result = subprocess.run(
                cmd_torch, check=True, capture_output=True, text=True
            )
            result = subprocess.run(
                cmd_vision, check=True, capture_output=True, text=True
            )
            print("\n✅ PyTorch installation successful!")
            print("=" * 60)
            return True
        except subprocess.CalledProcessError as e:
            print("\n❌ Installation failed!")
            print(f"Error: {e.stderr[:500]}")
            print("=" * 60)
            return False
    else:
        print("    💻 CPU-only system detected")
        print("[3/3] Installing PyTorch CPU version (optimized)...")
        # Install PyTorch without torchvision first to avoid NumPy conflicts
        cmd_torch = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torch==2.4.1+cpu",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
        ]
        cmd_vision = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torchvision==0.19.1+cpu",
            "torchaudio==2.4.1+cpu",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
            "--no-deps",
        ]

        try:
            result = subprocess.run(
                cmd_torch, check=True, capture_output=True, text=True
            )
            result = subprocess.run(
                cmd_vision, check=True, capture_output=True, text=True
            )
            print("\n✅ PyTorch installation successful!")
            print("=" * 60)
            return True
        except subprocess.CalledProcessError as e:
            print("\n❌ Installation failed!")
            print(f"Error: {e.stderr[:500]}")
            print("=" * 60)
            return False


if __name__ == "__main__":
    success = install_pytorch()
    sys.exit(0 if success else 1)
