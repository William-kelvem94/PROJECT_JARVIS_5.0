"""
🚀 INSTALADOR TOTAL JARVIS 5.0 - VERSÃO ULTRA RESILIENTE (FIXED VERSION)
Corrigido: dlib wheel name, PyTorch >=2.4, face_recognition_models
"""
import os
import sys
import subprocess
import json
import urllib.request
import tempfile
import time
import ctypes
from pathlib import Path
import logging

class TotalInstaller:
    """Instala TUDO que o JARVIS precisa com as correções críticas do usuário"""
    
    def __init__(self):
        # Detecção dinâmica do ROOT (scripts/install/total_installer.py -> root)
        self.project_root = Path(__file__).parent.parent.parent
        self.setup_logging()
        self.logger.info(f"📍 Projeto detectado em: {self.project_root}")
        
    def setup_logging(self):
        """Configura logging ultra robusto"""
        logging.root.handlers = []
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.project_root / 'logs' / 'total_installer.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        if sys.platform == "win32":
            try:
                import io
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
            except:
                pass

    def _check_cuda(self):
        """Verifica se tem GPU NVIDIA com CUDA"""
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, shell=True)
            return result.returncode == 0
        except:
            return False

    def run_command(self, cmd, skip_capture=False):
        """Executa comando de forma segura com tratamento de encoding resiliente"""
        try:
            self.logger.info(f"⚡ Executando: {' '.join(cmd[:5])}...")
            
            if skip_capture:
                # Streaming mode: deixa o processo imprimir direto no terminal
                # Isso evita buffering gigante em comandos como 'pip install torch'
                subprocess.run(cmd, check=True)
                return ""
            
            # Captura binária para evitar crashes de decode no pipe do Windows
            result = subprocess.run(cmd, check=True, capture_output=True, text=False)
            return result.stdout.decode('utf-8', errors='replace')
        except subprocess.CalledProcessError as e:
            if not skip_capture:
                err_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "Unknown error"
                self.logger.error(f"❌ Falha: {err_msg[:500]}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado: {e}")
            raise

    def install_pytorch_correct(self):
        """Instala PyTorch versão CORRETA (>=2.4)"""
        self.logger.info("🧠 Instalando PyTorch 2.4+...")
        
        # REMOVE versão antiga para evitar conflitos
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"], capture_output=True)
        except:
            pass
        
        # Instala versão NOVA (CPU ou CUDA)
        if self._check_cuda():
            self.logger.info("🎮 GPU detectada! Instalando PyTorch 2.4+ CUDA 12.1...")
            torch_cmd = [
                sys.executable, "-m", "pip", "install",
                "torch>=2.4.0", "torchvision>=0.19.0", "torchaudio>=2.4.0",
                "--index-url", "https://download.pytorch.org/whl/cu121"
            ]
        else:
            self.logger.info("💻 CPU detectada. Instalando PyTorch 2.4.1+cpu (Stable)...")
            torch_cmd = [
                sys.executable, "-m", "pip", "install",
                "torch==2.4.1+cpu", "torchvision==0.19.1+cpu", "torchaudio==2.4.1+cpu",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ]
        
        self.run_command(torch_cmd, skip_capture=True)

    def _download_dlib_wheel(self):
        """Download do wheel CORRETO do dlib com nome exato"""
        python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
        wheel_name = f"dlib-19.24.0-{python_version}-{python_version}-win_amd64.whl"
        
        wheel_urls = [
            f"https://github.com/z-mahmud22/Dlib_Wheels/releases/download/v19.24.0/{wheel_name}",
            f"https://github.com/sachadee/Dlib-builds/releases/download/v19.24.0/{wheel_name}",
            f"https://github.com/ZeroReiNull/dlib-python/raw/main/dlib-19.24.1-{python_version}-{python_version}-win_amd64.whl"
        ]
        
        temp_dir = tempfile.gettempdir()
        
        # Se for 19.24.1 o nome muda levemente, mas vamos tentar manter o nome que o PIP espera ou o nome real do download
        for url in wheel_urls:
            # Extrair nome real da URL se possível ou usar o padrão
            target_name = url.split('/')[-1]
            wheel_path = os.path.join(temp_dir, target_name)
            
            try:
                self.logger.info(f"📦 Baixando dlib wheel: {target_name}")
                urllib.request.urlretrieve(url, wheel_path)
                if os.path.exists(wheel_path):
                    return wheel_path
            except Exception as e:
                self.logger.warning(f"⚠️ Falha ao baixar de {url}: {e}")
                continue
        
        return None

    def install_face_recognition_complete(self):
        """Instala face_recognition COMPLETO"""
        self.logger.info("👤 Instalando face_recognition completo...")
        
        # 1. Instala modelos primeiro (via GIT como solicitado)
        self.logger.info("📦 Instalando face_recognition_models via git...")
        try:
            self.run_command([
                sys.executable, "-m", "pip", "install",
                "git+https://github.com/ageitgey/face_recognition_models"
            ], skip_capture=True)
        except Exception as e:
            self.logger.error(f"❌ Falha ao instalar modelos via git: {e}. Tentando via pip padrão...")
            try:
                self.run_command([sys.executable, "-m", "pip", "install", "face-recognition-models"], skip_capture=True)
            except:
                pass
        
        # 2. Instala face_recognition
        self.run_command([
            sys.executable, "-m", "pip", "install",
            "face-recognition>=1.3.0"
        ], skip_capture=True)

    def install_all(self):
        """Instala TUDO na ordem correta"""
        self.logger.info("🚀 INICIANDO INSTALAÇÃO JARVIS 5.0 (CORRIGIDA)")
        
        # 1. Update PIP
        self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], skip_capture=True)

        # 2. PyTorch correto (>=2.4)
        self.install_pytorch_correct()
        
        # 3. Dependências básicas
        self.logger.info("📦 Instalando dependências básicas...")
        basic_deps = ["numpy==1.26.4", "pandas", "scipy", "pyyaml", "python-dotenv", "PyQt6", "customtkinter", "pillow", "opencv-python", "mss", "ultralytics", "easyocr"]
        for dep in basic_deps:
            try: self.run_command([sys.executable, "-m", "pip", "install", dep], skip_capture=True)
            except: pass
        
        # 4. dlib via wheel CORRETO
        dlib_wheel = self._download_dlib_wheel()
        if dlib_wheel and os.path.exists(dlib_wheel):
            self.logger.info(f"🧠 Instalando dlib via wheel local: {dlib_wheel}")
            try:
                self.run_command([sys.executable, "-m", "pip", "install", dlib_wheel], skip_capture=True)
            except Exception as e:
                self.logger.error(f"❌ Falha ao instalar wheel: {e}")
        else:
            self.logger.warning("⚠️ Não foi possível baixar um wheel compatível. Tentando dlib-bin...")
            try: self.run_command([sys.executable, "-m", "pip", "install", "dlib-bin"], skip_capture=True)
            except: pass
        
        # 5. face_recognition COMPLETO
        self.install_face_recognition_complete()
        
        # 6. Restante das dependências
        self.logger.info("📦 Instalando dependências restantes (Voz, Web, etc.)...")
        remaining = [
            "transformers", "tokenizers", "sentence-transformers", "accelerate",
            "SpeechRecognition", "pyaudio", "pyttsx3", "edge-tts", "librosa", "faster-whisper",
            "webrtcvad-wheels", "pytesseract", "pyautogui", "psutil", "chromadb",
            "fastapi", "uvicorn[standard]", "pywin32", "onnxruntime>=1.17.0",
            "openvino-dev>=2024.1.0", "optimum-intel[openvino,nncf]>=1.18.0"
        ]
        
        # Resemblyzer separado (no-deps)
        try: self.run_command([sys.executable, "-m", "pip", "install", "resemblyzer", "--no-deps"], skip_capture=True)
        except: pass

        for dep in remaining:
            try: self.run_command([sys.executable, "-m", "pip", "install", dep], skip_capture=True)
            except: pass

        # 7. Final Fix for Transformers & NumPy (Enforce version < 2)
        self.logger.info("🧹 Finalizing environment constraints...")
        self.run_command([sys.executable, "-m", "pip", "install", "transformers", "tokenizers", "numpy<2", "-U"], skip_capture=True)
        
        self.logger.info("\n" + "="*50)
        self.logger.info("🎉 INSTALAÇÃO FINALIZADA!")
        self.logger.info("Por favor, execute: python test_install.py")
        self.logger.info("="*50)

if __name__ == "__main__":
    installer = TotalInstaller()
    installer.install_all()
