"""
INSTALADOR TOTAL JARVIS 5.0 - VERSAO ULTRA RESILIENTE (FIXED VERSION)
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
        self.logger.info(f"[INFO] Projeto detectado em: {self.project_root}")
        
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
            self.logger.info(f"++ Executando: {' '.join(cmd[:5])}...")
            
            if skip_capture:
                # Streaming mode: deixa o processo imprimir direto no terminal
                # Isso evita buffering gigante em comandos como 'pip install torch'
                subprocess.run(cmd, check=True)
                return ""
            
            # Captura binária para evitar crashes de decode no pipe do Windows
            result = subprocess.run(cmd, check=True, capture_output=True, text=False)
            
            # Decode com fallback robusto para Windows
            stdout = ""
            if result.stdout:
                try:
                    stdout = result.stdout.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        stdout = result.stdout.decode('cp1252', errors='replace')
                    except:
                        stdout = result.stdout.decode('utf-8', errors='replace')
            
            return stdout
        except subprocess.CalledProcessError as e:
            if not skip_capture:
                err_msg = ""
                err_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "Unknown error"
                self.logger.error(f"[ERR] Falha: {err_msg[:500]}")
            raise
        except Exception as e:
            self.logger.error(f"[ERR] Erro inesperado: {e}")
            raise

    def install_pytorch_correct(self):
        """Instala PyTorch versão CORRETA (>=2.4)"""
        self.logger.info("[SYS] Instalando PyTorch 2.4+...")
        
        # REMOVE versão antiga para evitar conflitos (Seguro contra encoding)
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"], 
                           capture_output=True, text=False)
        except:
            pass
        
        # Instala versão NOVA (CPU ou CUDA)
        if self._check_cuda():
            self.logger.info("[GPU] GPU detectada! Instalando PyTorch 2.4+ CUDA 12.1...")
            torch_cmd = [
                sys.executable, "-m", "pip", "install",
                "torch>=2.4.0", "torchvision>=0.19.0", "torchaudio>=2.4.0",
                "--index-url", "https://download.pytorch.org/whl/cu121"
            ]
        else:
            self.logger.info("[SYS] CPU detectada. Instalando PyTorch 2.4.1+cpu (Stable)...")
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
                self.logger.info(f"[DOWN] Baixando dlib wheel: {target_name}")
                urllib.request.urlretrieve(url, wheel_path)
                if os.path.exists(wheel_path):
                    return wheel_path
            except Exception as e:
                self.logger.warning(f"[WARN] Falha ao baixar de {url}: {e}")
                continue
        
        return None

    def install_face_recognition_complete(self):
        """Instala face_recognition COMPLETO"""
        self.logger.info("[SYS] Instalando face_recognition completo...")
        
        # 1. Instala modelos primeiro (via GIT como solicitado)
        self.logger.info("[DOWN] Instalando face_recognition_models via git...")
        try:
            self.run_command([
                sys.executable, "-m", "pip", "install",
                "git+https://github.com/ageitgey/face_recognition_models"
            ], skip_capture=True)
        except Exception as e:
            self.logger.error(f"[ERR] Falha ao instalar modelos via git: {e}. Tentando via pip padrao...")
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
        self.logger.info("[START] INICIANDO INSTALACAO JARVIS 5.0 (CORRIGIDA)")
        
        # 1. Update PIP
        self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], skip_capture=True)

        # 2. PyTorch correto (>=2.4)
        self.install_pytorch_correct()
        
        # 3. Dependências básicas
        self.logger.info("[DOWN] Instalando dependencias basicas...")
        basic_deps = ["numpy==1.26.4", "pandas", "scipy", "pyyaml", "python-dotenv", "PyQt6", "customtkinter", "pillow", "opencv-python", "mss"]
        for dep in basic_deps:
            try: self.run_command([sys.executable, "-m", "pip", "install", dep], skip_capture=True)
            except: pass
        
        # Forçar NumPy 1.26.4 ANTES de instalar ultralytics/easyocr
        try: self.run_command([sys.executable, "-m", "pip", "install", "--force-reinstall", "numpy==1.26.4"], skip_capture=True)
        except: pass
        
        # Instalar ultralytics após NumPy correto
        try: self.run_command([sys.executable, "-m", "pip", "install", "ultralytics"], skip_capture=True)
        except: pass
        
        # Instalar easyocr após NumPy correto
        try: self.run_command([sys.executable, "-m", "pip", "install", "easyocr"], skip_capture=True)
        except: pass
        
        # Forçar NumPy correto novamente após easyocr
        try: self.run_command([sys.executable, "-m", "pip", "install", "--force-reinstall", "numpy==1.26.4"], skip_capture=True)
        except: pass
        
        # 4. dlib via wheel CORRETO
        dlib_wheel = self._download_dlib_wheel()
        if dlib_wheel and os.path.exists(dlib_wheel):
            self.logger.info(f"[SYS] Instalando dlib via wheel local: {dlib_wheel}")
            try:
                self.run_command([sys.executable, "-m", "pip", "install", dlib_wheel], skip_capture=True)
            except Exception as e:
                self.logger.error(f"[ERR] Falha ao instalar wheel: {e}")
        else:
            self.logger.warning("[WARN] Nao foi possivel baixar um wheel compativel. Tentando dlib-bin...")
            try: self.run_command([sys.executable, "-m", "pip", "install", "dlib-bin"], skip_capture=True)
            except: pass
        
        # 5. face_recognition COMPLETO
        self.install_face_recognition_complete()
        
        # 5.5. Dependências faltantes críticas (resemblyzer, etc.)
        self.logger.info("[SYS] Instalando dependencias faltantes criticas...")
        critical_missing = ["typing", "webrtcvad>=2.0.10"]
        for dep in critical_missing:
            try: self.run_command([sys.executable, "-m", "pip", "install", dep], skip_capture=True)
            except: pass

        # 6. Restante das dependencias
        self.logger.info("[DOWN] Instalando dependencias restantes (Voz, Web, etc.)...")
        
        # Install packages that might pull NumPy 2.x with --no-deps
        numpy_conflicting = ["optimum-intel[openvino,nncf]>=1.18.0", "openvino-dev>=2024.1.0", "onnxruntime>=1.17.0,<1.18.0"]
        for dep in numpy_conflicting:
            try: self.run_command([sys.executable, "-m", "pip", "install", dep, "--no-deps"], skip_capture=True)
            except: pass

        # Install remaining packages normally
        remaining = [
            "transformers>=4.36,<4.54", "tokenizers", "sentence-transformers", "accelerate",
            "SpeechRecognition", "pyaudio", "pyttsx3", "edge-tts", "librosa", "soundfile", 
            "faster-whisper", "webrtcvad-wheels", "pytesseract", "pyautogui", "psutil", 
            "chromadb", "fastapi", "uvicorn[standard]", "pywin32", "wmi", 
            "screen-brightness-control", "resemblyzer"
        ]
        
        for dep in remaining:
            try: self.run_command([sys.executable, "-m", "pip", "install", dep], skip_capture=True)
            except: pass


        # 7. Final Fix for Transformers & NumPy (Enforce version < 2)
        self.logger.info("[FIX] Finalizing environment constraints...")
        self.run_command([sys.executable, "-m", "pip", "install", "transformers", "tokenizers", "-U"], skip_capture=True)
        
        # FORCE NumPy 1.26.4 at the VERY END after all packages are installed
        self.logger.info("[FIX] Enforcing NumPy 1.26.4 compatibility...")
        try: self.run_command([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"], skip_capture=True)
        except: pass
        try: self.run_command([sys.executable, "-m", "pip", "install", "numpy==1.26.4", "--no-deps"], skip_capture=True)
        except: pass
        
        self.logger.info("\n" + "="*50)
        self.logger.info("[DONE] INSTALACAO FINALIZADA!")
        self.logger.info("Por favor, execute: python test_install.py")
        self.logger.info("="*50)

if __name__ == "__main__":
    installer = TotalInstaller()
    installer.install_all()
