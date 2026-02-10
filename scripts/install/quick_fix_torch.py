"""
🔧 Quick Fix - Install PyTorch Only
Instala apenas torch e torchvision quando faltam
"""
import sys
import subprocess
import platform

def check_cuda():
    """Verifica se tem GPU NVIDIA"""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, shell=True)
        return result.returncode == 0
    except:
        return False

def install_pytorch():
    """Instala PyTorch com a configuração correta"""
    print("🧠 Installing PyTorch...")
    print("=" * 60)
    
    # Remove versões antigas que podem causar conflito
    print("[1/3] Removing old PyTorch installations...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"],
            capture_output=True
        )
    except:
        pass
    
    print("[2/3] Detecting hardware configuration...")
    
    # Detecta se tem CUDA
    has_cuda = check_cuda()
    
    if has_cuda:
        print("    🎮 NVIDIA GPU detected!")
        print("[3/3] Installing PyTorch with CUDA support...")
        cmd = [
            sys.executable, "-m", "pip", "install",
            "torch>=2.4.0", "torchvision>=0.19.0", "torchaudio>=2.4.0",
            "--index-url", "https://download.pytorch.org/whl/cu121"
        ]
    else:
        print("    💻 CPU-only system detected")
        print("[3/3] Installing PyTorch CPU version (optimized)...")
        cmd = [
            sys.executable, "-m", "pip", "install",
            "torch==2.4.1+cpu", "torchvision==0.19.1+cpu", "torchaudio==2.4.1+cpu",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\n✅ PyTorch installation successful!")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed!")
        print(f"Error: {e.stderr[:500]}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = install_pytorch()
    sys.exit(0 if success else 1)
