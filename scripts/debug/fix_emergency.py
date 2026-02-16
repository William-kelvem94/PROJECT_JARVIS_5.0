import sys
import subprocess
import os

print("🔧 CORREÇÃO DE EMERGÊNCIA JARVIS 5.0")

# 1. Forçar UTF-8
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

# 2. Instalar pacotes críticos sem dlib
packages = [
    "opencv-python",
    "pillow",
    "mss",
    "PyQt6",
    "faster-whisper",
    "torchaudio",
    "resemblyzer",
]

for pkg in packages:
    print(f"📦 Instalando {pkg}...")
    subprocess.run([sys.executable, "-m", "pip", "install", pkg])

# 3. Verificar se torchaudio está instalado corretamente
try:
    import torch

    torch_version = torch.__version__
    print(f"✅ PyTorch {torch_version} detectado")

    # Instalar torchaudio compatível
    if "2.1" in torch_version:
        subprocess.run([sys.executable, "-m", "pip", "install", "torchaudio==2.1.0"])
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", "torchaudio"])
except:
    print("⚠️ PyTorch não encontrado")

print("✅ Correção de emergência aplicada!")
