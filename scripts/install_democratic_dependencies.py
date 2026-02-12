#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Instalador de Dependências Democráticas Opcionais
===========================================================
Instala dependências opcionais para funcionalidades democráticas avançadas.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_optional_dependencies():
    """Instala dependências opcionais para funcionalidades avançadas"""
    
    print("🔧 Instalando dependências democráticas opcionais...")
    
    requirements_file = Path(__file__).parent.parent / "requirements_democratic_optional.txt"
    
    try:
        # Verificar se arquivo existe
        if not requirements_file.exists():
            print(f"❌ Arquivo não encontrado: {requirements_file}")
            return False
        
        # Instalar dependências
        print(f"📦 Instalando de: {requirements_file}")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências opcionais instaladas com sucesso!")
            print("\n📋 Funcionalidades habilitadas:")
            print("   🔐 Reconhecimento facial avançado")
            print("   🎤 Reconhecimento vocal")
            print("   ☁️ Integração Google Drive API")
            print("   🖥️ Monitoramento avançado de sistema")
            return True
        else:
            print("❌ Erro na instalação:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_optional_dependencies():
    """Verifica quais dependências opcionais estão disponíveis"""
    
    print("\n🔍 Verificando dependências opcionais...")
    
    checks = [
        ("face_recognition", "Reconhecimento facial"),
        ("pyaudio", "Captura de áudio"),
        ("librosa", "Processamento de áudio"), 
        ("googleapiclient", "Google Drive API"),
        ("wmi", "Informações do sistema Windows"),
        ("tkinter", "Interface gráfica")
    ]
    
    available = 0
    total = len(checks)
    
    for module, description in checks:
        try:
            __import__(module)
            print(f"   ✅ {description}")
            available += 1
        except ImportError:
            print(f"   ❌ {description} (opcional)")
    
    print(f"\n📊 Status: {available}/{total} funcionalidades opcionais disponíveis")
    
    if available == total:
        print("🎉 Todas as funcionalidades opcionais estão disponíveis!")
    elif available > total // 2:
        print("✅ Maioria das funcionalidades disponíveis")
    else:
        print("⚠️ Muitas funcionalidades opcionais ausentes")
        print("💡 Execute este script para instalar")

if __name__ == "__main__":
    print("🔥 JARVIS - Instalador de Dependências Democráticas")
    print("=" * 60)
    
    # Verificar dependências atuais
    check_optional_dependencies()
    
    # Perguntar se quer instalar
    print("\n" + "=" * 60)
    while True:
        choice = input("Instalar dependências opcionais? (S/n): ").lower()
        if choice in ['s', 'sim', 'y', 'yes', '']:
            success = install_optional_dependencies()
            if success:
                print("\n🔍 Verificação pós-instalação:")
                check_optional_dependencies()
            break
        elif choice in ['n', 'nao', 'não', 'no']:
            print("⚠️ Algumas funcionalidades podem estar limitadas sem as dependências opcionais")
            break
        else:
            print("❓ Resposta inválida. Digite 'S' para sim ou 'N' para não.")
    
    print("\n🎯 Instalação concluída!")
    print("🚀 Execute START_JARVIS.bat para iniciar o sistema democrático")