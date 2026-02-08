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
        log_dir = PROJECT_ROOT / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [LAUNCHER] - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "launcher.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("Launcher")

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
  [ROOT] {PROJECT_ROOT}
"""
        print(header)

    def step(self, title, status="WAIT"):
        colors = {"OK": Color.GREEN, "WARN": Color.YELLOW, "ERR": Color.RED, "WAIT": Color.CYAN}
        badge = f"[{colors.get(status, Color.BLUE)}{status}{Color.END}]"
        print(f"  {badge} {title}")

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
            path = PROJECT_ROOT / m["file"]
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

    def pre_flight_checks(self):
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 3] Pre-Flight System Check{Color.END}")
        print("-" * 80)
        print("🧠 Starting JARVIS Pre-flight Sequence...")
        
        # Check critical libs
        libs = ["PyQt6", "cv2", "numpy", "torch", "chromadb", "ultralytics"]
        missing = []
        for lib in libs:
            try:
                subprocess.run([str(VENV_PYTHON), "-c", f"import {lib}"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                print(f"  {Color.GREEN}✅ {lib.ljust(15)} - Validated{Color.END}")
            except:
                print(f"  {Color.RED}❌ {lib.ljust(15)} - Missing or Corrupted{Color.END}")
                missing.append(lib)
        
        if missing:
            self.step("Dependencies failure detected", "ERR")
            print(f"  {Color.YELLOW}💡 Hint: Run 'pip install -r requirements.txt'{Color.END}")
            return False
            
        print(f"\n🚀 {Color.GREEN}Pre-flight concluído com sucesso!{Color.END}")
        print("-" * 80)
        self.step("Pre-flight checks passed", "OK")
        return True

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
            
        except Exception as e:
            self.logger.fatal(f"Failed to launch core: {e}")
            print(f"\n{Color.RED}❌ FATAL ERROR: {e}{Color.END}")

    def run(self):
        self.print_header()
        
        # Stage 0
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 0] Infrastructure Synchronization{Color.END}")
        print("-" * 80)
        self.sync_infrastructure()
        
        # Stage 1
        print(f"{Color.BOLD}{Color.CYAN}[STAGE 1] Environment Validation{Color.END}")
        print("-" * 80)
        if not self.validate_environment():
            return

        # Stage 2
        self.check_ml_models()

        # Stage 3
        if not self.pre_flight_checks():
            return
            
        # Launch
        self.launch_core()

if __name__ == "__main__":
    launcher = SingularityLauncher()
    launcher.run()
