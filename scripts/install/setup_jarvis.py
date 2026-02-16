#!/usr/bin/env python3
"""
JARVIS 5.0 Setup Script
Comprehensive installation and validation for a fully functional system.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    """Terminal colors for better output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def check_python_version():
    """Ensure Python 3.10+"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True

def create_directories():
    """Create all required data directories"""
    print_header("Creating Directory Structure")
    
    directories = [
        "data/database",
        "data/backups/auto",
        "data/learning",
        "data/events",
        "data/logs",
        "data/cache",
        "data/memory",
        "src/plugins/auto_generated",
        "config",
        "models"
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {dir_path}")
        else:
            print_info(f"Exists: {dir_path}")
    
    return True

def install_dependencies():
    """Install all required Python packages"""
    print_header("Installing Dependencies")
    
    # Core dependencies (required)
    core_deps = [
        "psutil",
        "aiofiles",
        "requests",
        "pydantic",
        "python-dotenv",
        "PyYAML",
        "aiohttp",
        "beautifulsoup4",
        "lxml",
        "sqlalchemy",
        "tqdm"
    ]
    
    # Audio dependencies
    audio_deps = [
        "pyttsx3",
        "SpeechRecognition",
        "pyaudio"  # May fail on some systems
    ]
    
    # Vision dependencies
    vision_deps = [
        "numpy",
        "pillow",
        "opencv-python-headless"
    ]
    
    # Optional dependencies
    optional_deps = [
        "PyQt6",  # GUI features
        "chromadb",  # Vector database
        "sentence-transformers"  # Embeddings
    ]
    
    def install_package(package):
        """Install a single package"""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            return False
    
    # Install core dependencies
    print_info("Installing core dependencies...")
    for dep in core_deps:
        if install_package(dep):
            print_success(f"Installed: {dep}")
        else:
            print_error(f"Failed: {dep}")
            return False
    
    # Install audio dependencies (best effort)
    print_info("\nInstalling audio dependencies...")
    for dep in audio_deps:
        if install_package(dep):
            print_success(f"Installed: {dep}")
        else:
            print_warning(f"Skipped: {dep} (may require system libraries)")
    
    # Install vision dependencies
    print_info("\nInstalling vision dependencies...")
    for dep in vision_deps:
        if install_package(dep):
            print_success(f"Installed: {dep}")
        else:
            print_warning(f"Failed: {dep}")
    
    # Install optional dependencies (best effort)
    print_info("\nInstalling optional dependencies...")
    for dep in optional_deps:
        if install_package(dep):
            print_success(f"Installed: {dep}")
        else:
            print_warning(f"Skipped: {dep} (optional)")
    
    return True

def check_ollama():
    """Check if Ollama is installed and running"""
    print_header("Checking Ollama")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print_success("Ollama is running ✓")
            models = response.json().get("models", [])
            if models:
                print_info(f"Available models: {', '.join([m['name'] for m in models[:3]])}")
            return True
        else:
            print_warning("Ollama responded but may not be configured correctly")
            return False
    except Exception as e:
        print_warning("Ollama not detected (optional for basic operation)")
        print_info("Install Ollama from: https://ollama.ai")
        print_info("Self-healing features require Ollama")
        return False

def validate_imports():
    """Validate that critical modules can be imported"""
    print_header("Validating Imports")
    
    # Test via subprocess to avoid cache issues
    test_script = """
import sys
critical_modules = ['psutil', 'aiofiles', 'requests', 'pydantic', 'yaml', 'aiohttp', 'sqlalchemy']
failed = []
for module in critical_modules:
    try:
        __import__(module)
    except ImportError:
        failed.append(module)
if failed:
    print(','.join(failed))
    sys.exit(1)
else:
    print('ALL_OK')
    sys.exit(0)
"""
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and 'ALL_OK' in result.stdout:
            print_success("All critical imports validated ✓")
            return True
        else:
            failed_modules = result.stdout.strip().split(',')
            for module in failed_modules:
                if module:
                    print_error(f"Import FAILED: {module}")
            return False
    except Exception as e:
        print_warning(f"Import validation had issues: {e}")
        # Try direct import as fallback
        try:
            import psutil, aiofiles, requests, pydantic, yaml, aiohttp, sqlalchemy
            print_success("Imports OK (via fallback test)")
            return True
        except ImportError as ie:
            print_error(f"Import error: {ie}")
            return False

def test_basic_functionality():
    """Test basic system components"""
    print_header("Testing Basic Functionality")
    
    # Test 1: Can we import JARVIS modules?
    try:
        sys.path.insert(0, str(Path.cwd()))
        from src.utils.platform_compat import IS_WINDOWS, IS_LINUX, IS_MAC
        print_success(f"Platform detection: Windows={IS_WINDOWS}, Linux={IS_LINUX}, Mac={IS_MAC}")
    except Exception as e:
        print_error(f"Failed to import platform_compat: {e}")
        return False
    
    # Test 2: Can we create database directory?
    try:
        db_path = Path("data/learning/knowledge.db")
        if not db_path.parent.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
        print_success("Database directory accessible")
    except Exception as e:
        print_error(f"Cannot access database directory: {e}")
        return False
    
    # Test 3: Can we write to logs?
    try:
        log_path = Path("data/logs/setup.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as f:
            f.write("Setup test\n")
        print_success("Log directory writable")
    except Exception as e:
        print_error(f"Cannot write to logs: {e}")
        return False
    
    return True

def create_startup_script():
    """Create easy startup scripts"""
    print_header("Creating Startup Scripts")
    
    # Unix/Linux/Mac startup script
    unix_script = """#!/bin/bash
# JARVIS 5.0 Startup Script

echo "Starting JARVIS 5.0..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check dependencies
python3 scripts/install/setup_jarvis.py --quick-check

# Start JARVIS
python3 main.py "$@"
"""
    
    # Windows startup script
    windows_script = """@echo off
REM JARVIS 5.0 Startup Script

echo Starting JARVIS 5.0...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

REM Check dependencies
python scripts/install/setup_jarvis.py --quick-check

REM Start JARVIS
python main.py %*
"""
    
    # Write Unix script
    with open("start_jarvis.sh", "w") as f:
        f.write(unix_script)
    os.chmod("start_jarvis.sh", 0o755)
    print_success("Created: start_jarvis.sh")
    
    # Write Windows script
    with open("start_jarvis.bat", "w") as f:
        f.write(windows_script)
    print_success("Created: start_jarvis.bat")
    
    return True

def main():
    """Main setup routine"""
    print(f"""
{Colors.BOLD}{Colors.HEADER}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  JARVIS 5.0 Setup Wizard                  ║
║                                                           ║
║          Making Your AI Assistant Production-Ready        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """)
    
    # Quick check mode
    if "--quick-check" in sys.argv:
        if not validate_imports():
            sys.exit(1)
        sys.exit(0)
    
    steps = [
        ("Python Version", check_python_version),
        ("Directory Structure", create_directories),
        ("Dependencies", install_dependencies),
        ("Ollama (Optional)", check_ollama),
        ("Import Validation", validate_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Startup Scripts", create_startup_script)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print_error(f"Step '{step_name}' failed: {e}")
            results.append((step_name, False))
    
    # Summary
    print_header("Setup Summary")
    
    success_count = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        if result:
            print_success(f"{step_name}: OK")
        else:
            print_warning(f"{step_name}: PARTIAL or SKIPPED")
    
    print(f"\n{Colors.BOLD}Status: {success_count}/{total} steps completed{Colors.ENDC}\n")
    
    if success_count >= 6:  # At least 6 out of 7 (Ollama is optional)
        print_success("✓ JARVIS 5.0 is ready!")
        print_info("\nTo start JARVIS:")
        print_info("  Unix/Linux/Mac: ./start_jarvis.sh")
        print_info("  Windows: start_jarvis.bat")
        print_info("  Or directly: python3 main.py")
        return 0
    else:
        print_error("✗ Setup incomplete. Please fix errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
