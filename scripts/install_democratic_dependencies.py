#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Instalador de Dependências Democráticas Obrigatórias
=============================================================
Instala dependências obrigatórias para funcionalidades democráticas avançadas.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_mandatory_dependencies():
    """Instala dependências obrigatórias para funcionalidades avançadas"""
    
    print("🔧 Instalando dependências democráticas obrigatórias...")
    
    requirements_file = Path(__file__).parent.parent / "scripts" / "install" / "requirements.txt"
    
    try:
        # Verificar se arquivo existe
        if not requirements_file.exists():
            print(f"❌ Arquivo não encontrado: {requirements_file}")
            return False
        
        # Instalar dependências
        print(f"📦 Instalando dependências obrigatórias de: {requirements_file}")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências obrigatórias sincronizadas!")
            print("\n📋 Recursos OBRIGATÓRIOS habilitados:")
            print("   🔐 Reconhecimento Facial (FaceID)")
            print("   🎤 Processamento de Voz Avançado")
            print("   🖥️ Monitoramento de Sistema (WMI/psutil)")
            print("   🖥️ Interface Aprimorada (Tooltips)")
            return True
        else:
            print("❌ Erro na instalação:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_mandatory_dependencies():
    """Verifica quais dependências obrigatórias estão disponíveis"""
    
    print("\n🔍 Verificando dependências obrigatórias...")
    
    checks = [
        ("face_recognition", "Reconhecimento facial"),
        ("dlib", "Processamento facial"),
        ("pyaudio", "Captura de áudio"),
        ("librosa", "Processamento de áudio"), 
        ("soundfile", "I/O de arquivos de áudio"),
        ("tkinter_tooltip", "Tooltips de interface"),
        ("wmi", "Informações do sistema Windows"),
        ("psutil", "Monitoramento de sistema")
    ]
    
    available = 0
    total = len(checks)
    
    for module, description in checks:
        try:
            __import__(module)
            print(f"   ✅ {description}")
            available += 1
        except ImportError:
            print(f"   ❌ {description} (OBRIGATÓRIA - FALTANDO)")
    
    print(f"\n📊 Status: {available}/{total} funcionalidades obrigatórias disponíveis")
    
    if available == total:
        print("🎉 Todas as funcionalidades obrigatórias estão disponíveis!")
        return True
    else:
        print("❌ Algumas dependências obrigatórias estão faltando!")
        print("💡 Execute este script novamente para tentar instalar")
        return False

if __name__ == "__main__":
    print("🔥 JARVIS - Instalador de Dependências Democráticas Obrigatórias")
    print("=" * 60)
    
    # Verificar dependências atuais
    all_available = check_mandatory_dependencies()
    
    if not all_available:
        print("\n" + "=" * 60)
        print("🔧 Instalando dependências obrigatórias faltantes...")
        success = install_mandatory_dependencies()
        if success:
            print("\n🔍 Verificação pós-instalação:")
            check_mandatory_dependencies()
        else:
            print("❌ Falha na instalação. Verifique os logs acima.")
            sys.exit(1)
    else:
        print("✅ Todas as dependências obrigatórias já estão instaladas!")
    
    print("\n🎯 Instalação concluída!")
    print("🚀 Execute START_JARVIS.bat para iniciar o sistema democrático")