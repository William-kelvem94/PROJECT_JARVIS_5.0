"""
JARVIS 5.0 - SISTEMA AUTO-INTELIGENTE (OTIMIZADO & RESILIENTE)
Instala, corrige, configura e persiste automaticamente.
"""

import sys
import os
import subprocess
import importlib
import shutil
import json
import time
import io
from pathlib import Path
import logging
from datetime import datetime


class DependencyCache:
    """Cache de validação de dependências para inicialização rápida"""

    def __init__(self, cache_file):
        self.cache_file = Path(cache_file)
        self.cache_duration = 86400  # 24 horas
        self.data = self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except BaseException:
                pass
        return {}

    def is_valid(self, key):
        if key in self.data:
            entry = self.data[key]
            if time.time() - entry.get("timestamp", 0) < self.cache_duration:
                return True
        return False

    def set_valid(self, key):
        self.data[key] = {"timestamp": time.time(), "status": "valid"}
        self._save()

    def _save(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.data, f)


class JarvisAutoSystem:
    """Sistema inteligente que se auto-configura e corrige"""

    def __init__(self):
        # Corrigido para detectar a raiz real do projeto (subir 2 níveis de
        # scripts/install)
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.data_dir / "logs"

        for d in [self.config_dir, self.data_dir, self.logs_dir]:
            d.mkdir(exist_ok=True, parents=True)

        self.cache = DependencyCache(self.data_dir / "dependency_cache.json")
        self.setup_logging()

    def setup_logging(self):
        """Configura logging com UTF-8 forçado para Windows"""
        # FORÇA UTF-8 NO WINDOWS
        if sys.platform == "win32":
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )

        # Remove handlers existentes
        logging.root.handlers = []

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    self.logs_dir
                    / f'jarvis_auto_{datetime.now().strftime("%Y%m%d")}.log',
                    encoding="utf-8",
                ),
                self._create_windows_safe_handler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _create_windows_safe_handler(self):
        """Cria handler seguro para Windows com fallback de emojis"""

        class WindowsSafeStreamHandler(logging.StreamHandler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    if sys.platform == "win32":
                        msg = self._replace_emojis(msg)
                    stream = self.stream
                    stream.write(msg + self.terminator)
                    self.flush()
                except Exception:
                    self.handleError(record)

            def _replace_emojis(self, text):
                replacements = {
                    "✅": "[OK]",
                    "❌": "[ERRO]",
                    "⚠️": "[AVISO]",
                    "🔄": "[ATUALIZANDO]",
                    "📦": "[PACOTE]",
                    "🔧": "[CORRIGINDO]",
                    "🚀": "[INICIANDO]",
                    "🔍": "[VERIFICANDO]",
                    "⚡": "[RÁPIDO]",
                    "🧠": "[IA]",
                    "👁️": "[VISÃO]",
                    "🎤": "[VOZ]",
                }
                for emoji, replacement in replacements.items():
                    text = text.replace(emoji, replacement)
                return text

        return WindowsSafeStreamHandler(sys.stdout)

    def backup_file(self, file_path):
        """Cria backup antes de modificações críticas"""
        path = Path(file_path)
        if path.exists():
            backup_path = (
                self.data_dir / "backups" / f"{path.name}.{int(time.time())}.bak"
            )
            backup_path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy2(path, backup_path)
            self.logger.info(f"Backup criado: {backup_path}")
            return backup_path
        return None

    def intelligent_dependency_installer(self):
        if self.cache.is_valid("all_dependencies"):
            self.logger.info("⚡ Dependências validadas recentemente")
            return True

        self.logger.info("📦 Validando dependências...")
        critical_deps = {
            "torch": self._install_pytorch_intelligent,
            "mss": self._install_mss,
            "face_recognition": self._install_face_recognition,
            "PyQt6": self._install_pyqt6,
            "transformers": self._install_transformers,
            "faster_whisper": self._install_faster_whisper,
            "torchaudio": self._install_torchaudio,
            "resemblyzer": self._install_resemblyzer,
        }

        all_ok = True
        for dep, installer in critical_deps.items():
            try:
                importlib.import_module(dep.replace("-", "_"))
                self.logger.info(f"✅ {dep} OK")
            except ImportError:
                all_ok = False
                self.logger.warning(f"⚠️ {dep} faltando")
                installer()

        if all_ok:
            self.cache.set_valid("all_dependencies")
        return all_ok

    def _install_pytorch_intelligent(self):
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torch",
            "torchvision",
            "--extra-index-url",
            "https://download.pytorch.org/whl/cpu",
        ]
        subprocess.run(cmd)

    def _install_mss(self):
        subprocess.run([sys.executable, "-m", "pip", "install", "mss"])

    def _install_pyqt6(self):
        subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6"])

    def _install_transformers(self):
        subprocess.run([sys.executable, "-m", "pip", "install", "transformers==4.30.2"])

    def _install_faster_whisper(self):
        subprocess.run([sys.executable, "-m", "pip", "install", "faster-whisper"])

    def _install_torchaudio(self):
        try:
            import torch

            v = torch.__version__
            pkg = (
                "torchaudio==2.1.0"
                if "2.1" in v
                else "torchaudio==2.0.2" if "2.0" in v else "torchaudio"
            )
            subprocess.run([sys.executable, "-m", "pip", "install", pkg])
        except BaseException:
            subprocess.run([sys.executable, "-m", "pip", "install", "torchaudio"])

    def _install_resemblyzer(self):
        subprocess.run([sys.executable, "-m", "pip", "install", "resemblyzer"])

    def _install_face_recognition(self):
        """Instala face_recognition no Windows sem compilação local se possível"""
        self.logger.info("🔄 Tentando instalação otimizada do face_recognition...")
        try:
            # Tenta baixar wheel pré-compilado para Python 3.11 se for o caso
            if sys.version_info.major == 3 and sys.version_info.minor == 11:
                wheel = "dlib-19.24.0-cp311-cp311-win_amd64.whl"
                url = f"https://github.com/zakaria-Ghe/dlib-19.24.0-windows-python-3.11/releases/download/v1.0.0/{wheel}"
                import urllib.request

                self.logger.info(f"Baixando wheel: {wheel}")
                urllib.request.urlretrieve(url, wheel)
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", wheel], check=True
                )
                os.remove(wheel)

            subprocess.run(
                [sys.executable, "-m", "pip", "install", "face-recognition"], check=True
            )
            self.logger.info("✅ face_recognition instalado")
        except Exception as e:
            self.logger.warning(f"⚠️ Falha no dlib otimizado: {e}. Usando fallback.")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "opencv-python",
                    "pillow",
                    "numpy",
                ]
            )

    def validate_system(self):
        self.logger.info("🔍 Validando Sistema...")
        files = [
            "src/core/engine/autonomy.py",
            "main.py",
            "src/utils/system_monitor.py",
        ]
        results = {
            f: "OK" if (self.project_root / f).exists() else "MISSING" for f in files
        }
        return results

    def auto_fix(self):
        self.intelligent_dependency_installer()
        hud_path = self.project_root / "src" / "interface" / "hud.py"
        if hud_path.exists():
            with open(hud_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "ReactorWidget" not in content:
                self.backup_file(hud_path)
                with open(hud_path, "a", encoding="utf-8") as f:
                    f.write("\n\nclass ReactorWidget: pass # Stub\n")
        return True


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--auto-fix", action="store_true")
    p.add_argument("--validate", action="store_true")
    args = p.parse_args()
    sys_auto = JarvisAutoSystem()
    if args.auto_fix:
        sys_auto.auto_fix()
    if args.validate:
        print(sys_auto.validate_system())


if __name__ == "__main__":
    main()
