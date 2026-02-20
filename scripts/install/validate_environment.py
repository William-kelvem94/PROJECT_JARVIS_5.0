#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Startup Validator and Dependency Checker
=====================================================
Validates environment and installs missing dependencies before starting JARVIS.

Author: JARVIS 5.0 Core Team
"""

import sys
import subprocess
import importlib
from pathlib import Path

# Required core dependencies (critical for operation)
REQUIRED_DEPENDENCIES = {
    "psutil": "psutil",
    "aiofiles": "aiofiles",
    "requests": "requests",
    "pydantic": "pydantic",
    "python-dotenv": "dotenv",
    "PyYAML": "yaml",
    "aiohttp": "aiohttp",
    "beautifulsoup4": "bs4",
    "lxml": "lxml",
    "sqlalchemy": "sqlalchemy",
    "tqdm": "tqdm",
    "numpy": "numpy",
    "pillow": "PIL",
    "pyttsx3": "pyttsx3",
}

# Optional dependencies (graceful degradation)
OPTIONAL_DEPENDENCIES = {
    "PyQt6": "PyQt6",
    "opencv-python-headless": "cv2",
    "SpeechRecognition": "speech_recognition",
    "transformers": "transformers",
    "torch": "torch",
}


def check_python_version():
    """Ensure Python version is compatible"""
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required, found {sys.version}")
        return False
    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    return True


def check_dependency(package_name, import_name):
    """Check if a dependency is installed"""
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def install_dependency(package_name):
    """Install a missing dependency"""
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--user", package_name, "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def create_required_directories():
    """Create all required data directories"""
    directories = [
        "data/database",
        "data/backups/auto",
        "data/learning",
        "data/events",
        "data/logs",
        "data/cache",
        "data/models",
        "config",
        "models",
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print("✅ All required directories created")


def validate_environment():
    """Validate the complete JARVIS environment"""
    print("🔍 JARVIS 5.0 - Environment Validation")
    print("=" * 60)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check required dependencies
    print("\n📦 Checking required dependencies...")
    missing_required = []
    for package_name, import_name in REQUIRED_DEPENDENCIES.items():
        if check_dependency(package_name, import_name):
            print(f"  ✅ {package_name}")
        else:
            print(f"  ❌ {package_name} (missing)")
            missing_required.append(package_name)

    # Install missing required dependencies
    if missing_required:
        print(f"\n🔧 Installing {len(missing_required)} missing dependencies...")
        for package_name in missing_required:
            if install_dependency(package_name):
                print(f"  ✅ Installed {package_name}")
            else:
                print(f"  ❌ Failed to install {package_name}")
                print(f"\nPlease install manually: pip install {package_name}")
                sys.exit(1)

    # Check optional dependencies
    print("\n📦 Checking optional dependencies...")
    missing_optional = []
    for package_name, import_name in OPTIONAL_DEPENDENCIES.items():
        if check_dependency(package_name, import_name):
            print(f"  ✅ {package_name}")
        else:
            print(f"  ⚠️  {package_name} (optional, not installed)")
            missing_optional.append(package_name)

    if missing_optional:
        print(f"\n⚠️  {len(missing_optional)} optional dependencies missing")
        print("   These are not required but enable additional features:")
        for pkg in missing_optional:
            print(f"   - {pkg}")
        print(f"\n   Install with: pip install {' '.join(missing_optional)}")

    # Create directories
    print("\n📁 Creating required directories...")
    create_required_directories()

    # Final validation
    print("\n" + "=" * 60)
    print("✅ Environment validation complete!")
    print("\n🚀 Starting JARVIS 5.0...")
    return True


if __name__ == "__main__":
    try:
        if validate_environment():
            # Environment is ready
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        sys.exit(1)
