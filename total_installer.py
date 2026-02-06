"""
🚀 INSTALADOR TOTAL JARVIS 5.0 - VERSÃO ULTRA RESILIENTE (WHEEL-FOCUSED)
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
    """Instala TUDO que o JARVIS precisa usando Wheels pré-compilados quando possível"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.setup_logging()
        
    def setup_logging(self):
        """Configura logging ultra robusto"""
        logging.root.handlers = []
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.project_root / 'total_installer.log', encoding='utf-8'),
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
    
    def install_python_dependencies(self):
        """Instala TODAS as dependências de forma inteligente"""
        self.logger.info("🐍 INICIANDO INSTALAÇÃO DE DEPENDÊNCIAS...")
        
        # 1. Update PIP
        self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 2. PyTorch (Fixed Version)
        self.logger.info("🧠 Instalando PyTorch CPU (Otimizado para Windows)...")
        self.run_command([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        
        # 3. Main Groups
        dependencies = [
            # Core & Data
            ["numpy<2", "pandas>=2.0.0", "scipy>=1.10.0", "pyyaml", "python-dotenv"],
            # GUI
            ["PyQt6>=6.5.0", "customtkinter>=5.2.0", "pillow"],
            # Vision
            ["opencv-python>=4.8.0", "opencv-contrib-python>=4.8.0", "mss", "ultralytics"],
            # IA & NLP
            ["transformers", "tokenizers", "sentence-transformers", "accelerate", "langchain"],
            # Voice Core
            ["SpeechRecognition", "pyaudio", "pyttsx3", "edge-tts", "gTTS", "librosa", "sounddevice", "faster-whisper"],
            # Tools & DB
            ["pytesseract", "easyocr", "pyautogui", "keyboard", "mouse", "psutil", "sqlalchemy", "chromadb", "watchdog"],
            # Web & Windows
            ["fastapi", "uvicorn[standard]", "websockets", "pywin32", "comtypes", "WMI", "pycaw"]
        ]
        
        for group in dependencies:
            try:
                self.run_command([sys.executable, "-m", "pip", "install"] + group)
            except:
                self.logger.warning(f"⚠️ Algum pacote no grupo {group} falhou. Continuando...")
        
        # 4. TRICKY PACKAGES (Wheels)
        self.logger.info("🔨 Instalando pacotes críticos via Wheels...")
        
        # dlib
        python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
        dlib_wheel = f"https://github.com/ZeroReiNull/dlib-python/raw/main/dlib-19.24.1-{python_version}-{python_version}-win_amd64.whl"
        
        try:
            self.logger.info(f"🧠 Instalando dlib wheel...")
            wheel_path = os.path.join(tempfile.gettempdir(), "dlib_jarvis.whl")
            urllib.request.urlretrieve(dlib_wheel, wheel_path)
            self.run_command([sys.executable, "-m", "pip", "install", wheel_path])
        except Exception as e:
            self.logger.error(f"❌ Falha no dlib wheel: {e}. Tentando dlib-bin...")
            try: self.run_command([sys.executable, "-m", "pip", "install", "dlib-bin"])
            except: pass

        # face-recognition
        try:
            self.logger.info("👤 Instalando face-recognition...")
            self.run_command([sys.executable, "-m", "pip", "install", "face-recognition"])
        except: pass

        # webrtcvad (via wheels version)
        try:
            self.logger.info("🎵 Instalando webrtcvad-wheels...")
            self.run_command([sys.executable, "-m", "pip", "install", "webrtcvad-wheels"])
        except: pass

        # resemblyzer (sem deps para não quebrar o vad)
        try:
            self.logger.info("🎙️ Instalando resemblyzer (no-deps)...")
            self.run_command([sys.executable, "-m", "pip", "install", "resemblyzer", "--no-deps"])
        except: pass

        # 5. Fix Transformers/Tokenizers Mismatch
        self.logger.info("🔄 Ajustando versões de Transformers e Tokenizers...")
        self.run_command([sys.executable, "-m", "pip", "install", "transformers", "tokenizers", "-U"])
    
    def run_command(self, cmd):
        """Executa comando de forma segura"""
        try:
            self.logger.info(f"⚡ {cmd[0]} {' '.join(cmd[1:5])}...")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Falha: {e.stderr[:200]}")
            raise

    def verify(self):
        """Verifica se tudo está pronto"""
        self.logger.info("\n🔍 VERIFICAÇÃO FINAL:")
        modules = ["torch", "cv2", "PyQt6", "transformers", "dlib", "face_recognition", "webrtcvad", "resemblyzer", "ultralytics"]
        results = {}
        for mod in modules:
            try:
                __import__(mod)
                results[mod] = "✅ OK"
            except Exception as e:
                results[mod] = f"❌ Error: {str(e)[:50]}"
        
        for mod, res in results.items():
            self.logger.info(f"{mod.ljust(20)}: {res}")
        
        return all("✅" in r for r in results.values())

    def run(self):
        self.logger.info("🚀 JARVIS 5.0 - STARTING TOTAL INSTALLATION")
        try:
            self.install_python_dependencies()
            if self.verify():
                self.logger.info("\n🎉 TUDO PRONTO! O JARVIS ESTÁ PRONTO PARA RODAR.")
                self.logger.info("Execute: JARVIS_AUTO.bat")
            else:
                self.logger.warning("\n⚠️ Instalação concluída com avisos. Verifique o log.")
        except Exception as e:
            self.logger.error(f"\n💥 ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    TotalInstaller().run()
