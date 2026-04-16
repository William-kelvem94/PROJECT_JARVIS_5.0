# Script para instalar PyTorch com CUDA no Desktop (i3 + GTX 1050 Ti)
# Execute este script no terminal do desktop

echo "Desinstalando PyTorch CPU..."
pip uninstall torch torchvision torchaudio -y

echo "Instalando PyTorch com CUDA 11.8..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "Verificando instalação..."
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"