#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Quick Setup Checker
Verifica rapidamente se o sistema esta pronto para executar
"""

import sys
import subprocess
from pathlib import Path

# Colors
class C:
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    INFO = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_python():
    """Verifica Python"""
    print("\n[1] Verificando Python...")
    
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    if sys.version_info >= (3, 10):
        print(f"   {C.OK}[OK]{C.END} Python {version} instalado")
        return True
    else:
        print(f"   {C.FAIL}[FALHOU]{C.END} Python {version} muito antigo (minimo: 3.10)")
        return False

def check_venv():
    """Verifica ambiente virtual"""
    print("\n[2] Verificando ambiente virtual...")
    
    venv_path = Path("venv")
    
    if venv_path.exists() and (venv_path / "bin" / "python").exists():
        print(f"   {C.OK}[OK]{C.END} Ambiente virtual encontrado (Unix)")
        return True
    elif venv_path.exists() and (venv_path / "Scripts" / "python.exe").exists():
        print(f"   {C.OK}[OK]{C.END} Ambiente virtual encontrado (Windows)")
        return True
    else:
        print(f"   {C.WARN}[AVISO]{C.END} Ambiente virtual nao encontrado")
        print(f"   Solucao: Execute JARVIS_SINGULARITY.bat ou python -m venv venv")
        return False

def check_critical_files():
    """Verifica arquivos criticos"""
    print("\n[3] Verificando arquivos criticos...")
    
    files = [
        ("main_singularity.py", True),
        ("main.py", False),
        ("config.yaml", True),
        ("requirements_singularity.txt", True),
        ("setup_manager.py", True),
    ]
    
    all_ok = True
    found_main = False
    
    for filename, required in files:
        if Path(filename).exists():
            if "main" in filename:
                found_main = True
        elif required and "main" not in filename:
            print(f"   {C.FAIL}[FALHOU]{C.END} {filename} nao encontrado")
            all_ok = False
    
    if not found_main:
        print(f"   {C.FAIL}[FALHOU]{C.END} Entry point nao encontrado (main.py ou main_singularity.py)")
        all_ok = False
    
    if all_ok:
        print(f"   {C.OK}[OK]{C.END} Todos os arquivos criticos presentes")
    
    return all_ok

def check_structure():
    """Verifica estrutura de pastas"""
    print("\n[4] Verificando estrutura de pastas...")
    
    dirs = [
        "src/core",
        "src/interface",
        "src/database",
        "data",
    ]
    
    all_ok = True
    
    for dir_path in dirs:
        if not Path(dir_path).exists():
            print(f"   {C.FAIL}[FALHOU]{C.END} {dir_path} nao encontrado")
            all_ok = False
    
    if all_ok:
        print(f"   {C.OK}[OK]{C.END} Estrutura de pastas OK")
    
    return all_ok

def run_validator():
    """Executa validador completo"""
    print("\n[5] Executando validador completo...")
    
    if not Path("validate_project.py").exists():
        print(f"   {C.WARN}[AVISO]{C.END} validate_project.py nao encontrado")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, "validate_project.py"],
            capture_output=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"   {C.OK}[OK]{C.END} Validacao completa passou")
            return True
        elif result.returncode == 1:
            print(f"   {C.WARN}[AVISO]{C.END} Validacao parcial (execute: python validate_project.py)")
            return True
        else:
            print(f"   {C.FAIL}[FALHOU]{C.END} Validacao completa falhou")
            return False
    except subprocess.TimeoutExpired:
        print(f"   {C.WARN}[AVISO]{C.END} Validador excedeu timeout")
        return True
    except Exception as e:
        print(f"   {C.WARN}[AVISO]{C.END} Erro ao executar validador: {e}")
        return True

def main():
    """Funcao principal"""
    print(f"\n{C.BOLD}{'='*70}")
    print("  JARVIS - VERIFICADOR RAPIDO DE SETUP")
    print(f"{'='*70}{C.END}\n")
    
    # Executar checks
    checks = [
        check_python(),
        check_venv(),
        check_critical_files(),
        check_structure(),
        run_validator(),
    ]
    
    # Resultado
    all_ok = all(checks)
    
    print(f"\n{C.BOLD}{'='*70}")
    
    if all_ok:
        print(f"{C.OK}  RESULTADO: SISTEMA PRONTO PARA EXECUCAO{C.END}")
        print(f"{C.BOLD}{'='*70}{C.END}\n")
        print("  Para iniciar o JARVIS:")
        print("  1. Windows: Execute JARVIS_SINGULARITY.bat")
        print("  2. Manual: python main.py")
        print("  3. Validar: python validate_project.py")
    else:
        print(f"{C.WARN}  RESULTADO: SISTEMA PRECISA DE CONFIGURACAO{C.END}")
        print(f"{C.BOLD}{'='*70}{C.END}\n")
        print("  Problemas detectados. Solucoes:")
        print("  1. Windows: Execute JARVIS_SINGULARITY.bat (auto-config)")
        print("  2. Manual: python setup_manager.py")
        print("  3. Diagnostico: python validate_project.py")
        print("  4. Ajuda: Veja TROUBLESHOOTING.md")
    
    print()
    return 0 if all_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{C.WARN}Verificacao interrompida{C.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{C.FAIL}Erro: {e}{C.END}")
        sys.exit(1)
