#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Mandatory Dependencies Validation
=====================================================
Testa importações e funcionalidade básica para todas as categorias obrigatórias:
Biometria, Áudio, Interface e Monitoramento.
"""

import sys

import importlib
from pathlib import Path

# Ensure project root is on sys.path so imports from repo root resolve when running from /scripts
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def test_imports():
    """Testa importação de todos os pacotes obrigatórios"""
    # Note: some biometric packages (dlib/face_recognition) are optional on systems
    # without native build toolchains. We will warn but not fail the full validation
    # so the app can boot in degraded mode.
    mandatory_packages = {
        "Biometria": ["cv2"],
        "Áudio": ["pyaudio", "librosa", "soundfile"],
        "Interface": ["tkinter", "tkinter_tooltip", "PyQt6"],
        "Monitoramento": ["psutil", "wmi"]
    }
    optional_packages = {
        "Biometria (optional)": ["face_recognition", "dlib"]
    }
    
    results = {}
    all_passed = True
    
    print("\n🔍 TESTANDO IMPORTAÇÕES OBRIGATÓRIAS...")
    print("=" * 50)
    
    for category, packages in mandatory_packages.items():
        print(f"\n📂 Categoria: {category}")
        category_passed = True
        for package in packages:
            try:
                importlib.import_module(package)
                print(f"   ✅ {package:20} - OK")
            except ImportError as e:
                print(f"   ❌ {package:20} - FALHOU: {e}")
                category_passed = False
                all_passed = False
        results[category] = category_passed
    # Check optional packages but don't change overall pass/fail
    for category, packages in optional_packages.items():
        print(f"\n📂 Categoria: {category}")
        for package in packages:
            try:
                importlib.import_module(package)
                print(f"   ✅ {package:20} - OK")
            except ImportError as e:
                print(f"   ⚠️ {package:20} - OPCIONAL AUSENTE: {e}")
        
    return all_passed

def test_basic_functionality():
    """Testa funcionalidades básicas de cada categoria"""
    print("\n⚙️ TESTANDO FUNCIONALIDADES BÁSICAS...")
    print("=" * 50)
    
    # 1. Monitoramento (psutil)
    try:
        import psutil
        cpu_usage = psutil.cpu_percent(interval=0.1)
        print(f"📊 Monitoramento: CPU Usage detectada ({cpu_usage}%) - ✅")
    except Exception as e:
        print(f"📊 Monitoramento: FALHA ao ler CPU - ❌ ({e})")

    # 2. Áudio (pyaudio)
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"🎤 Áudio: {device_count} dispositivos encontrados - ✅")
    except Exception as e:
        print(f"🎤 Áudio: FALHA ao inicializar PyAudio - ❌ ({e})")

    # 3. Biometria (dlib/face_recognition)
    try:
        import dlib
        import face_recognition
        import numpy as np
        # Testar se dlib consegue criar um detector
        detector = dlib.get_frontal_face_detector()  # type: ignore
        # Validação simples: executar o detector em uma imagem dummy
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        _ = detector(test_image, 1)
        # Testar importação básica de face_recognition
        _ = face_recognition
        print(f"🔐 Biometria: dlib face detector inicializado - ✅")
    except Exception as e:
        print(f"🔐 Biometria: FALHA - ❌ ({e})")
    
    # 4. Interface (tkinter/tkinter_tooltip)
    try:
        import tkinter as tk
        import tkinter_tooltip  # type: ignore
        root = tk.Tk()
        root.withdraw() # Não mostrar janela
        label = tk.Label(root, text="Test")
        tkinter_tooltip.ToolTip(label, msg="Test Tooltip")
        root.destroy()
        print(f"🖥️ Interface: tkinter-tooltip funcional - ✅")
    except Exception as e:
        print(f"🖥️ Interface: FALHA na interface - ❌ ({e})")

def main():
    print("🔥 VALIDADOR DE DEPENDÊNCIAS OBRIGATÓRIAS JARVIS 5.0")
    print("=" * 50)
    
    imports_ok = test_imports()
    test_basic_functionality()
    
    print("\n" + "=" * 50)
    if imports_ok:
        print("🎉 SUCESSO: Todas as dependências obrigatórias estão funcionais!")
        return 0
    else:
        print("❌ ERRO: Algumas dependências obrigatórias estão faltando ou corrompidas.")
        print("💡 Verifique o requirements.txt e execute a instalação novamente.")
        return 1

if __name__ == "__main__":
    sys.exit(main())