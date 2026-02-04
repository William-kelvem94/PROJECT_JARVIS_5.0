"""
Gerenciador de Manutenção e Auto-Reparo (Maintenance Manager)
Responsável por garantir que todas as dependências (Python e Sistema) estejam presentes.
Se algo estiver faltando, tenta instalar ou guia o usuário.
"""

import os
import sys
import subprocess
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.config import config

logger = logging.getLogger(__name__)

class MaintenanceManager:
    """Classe responsável por auto-reparo e verificação de saúde do sistema"""

    def __init__(self):
        self.is_cleaning = False
        self.repair_history = []
        self.on_progress: Optional[Callable[[str], None]] = None

    def check_and_repair_all(self):
        """Executa um check-up completo e tenta reparar o que for possível"""
        logger.info("Iniciando Verificação de Integridade do Sistema...")
        if self.on_progress: self.on_progress("SISTEMA: Iniciando verificação de integridade...")
        
        # 0. Alinhamento de bibliotecas base (NumPy)
        self._align_numpy()

        # 1. Sincronizar versões críticas (evitar conflitos mediapipe/protobuf)
        self._sync_critical_versions()

        
        # 2. Verificar dependências Python
        self._repair_python_deps()
        
        # 3. Verificar ferramentas de sistema (Tesseract, etc)
        self._check_system_tools()
        
        # 4. Verificar modelos de IA
        self._check_ai_models()
        
        if self.on_progress: self.on_progress("SISTEMA: Integridade verificada. Protocolos operacionais.")
        logger.info("Verificação de Integridade concluída.")

    def _align_numpy(self):
        """Força downgrade do NumPy se for >= 2.0 (incompatível com torch/mediapipe atual)"""
        try:
            import numpy as np
            ver = tuple(map(int, np.__version__.split('.')[:2]))
            if ver >= (2, 0):
                msg = f"Detectado NumPy {np.__version__} (Incompatível). Rebaixando para 1.26.4..."
                logger.warning(msg)
                if self.on_progress: self.on_progress(msg)
                self._pip_install("numpy==1.26.4 --force-reinstall")
        except Exception:
            pass

    def _sync_critical_versions(self):
        """Resolve conflitos conhecidos como Mediapipe + Protobuf"""
        # 1. Tentar detectar via import direto (se falhar, está quebrado)
        try:
            import google.protobuf
        except ImportError:
            logger.warning("Protobuf não encontrado. Sincronizando...")
            self._pip_install("protobuf==4.21.1") # Versão estável equilibrada
            return

        # 2. Corrigir erro específico de 'runtime_version' que aflige Mediapipe
        try:
            from google.protobuf import runtime_version
        except ImportError:
            msg = "Protobuf imcompatível detectado (runtime_version ausente). Alinhando..."
            logger.warning(msg)
            if self.on_progress: self.on_progress(msg)
            # 4.21.1 costuma ser o 'sweet spot' entre MediaPipe e TF moderno
            self._pip_install("protobuf==4.21.1 --force-reinstall")
            return

        # 3. Verificar versão mínima
        try:
            from google.protobuf import __version__ as proto_ver
            ver = tuple(map(int, proto_ver.split('.')[:2]))
            if ver < (3, 20):
                msg = f"Protobuf desatualizado ({proto_ver}). Sincronizando..."
                logger.warning(msg)
                if self.on_progress: self.on_progress(msg)
                self._pip_install("protobuf==3.20.3")
        except Exception:
            pass



    def _repair_python_deps(self):
        """Tenta importar módulos críticos e reinstala se falhar"""
        critical_modules = {
            "cv2": "opencv-contrib-python",
            "pyautogui": "pyautogui",
            "mediapipe": "mediapipe",
            "face_recognition": "face_recognition",
            "ultralytics": "ultralytics",
            "customtkinter": "customtkinter",
            "torch": "torch",
            "transformers": "transformers",
            "sentence_transformers": "sentence-transformers",
            "chromadb": "chromadb",
            "fer": "fer"
        }

        for module_name, pip_name in critical_modules.items():
            try:
                # Caso especial para Mediapipe que pode importar mas estar quebrado
                if module_name == "mediapipe":
                     import mediapipe as mp
                     if not hasattr(mp, 'solutions') and not hasattr(mp, 'tasks'):
                          raise ImportError("Mediapipe corrompido")
                else:
                    __import__(module_name)
                
                logger.debug(f"Dependência OK: {module_name}")
            except (ImportError, AttributeError):
                msg = f"Reparando pacote: {pip_name}..."
                logger.warning(msg)
                if self.on_progress: self.on_progress(msg)
                self._pip_install(pip_name)

    def _pip_install(self, package: str):
        """Executa instalação via pip com prioridade de usuário"""
        try:
            logger.info(f"Instalando {package}...")
            # Dividir a string de package para suportar args como --force-reinstall
            args = package.split()
            cmd = [sys.executable, "-m", "pip", "install"] + args + ["--no-cache-dir"]
            subprocess.check_call(cmd)
            return True
        except Exception as e:
            logger.error(f"Falha ao instalar {package}: {e}")
            return False


    def _check_system_tools(self):
        """Verifica se ferramentas externas como Tesseract estão instaladas"""
        tesseract_path = config.get_setting('ocr.tesseract_path', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        
        if not os.path.exists(tesseract_path):
            msg = "⚠️ Tesseract OCR não encontrado. Tentando localizar via PATH..."
            logger.warning(msg)
            if self.on_progress: self.on_progress(msg)
            
            # Tentar achar no PATH
            import shutil
            path_exec = shutil.which("tesseract")
            if path_exec:
                config.set_setting('ocr.tesseract_path', path_exec)
                logger.info(f"Tesseract encontrado via PATH: {path_exec}")
            else:
                 msg = "❌ Tesseract ausente. Funcionalidade de leitura de documentos desativada."
                 logger.error(msg)
                 if self.on_progress: self.on_progress(msg)

    def _check_ai_models(self):
        """Verifica se os arquivos de modelo necessários existem"""
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # 1. Modelos de Arquivo (YOLO, MediaPipe)
        models = {
            "yolov8n.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt",
            "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        }
        
        for model_name, url in models.items():
            model_path = models_dir / model_name
            if not model_path.exists():
                msg = f"⚙️ Baixando Modelo: {model_name}..."
                logger.info(msg)
                if self.on_progress: self.on_progress(msg)
                self._download_file(url, model_path)

        # 2. Verificação do Vosk (Voz Offline)
        vosk_path = models_dir / "vosk-model-small-pt-0.22"
        if not vosk_path.exists():
            logger.warning("Modelo Vosk PT-BR não encontrado. Assistente offline indisponível.")
            if self.on_progress: self.on_progress("AVISO: Modelo de voz offline ausente (vosk).")

        # 3. Verificação do Ollama e Modelos LLM
        self._check_ollama_and_models()


    def _check_ollama_and_models(self):
        """Verifica se Ollama está rodando e tem os modelos necessários"""
        ollama_url = config.get_setting('ai.ollama_url', 'http://localhost:11434/api/generate')
        base_url = ollama_url.replace("/api/generate", "")
        
        try:
            import requests
            # Verificar se Ollama está ONLINE
            try:
                requests.get(base_url, timeout=2)
                logger.info("Ollama detectado e configurado.")
            except:
                msg = "⚠️ Ollama não detectado. O 'Cérebro Local' pode não funcionar corretamente."
                logger.warning(msg)
                if self.on_progress: self.on_progress(msg)
                return

            # Verificar modelos carregados no Ollama
            required_models = ["llava", "qwen2.5:0.5b"]  # Modelos padrão do Jarvis
            try:
                resp = requests.get(f"{base_url}/api/tags")
                installed_models = [m['name'] for m in resp.json().get('models', [])]
                
                for model in required_models:
                    if not any(model in m for m in installed_models):
                        msg = f"⚙️ Baixando modelo local '{model}' via Ollama (pode demorar)..."
                        logger.info(msg)
                        if self.on_progress: self.on_progress(msg)
                        # Tentar pull (não-bloqueante para o log se possível)
                        subprocess.Popen(["ollama", "pull", model])
            except:
                pass
                
        except ImportError:
            pass


    def _download_file(self, url: str, dest_path: Path):
        """Baixa arquivo com progresso no log"""
        try:
            import requests
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(dest_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Notificar progresso a cada 1MB
                    if downloaded % (1024 * 1024) == 0 and self.on_progress:
                        percent = (downloaded / total_size) * 100 if total_size > 0 else 0
                        self.on_progress(f"⚙️ Download {dest_path.name}: {percent:.1f}%")
            
            logger.info(f"Download concluído: {dest_path}")
        except Exception as e:
            logger.error(f"Erro ao baixar {url}: {e}")
            if self.on_progress: self.on_progress(f"❌ Erro ao baixar {dest_path.name}")


# Instância global
maintenance_manager = MaintenanceManager()
