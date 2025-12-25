#!/usr/bin/env python3
"""
Script de instalacao simples para JARVIS 5.0
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Verifica se a versao do Python e compativel"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERRO: Python 3.8 ou superior e necessario")
        print(f"   Versao atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def install_requirements():
    """Instala dependencias do requirements.txt"""
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("ERRO: Arquivo requirements.txt nao encontrado")
        return False
    
    print("Instalando dependencias...")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Dependencias instaladas com sucesso")
            return True
        else:
            print("ERRO ao instalar dependencias:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERRO ao instalar dependencias: {e}")
        return False


def test_installation():
    """Testa a instalacao"""
    print("Testando instalacao...")
    
    try:
        # Tentar importar JARVIS
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from jarvis import JarvisAssistant
        
        # Tentar criar assistente
        assistant = JarvisAssistant()
        
        # Testar sistemas
        results = assistant.test_systems()
        
        if results.get('overall', False):
            print("Teste de instalacao - SUCESSO")
            return True
        else:
            print("Teste de instalacao - PROBLEMAS DETECTADOS")
            print("   Microfone:", "OK" if results.get('microphone') else "ERRO")
            print("   Voz:", "OK" if results.get('speech') else "ERRO")
            print("   Config:", "OK" if results.get('config') else "ERRO")
            return False
            
    except Exception as e:
        print(f"ERRO no teste de instalacao: {e}")
        return False


def main():
    """Funcao principal de instalacao"""
    print("JARVIS 5.0 - Script de Instalacao Simples")
    print("=" * 50)
    
    # Mostrar informacoes do sistema
    print("Informacoes do Sistema:")
    print(f"   OS: {platform.system()} {platform.version()}")
    print(f"   Python: {sys.version}")
    print()
    
    # Verificacoes
    checks = [
        ("Versao do Python", check_python_version),
        ("Dependencias", install_requirements),
    ]
    
    # Executar verificacoes
    results = []
    for name, check_func in checks:
        print(f"Verificando {name}...")
        result = check_func()
        results.append((name, result))
        print()
    
    # Testar instalacao
    test_result = test_installation()
    results.append(("Teste Final", test_result))
    
    # Mostrar resumo
    print()
    print("Resumo da Instalacao:")
    print("-" * 30)
    
    all_ok = True
    for name, result in results:
        status = "OK" if result else "ERRO"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    print("-" * 30)
    
    if all_ok:
        print("INSTALACAO CONCLUIDA COM SUCESSO!")
        print()
        print("Para usar o JARVIS:")
        print("  python main.py")
        print()
        print("Para ver opcoes:")
        print("  python main.py --help")
        print()
        print("Para testar:")
        print("  python main.py --test")
    else:
        print("INSTALACAO CONCLUIDA COM PROBLEMAS")
        print()
        print("Alguns componentes podem nao funcionar corretamente.")
        print("Verifique os erros acima e tente resolver os problemas.")
    
    return all_ok


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nInstalacao cancelada pelo usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado durante instalacao: {e}")
        sys.exit(1)
