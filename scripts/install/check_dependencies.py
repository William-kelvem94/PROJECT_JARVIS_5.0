#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Dependency Checker
Verifica o status de todas as dependências do sistema
"""

import sys
import platform
from pathlib import Path

def check_module(name, package_name=None):
    """Tenta importar um módulo e retorna o status"""
    if package_name is None:
        package_name = name
    
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version, None
    except ImportError as e:
        return False, None, f"ImportError: {str(e)}"
    except OSError as e:
        return False, None, f"OSError (DLL): {str(e)}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def main():
    print("=" * 70)
    print("🔍 JARVIS 5.0 - Dependency Status Check")
    print("=" * 70)
    print()
    
    # System Info
    print("📊 System Information:")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print()
    
    # Core Dependencies
    print("🔧 Core Dependencies:")
    core_deps = [
        ("PyQt5", "PyQt5"),
        ("numpy", "numpy"),
        ("cv2", "cv2"),
        ("PIL", "PIL"),
    ]
    
    for name, package in core_deps:
        status, version, error = check_module(name, package)
        if status:
            print(f"   ✅ {name:20} {version}")
        else:
            print(f"   ❌ {name:20} NOT AVAILABLE")
            if error and "DLL" in error:
                print(f"      ⚠️  DLL Error - Install Visual C++ Redistributable")
    
    print()
    
    # AI Dependencies
    print("🤖 AI/ML Dependencies (PyTorch-based):")
    ai_deps = [
        ("torch", "torch"),
        ("torchvision", "torchvision"),
        ("torchaudio", "torchaudio"),
        ("easyocr", "easyocr"),
        ("ultralytics", "ultralytics"),
        ("faster-whisper", "faster_whisper"),
        ("resemblyzer", "resemblyzer"),
    ]
    
    pytorch_issue = False
    for name, package in ai_deps:
        status, version, error = check_module(name, package)
        if status:
            print(f"   ✅ {name:20} {version}")
        else:
            print(f"   ❌ {name:20} NOT AVAILABLE")
            if error and "DLL" in error:
                pytorch_issue = True
                
    print()
    
    # Audio Dependencies
    print("🎤 Audio Dependencies:")
    audio_deps = [
        ("pyaudio", "pyaudio"),
        ("soundfile", "soundfile"),
        ("librosa", "librosa"),
    ]
    
    for name, package in audio_deps:
        status, version, error = check_module(name, package)
        if status:
            print(f"   ✅ {name:20} {version}")
        else:
            print(f"   ❌ {name:20} NOT AVAILABLE")
    
    print()
    
    # Vision Dependencies
    print("👁️  Vision Dependencies:")
    vision_deps = [
        ("face_recognition", "face_recognition"),
        ("mediapipe", "mediapipe"),
        ("mss", "mss"),
    ]
    
    for name, package in vision_deps:
        status, version, error = check_module(name, package)
        if status:
            print(f"   ✅ {name:20} {version}")
        else:
            print(f"   ❌ {name:20} NOT AVAILABLE")
    
    print()
    
    # Windows Integration
    if platform.system() == "Windows":
        print("🪟 Windows Integration:")
        windows_deps = [
            ("pywin32", "win32api"),
            ("pycaw", "pycaw"),
            ("wmi", "wmi"),
        ]
        
        for name, package in windows_deps:
            status, version, error = check_module(name, package)
            if status:
                print(f"   ✅ {name:20} {version}")
            else:
                print(f"   ❌ {name:20} NOT AVAILABLE")
        print()
    
    # Summary
    print("=" * 70)
    print("📋 Summary:")
    print()
    
    if pytorch_issue:
        print("❌ PyTorch DLL Error Detected!")
        print()
        print("🔧 Solution:")
        print("   1. Download Visual C++ Redistributable:")
        print("      https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("   2. Install and restart your computer")
        print("   3. Run this script again to verify")
        print()
        print("📝 Note: JARVIS will run in degraded mode without PyTorch.")
        print("   Core functionality (system control, audio, basic vision) works!")
    else:
        print("✅ No critical DLL errors detected!")
        print("   JARVIS should run with full AI capabilities.")
    
    print()
    print("=" * 70)
    print()
    print("For more info, see: FIX_PYTORCH.md")
    print()

if __name__ == "__main__":
    main()
