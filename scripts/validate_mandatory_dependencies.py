#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Mandatory Dependencies Validation
=====================================================
Testa importações e funcionalidade básica para todas as categorias obrigatórias:
Biometria, Áudio, Interface e Monitoramento.
"""

import sys
import os
import importlib
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Testa importação de todos os pacotes obrigatórios"""
    mandatory_packages = {
        "Biometria": ["face_recognition", "dlib", "cv2"],
        "Áudio": ["pyaudio", "librosa", "soundfile"],
        "Interface": ["tkinter", "tkinter_tooltip", "PyQt6"],
        "Monitoramento": ["psutil", "wmi"]
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
        detector = dlib.get_frontal_face_detector()
        print(f"🔐 Biometria: dlib face detector inicializado - ✅")
    except Exception as e:
        print(f"🔐 Biometria: FALHA na biometria - ❌ ({e})")

    # 4. Interface (tkinter_tooltip)
    try:
        import tkinter as tk
        from tkinter_tooltip import ToolTip
        root = tk.Tk()
        root.withdraw() # Não mostrar janela
        label = tk.Label(root, text="Test")
        tooltip = ToolTip(label, msg="Test Tooltip")
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