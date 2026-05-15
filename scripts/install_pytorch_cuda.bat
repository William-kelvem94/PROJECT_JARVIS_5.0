@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] .venv nao encontrada. Rode start-jarvis.bat primeiro.
  exit /b 1
)

echo [CUDA] Instalando PyTorch CUDA 11.8 para GPUs NVIDIA compativeis.
echo [CUDA] Perfil recomendado para GTX 1050 Ti 4GB: cu118 + modelos tiny/base.

"%PYTHON_EXE%" -m pip uninstall torch torchvision torchaudio -y
"%PYTHON_EXE%" -m pip install -r "%ROOT%backend\app\requirements-torch-cu118.txt"
if errorlevel 1 exit /b 1

"%PYTHON_EXE%" -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
exit /b %errorlevel%
