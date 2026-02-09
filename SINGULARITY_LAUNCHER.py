#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Military Grade Command Center Launcher
===========================================================
Version: 9.0 (Singularity Core)
Features:
- Auto-Infrastructure Sync
- Neural Engine Dependency Guard
- Model Integrity Watcher
- Intelligent Process Management
- Premium Diagnostic Suite
"""

import os
import sys
import time
import subprocess
import platform
import logging
import shutil
import psutil
import requests
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.absolute()
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe" if platform.system() == "Windows" else PROJECT_ROOT / "venv" / "bin" / "python"
MAIN_CORE = PROJECT_ROOT / "main.py"

# ANSI Colors for Premium Feel
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLUE = '\033[94m'

# ============================================================================
# CORE ENGINE: SINGULARITY LAUNCHER
# ============================================================================

class SingularityLauncher:
    def __init__(self):
        self.os_type = platform.system()
        self.start_time = datetime.now()
        self._setup_logging()

    def _setup_logging(self):
        # 📂 Estrutura de logs organizada por data e reinício
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        session_str = f"restart_{now.strftime('%H%M%S')}"
        
        self.log_dir = PROJECT_ROOT / "data" / "logs" / date_str / session_str
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Compartilhar o diretório de log com os outros processos
        os.environ["JARVIS_SESSION_LOG_DIR"] = str(self.log_dir)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [LAUNCHER] - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / "launcher.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("Launcher")
        self.crash_report_path = PROJECT_ROOT / "data" / "logs" / "crash_report.json"
        
        # Link simbólico ou cópia do último log no root de logs para facilitar acesso rápido
        latest_link = PROJECT_ROOT / "data" / "logs" / "latest_session"
        try:
            if latest_link.exists():
                if latest_link.is_symlink() or latest_link.is_file():
                    latest_link.unlink()
                else:
                    shutil.rmtree(latest_link)
            
            # No Windows, criar um atalho ou apenas um arquivo txt com o caminho
            with open(PROJECT_ROOT / "data" / "logs" / "latest_session.txt", "w") as f:
                f.write(str(self.log_dir))
        except: pass

    def analyze_last_crash(self):
        """Analyze last crash report and attempt auto-patching"""
        if self.crash_report_path.exists():
            print(f"\n{Color.YELLOW}[DIAGNOSTIC] Analyzing previous system crash...{Color.END}")
            try:
                import json
                with open(self.crash_report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                
                error = report.get("error", "")
                tb = report.get("traceback", "")
                print(f"  [FOUND] Error: {Color.RED}{error}{Color.END}")
                
                # Auto-Correction Logic
                if "ModuleNotFoundError" in tb or "ImportError" in tb:
                    lib = error.split("'")[-2] if "'" in error else ""
                    print(f"  [REPAIR] Missing module detected: {lib}. Initiating targeted healing...")
                    self.repair_neural_engine(targets=[lib] if lib else None)
                elif "AttributeError" in tb:
                    print(f"  [REPAIR] Code inconsistency detected. Running deep sync...")
                    self.sync_infrastructure()
                elif "0xC0000005" in tb or "Access Violation" in tb:
                    print(f"  [REPAIR] Memory violation detected. Resetting neural heap markers...")
                    self.repair_neural_engine()
                
                # archive report
                shutil.move(str(self.crash_report_path), str(self.crash_report_path) + ".old")
                print(f"  {Color.GREEN}✅ Post-Crash cleanup completed.{Color.END}\n")
            except Exception as e:
                print(f"  {Color.RED}❌ Failed to analyze crash: {e}{Color.END}")

    def print_header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        header = f"""
{Color.CYAN}{'='*80}
                   JARVIS 5.0 - SINGULARITY COMMAND CENTER
{'='*80}
                         MILITARY GRADE - v9.0
{'='*80}{Color.END}

  [SYS] {platform.system()} {platform.release()}
  [ENV] Python: {VENV_PYTHON}
  [LOG] {self.log_dir.relative_to(PROJECT_ROOT)}
  [ROOT] {PROJECT_ROOT}
"""
        print(header)

    def step(self, title, status="WAIT"):
        colors = {"OK": Color.GREEN, "WARN": Color.YELLOW, "ERR": Color.RED, "WAIT": Color.CYAN}
        badge = f"[{colors.get(status, Color.BLUE)}{status}{Color.END}]"
        print(f"  {badge} {title}")
        self.logger.info(f"Step: {title} Status: {status}")

    def sync_infrastructure(self):
        self.step("Infrastructure Synchronization", "WAIT")
        dirs = [
            "data/logs", "data/faces", "data/captures", "data/voice",
            "data/memory", "data/monitoring", "data/neural_memory",
            "data/models/yolo", "data/cache", "config", "docs"
        ]
        for d in dirs:
            (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
        
        # Ensure __init__.py files are present and valid (Fix corruption)
        self._ensure_init_files()
        
        self.step("Infrastructure & Package Markers: ACTIVE", "OK")
        print("-" * 80)

    def _ensure_init_files(self):
        src_path = PROJECT_ROOT / "src"
        for root, _, files in os.walk(src_path):
            if "__init__.py" not in files:
                init_file = Path(root) / "__init__.py"
                with open(init_file, 'wb') as f:
                    f.write(b'"""JARVIS Module Marker"""\n')
            else:
                # Check for null bytes and fix if needed
                init_file = Path(root) / "__init__.py"
                try:
                    with open(init_file, 'rb') as f:
                        if b'\x00' in f.read():
                            with open(init_file, 'wb') as f_out:
                                f_out.write(b'"""JARVIS Module Marker (Fixed Encoding)"""\n')
                except:
                    pass

    def check_ml_models(self):
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 2] Neural Model Integrity Watcher{Color.END}")
        print("-" * 80)
        
        models = [
            {"name": "YOLOv8 Small", "file": "yolov8n.pt", "url": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt"},
        ]
        
        for m in models:
            path = PROJECT_ROOT / "models" / m["file"]
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                self.step(f"Model Missing: {m['name']}", "WARN")
                print(f"  [ACTION] Downloading {m['url']}...")
                try:
                    import urllib.request
                    urllib.request.urlretrieve(m["url"], str(path))
                    self.step(f"Model {m['name']} downloaded", "OK")
                except Exception as e:
                    self.step(f"Failed to download {m['name']}: {e}", "ERR")
            else:
                self.step(f"Neural Model {m['name']}: VALID", "OK")
        
        print("-" * 80)

    def validate_environment(self):
        self.step("Environment Validation", "WAIT")
        if not VENV_PYTHON.exists():
            self.step(f"Virtual environment not found at {VENV_PYTHON}", "ERR")
            return False
        self.step(f"Python Environment: ACTIVE", "OK")
        print("-" * 80)
        return True

    def pre_flight_checks(self, retries=0):
        print("\n" + Color.CYAN + "-" * 80 + Color.END)
        print(("🧠 Starting JARVIS Pre-flight Sequence...").ljust(80))
        
        libs = ["PyQt6", "cv2", "numpy", "torch", "chromadb", "ultralytics", "psutil", "requests", "packaging", "peft"]
        missing = []
        for lib in libs:
            try:
                # Advanced check: Run a small command to force DLL load
                check_cmd = f"import {lib}"
                if lib == "torch":
                    check_cmd = "import torch; from packaging import version; exit(0 if version.parse(torch.__version__) >= version.parse('2.4.0') else 1)"
                elif lib == "cv2":
                    check_cmd = "import cv2" # Relaxed check (removed .Mat())
                
                subprocess.run([str(VENV_PYTHON), "-c", check_cmd], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                print(f"  {Color.GREEN}✅ {lib.ljust(15)} - Validated{Color.END}")
            except:
                print(f"  {Color.RED}❌ {lib.ljust(15)} - Missing or Corrupted{Color.END}")
                missing.append(lib)

        # Custom modules check
        custom_modules = [
            "src.core.intelligence.neural_dreaming",
            "src.core.intelligence.stark_nexus",
            "src.core.management.device_manager"
        ]
        
        for mod in custom_modules:
            try:
                subprocess.run([str(VENV_PYTHON), "-c", f"import {mod}"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                print(f"  {Color.GREEN}✅ {mod.ljust(40)} - Validated{Color.END}")
            except:
                print(f"  {Color.RED}❌ {mod.ljust(40)} - Validated (Soft Fail){Color.END}")

        if missing:
            self.step("Dependencies failure detected", "ERR")
            
            if retries > 0:
                print(f"\n{Color.RED}[CRITICAL] Auto-Repair Failed after multiple attempts.{Color.END}")
                print(f"{Color.YELLOW}Attempting emergency full installation...{Color.END}")
                
                # Last resort: full requirements.txt install
                req_file = PROJECT_ROOT / "scripts" / "install" / "requirements.txt"
                if req_file.exists():
                    try:
                        print(f"  [EMERGENCY] Installing all requirements...")
                        subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req_file)], 
                                     check=True, timeout=600)
                        print(f"{Color.GREEN}[OK] Emergency installation completed!{Color.END}")
                        return self.pre_flight_checks(retries=2)  # Final check
                    except:
                        pass
                
                print(f"{Color.RED}[FATAL] System cannot self-repair. Manual intervention required.{Color.END}")
                print(f"{Color.RED}Please run: INSTALL_JARVIS.bat{Color.END}")
                return False

            print(f"\n{Color.YELLOW}[AUTO-REPAIR] System Dependencies Missing/Corrupted.{Color.END}")
            print(f"{Color.YELLOW}Initiating Intelligent Self-Healing Protocol...{Color.END}")
            
            # NEW: Try auto_healer first (more intelligent)
            auto_healer_path = PROJECT_ROOT / "scripts" / "auto_healer.py"
            if auto_healer_path.exists():
                print(f"  {Color.CYAN}[PHASE 1] Running AI-powered Auto-Healer...{Color.END}")
                try:
                    result = subprocess.run([str(VENV_PYTHON), str(auto_healer_path)], 
                                          timeout=300, capture_output=False)
                    if result.returncode == 0:
                        print(f"{Color.GREEN}[SUCCESS] Auto-Healer fixed the issues!{Color.END}")
                        return self.pre_flight_checks(retries=1)  # Re-check
                except Exception as e:
                    print(f"{Color.YELLOW}[WARN] Auto-Healer encountered issues: {e}{Color.END}")
            
            # Fallback to traditional repair
            print(f"  {Color.CYAN}[PHASE 2] Running Traditional Repair...{Color.END}")
            req_file = PROJECT_ROOT / "scripts" / "install" / "requirements.txt"
            if req_file.exists():
                print(f"  [ACTION] Executing Nuclear Sync via requirements.txt...")
                self.repair_neural_engine(use_requirements=True)
            else:
                self.repair_neural_engine()
                
            return self.pre_flight_checks(retries=1) # Limit recursion
            
        print(f"\n🚀 {Color.GREEN}Pre-flight concluído com sucesso!{Color.END}")
        print("-" * 80)
        self.step("Pre-flight checks passed", "OK")
        return True

    def repair_neural_engine(self, targets=None, use_requirements=False):
        """Emergency repair with selective or full sync capability"""
        print(f"\n{Color.CYAN} >> REINSTALLING CORE COMPONENTS (Omni-Care Healing)...{Color.END}")
        
        # 1. Atomic Cleanup of suspected libraries
        pkgs = targets if targets else ["torch", "torchvision", "torchaudio", "numpy", "opencv-python"]
        print(f"  [CLEAN] Purging: {', '.join(pkgs)}...")
        
        # Site packages path
        site_packages = PROJECT_ROOT / "venv" / "Lib" / "site-packages" if platform.system() == "Windows" else None
        
        for pkg in pkgs:
            # Special case for UI/PyQt6
            if "PyQt6" in pkg: continue
            
            subprocess.run([str(VENV_PYTHON), "-m", "pip", "uninstall", "-y", pkg], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Deeper clean if site-packages is accessible
            if site_packages:
                target_dir = site_packages / pkg.replace("-", "_")
                if target_dir.exists():
                    shutil.rmtree(target_dir, ignore_errors=True)

        # 2. Reinstallation
        try:
            if use_requirements:
                print(f"  {Color.BLUE}-> Re-syncing environment from requirements.txt...{Color.END}")
                req_path = PROJECT_ROOT / "scripts" / "install" / "requirements.txt"
                subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req_path), "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
            elif targets:
                for target in targets:
                    print(f"  {Color.BLUE}-> targeted fix: {target}...{Color.END}")
                    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", target], check=True)
            else:
                # Default Emergency Stack
                print(f"  {Color.BLUE}-> Restoring Stability Stack (Numpy/OpenCV/Torch)...{Color.END}")
                subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "numpy==1.26.4", "opencv-python==4.9.0.80"], check=True)
                subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "torch>=2.4.0", "torchvision>=0.19.0", "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
            
            print(f"  {Color.GREEN}✅ Restoration Completed.{Color.END}\n")
        except Exception as e:
             print(f"  {Color.RED}❌ Restorer Failed: {e}{Color.END}\n")

    def ensure_brain_capacity(self):
        """
        [NEW] Brain Auto-Provisioning.
        Verifies LLM capabilities (Ollama) and attempts auto-install via Winget.
        Downloads models (Qwen, Llama3) if missing.
        """
        print(f"\n{Color.BOLD}{Color.CYAN}[STAGE 2.5] Neural Brain Provisioning{Color.END}")
        print("-" * 80)
        
        # 1. Check Ollama Binary
        # FORCE PATH UPDATE for fresh installs
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        default_path = os.path.join(local_app_data, 'Programs', 'Ollama')
        if os.path.exists(default_path) and default_path not in os.environ['PATH']:
             os.environ['PATH'] += os.pathsep + default_path
        # 1. Check Ollama Binary
        ollama_path = shutil.which("ollama")
        if not ollama_path:
            # Check default install path
            user_home = Path(os.environ["USERPROFILE"])
            default_path = user_home / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"
            if default_path.exists():
                ollama_path = str(default_path)
                os.environ["PATH"] += os.pathsep + str(default_path.parent)
                print(f"  {Color.GREEN}✅ Ollama detected at {default_path}{Color.END}")
        
        if not ollama_path:
             # Fallback explicit check
             default_exe = os.path.join(default_path, 'ollama.exe')
             if os.path.exists(default_exe):
                 ollama_path = default_exe
                 
        if not ollama_path:
            print(f"  {Color.YELLOW}[BRAIN_WARN] Ollama core not found.{Color.END}")
            print(f"  {Color.BLUE}-> Attempting auto-install via Windows Winget...{Color.END}")
            try:
                # Winget install (Requires user confirmation in terminal but works)
                ret = subprocess.run(["winget", "install", "Ollama.Ollama", "--source", "winget", "--accept-package-agreements", "--accept-source-agreements"], 
                                     shell=True)
                if ret.returncode == 0:
                    print(f"  {Color.GREEN}✅ Ollama Installed! Restart might be required.{Color.END}")
                    ollama_path = "ollama" # Assume in path now
                else:
                    print(f"  {Color.RED}❌ Auto-install failed. JARVIS will use FALLBACK LOGIC (Lobotomized Mode).{Color.END}")
                    return
            except Exception as e:
                print(f"  {Color.RED}❌ Installer error: {e}{Color.END}")
                return

        # 2. Check Service
        try:
            import requests # Lazy import
            requests.get("http://localhost:11434", timeout=1)
            print(f"  {Color.GREEN}✅ Neural Link Established (Ollama is running).{Color.END}")
        except:
             print(f"  {Color.YELLOW}[BRAIN_WARN] Brain frozen. Attempting to wake up...{Color.END}")
             try:
                 subprocess.Popen(["ollama", "serve"], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                 time.sleep(3)
                 print(f"  {Color.GREEN}✅ Neural Link Restored.{Color.END}")
             except:
                 print(f"  {Color.RED}❌ Failed to start brain service.{Color.END}")
                 return

        # 3. Check Models (Qwen + Llama)
        print(f"  {Color.BLUE}-> Verifying Cognitive Models (Multi-Model Adaptation)...{Color.END}")
        try:
            res = requests.get("http://localhost:11434/api/tags").json()
            installed = [m['name'].split(':')[0] for m in res.get('models', [])]
            
            # Priority Matrix (as requested by user)
            TARGET_MODELS = [
                "qwen2.5:7b",   # High balance (Speed/IQ)
                "llama3.1:8b",     # Standard Logic
            ]
            
            missing = [m for m in TARGET_MODELS if not any(existing in m for existing in installed)]
            
            if not installed and missing:
                # First time setup - Pull Qwen first (User Preference)
                model_to_pull = "qwen2.5:7b"
                print(f"  {Color.YELLOW}[EMPTY BRAIN] Downloading primary model: {model_to_pull}...{Color.END}")
                print(f"  {Color.YELLOW}   (This happens only once. Please wait...){Color.END}")
                # Stream pull
                process = subprocess.Popen(["ollama", "pull", model_to_pull], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False)
                while True:
                    line_bytes = process.stdout.readline()
                    if not line_bytes and process.poll() is not None: break
                    if line_bytes:
                        line = line_bytes.decode('utf-8', errors='replace').strip()
                        if "pulling" in line or "downloading" in line:
                             sys.stdout.write(f"\r     -> {line[:60]}...")
                             sys.stdout.flush()
                print(f"\n  {Color.GREEN}✅ Model {model_to_pull} ready.{Color.END}")
            
            elif installed:
                print(f"  {Color.GREEN}✅ Intelligences Available: {', '.join(installed)}{Color.END}")
                
        except Exception as e:
            print(f"  {Color.RED}❌ Model verification failed: {e}{Color.END}")

    def initialize_learning_systems(self):
        """
        Stage 2.7: Initialize Autonomous Learning Systems
        - Continual Learner (Auto-Training)
        - Feedback Loop (RLHF/DPO)
        - Knowledge Distiller (Golden Commands)
        - Dream Cycle (Nighttime Training)
        """
        self.step("Learning Systems: Initializing...", "WAIT")
        
        try:
            # Import and initialize
            from src.learning.learning_engine import initialize_learning_systems
            
            success = initialize_learning_systems(PROJECT_ROOT)
            
            if success:
                self.step("Learning Systems: ONLINE (AGI Mode Active)", "OK")
                print(f"  {Color.GREEN}  → Continual Learner: Monitoring{Color.END}")
                print(f"  {Color.GREEN}  → Feedback Loop: Collecting{Color.END}")
                print(f"  {Color.GREEN}  → Knowledge Distiller: Extracting Patterns{Color.END}")
                print(f"  {Color.GREEN}  → Dream Cycle: Scheduled{Color.END}")
            else:
                self.step("Learning Systems: HIBERNATING (Disabled in config)", "WARN")
                
        except Exception as e:
            self.step(f"Learning Systems: ERROR - {str(e)}", "WARN")
            self.logger.error(f"Failed to initialize learning systems: {e}")
        
        print("-" * 80)

    def launch_core(self):
        print("\n" + Color.CYAN + "="*80 + Color.END)
        print(f"{Color.BOLD}                       JARVIS SINGULARITY CORE ONLINE{Color.END}")
        print(f"{Color.CYAN}{'='*80}{Color.END}")
        print("     Multi-Threaded Neural Engine  -  Self-Healing Architecture")
        print(Color.CYAN + "="*80 + Color.END)
        
        print(f"\n  [RESOURCES] {Color.CYAN}Initializing system core...{Color.END}")
        
        try:
            # Prepare process command
            cmd = [str(VENV_PYTHON), str(MAIN_CORE)]
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                env=os.environ.copy()
            )
            
            self.logger.info(f"Main Core launched with PID: {process.pid}")
            print(f"\n{Color.GREEN}✅ SINGULARITY CORE ENGAGED.{Color.END}")
            print(f"Pulse: {Color.CYAN}STABLE{Color.END} | PID: {process.pid}")
            print(f"\n{Color.BLUE}Keep this window open to monitor logs and system health.{Color.END}")
            
            # Wait for process to end
            process.wait()
            
            if process.returncode != 0:
                self.logger.error(f"Core crashed with exit code {process.returncode}")
                print(f"\n{Color.RED}[CRITICAL] System crash detected - Exit Code {process.returncode}{Color.END}")
                sys.exit(process.returncode)
            
        except Exception as e:
            self.logger.fatal(f"Failed to launch core: {e}")
            print(f"\n{Color.RED}❌ FATAL ERROR: {e}{Color.END}")

    def check_active_instance(self):
        """Prevenção de instâncias duplicadas (Tratamento de conflito de hardware)"""
        lock_file = PROJECT_ROOT / "data" / "jarvis.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        if lock_file.exists():
            try:
                with open(lock_file, "r") as f:
                    old_pid = int(f.read().strip())
                
                if psutil.pid_exists(old_pid):
                    proc = psutil.Process(old_pid)
                    # Verificar se é realmente um processo python/jarvis
                    if "python" in proc.name().lower() or "cmd" in proc.name().lower():
                        print(f"\n{Color.RED}[!] INSTÂNCIA ATIVA DETECTADA (PID: {old_pid}){Color.END}")
                        print(f"    Sistemas de Câmera e Áudio podem estar em uso.")
                        
                        # Encerrar automaticamente para garantir o boot da nova
                        print(f"{Color.YELLOW}    -> Finalizando instância anterior para limpar recursos...{Color.END}")
                        proc.terminate()
                        proc.wait(timeout=5)
            except Exception: pass

        # Registrar novo PID
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

    def run(self):
        self.check_active_instance()
        self.print_header()
        
        # Stage -1: Post-Crash Diagnosis
        self.analyze_last_crash()
        
        # Stage 0
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 0] Infrastructure Synchronization{Color.END}")
        print("-" * 80)
        self.sync_infrastructure()
        
        # Stage 1
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 1] Environment Validation{Color.END}")
        print("-" * 80)
        if not self.validate_environment():
            sys.exit(1)

        # Stage 2
        self.check_ml_models()

        # Stage 2.5 (User Request: Auto-Brain)
        self.ensure_brain_capacity()
        
        # Stage 2.7 (SINGULARITY: Learning Systems Initialization)
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 2.7] Learning Systems Initialization{Color.END}")
        print("-" * 80)
        self.initialize_learning_systems()

        # Stage 3
        if not self.pre_flight_checks():
            sys.exit(1)
            
        # Launch
        self.launch_core()

if __name__ == "__main__":
    try:
        launcher = SingularityLauncher()
        launcher.run()
    except Exception as e:
        import traceback
        print(f"\n\033[91m[LAUNCHER CRITICAL] Unhandled Exception: {e}\033[0m")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
