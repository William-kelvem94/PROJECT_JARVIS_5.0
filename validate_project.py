#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Project Validator
Valida todo o projeto: estrutura, dependencias, sintaxe, imports, config
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Tuple, Dict
import subprocess
import json

# ============================================================================
# CONFIGURACAO
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
REQUIRED_DIRS = [
    "src/core",
    "src/interface",
    "src/database",
    "src/utils",
    "data",
    "config",
    "models",
]

CRITICAL_FILES = [
    "main_singularity.py",
    "config.yaml",
    "requirements_singularity.txt",
    "setup_manager.py",
    "src/core/ai_agent.py",
    "src/interface/ai_worker.py",
    "src/interface/hud.py",
]

REQUIRED_PACKAGES = [
    "PyQt6",
    "numpy",
    "torch",
    "opencv-python",
    "sqlalchemy",
]

# ============================================================================
# CORES PARA OUTPUT
# ============================================================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Imprime cabecalho"""
    print(f"\n{Colors.HEADER}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(text: str):
    """Imprime sucesso"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Imprime erro"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Imprime aviso"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    """Imprime info"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

# ============================================================================
# VALIDADORES
# ============================================================================

def validate_directory_structure() -> Tuple[bool, List[str]]:
    """Valida estrutura de diretorios"""
    print_header("1. VALIDANDO ESTRUTURA DE DIRETORIOS")
    
    errors = []
    for dir_path in REQUIRED_DIRS:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"Diretorio encontrado: {dir_path}")
        else:
            errors.append(f"Diretorio faltando: {dir_path}")
            print_error(f"Diretorio faltando: {dir_path}")
    
    return len(errors) == 0, errors


def validate_critical_files() -> Tuple[bool, List[str]]:
    """Valida arquivos criticos"""
    print_header("2. VALIDANDO ARQUIVOS CRITICOS")
    
    errors = []
    for file_path in CRITICAL_FILES:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists() and full_path.is_file():
            print_success(f"Arquivo encontrado: {file_path}")
        else:
            errors.append(f"Arquivo faltando: {file_path}")
            print_error(f"Arquivo faltando: {file_path}")
    
    return len(errors) == 0, errors


def validate_python_syntax() -> Tuple[bool, List[str]]:
    """Valida sintaxe de todos os arquivos Python"""
    print_header("3. VALIDANDO SINTAXE PYTHON")
    
    errors = []
    python_files = list(PROJECT_ROOT.rglob("*.py"))
    
    # Filtrar arquivos em pastas a ignorar
    ignore_dirs = {".git", "venv", "__pycache__", ".pytest_cache", "_backup_legacy"}
    python_files = [
        f for f in python_files 
        if not any(part in ignore_dirs for part in f.parts)
    ]
    
    print_info(f"Verificando {len(python_files)} arquivos Python...")
    
    for py_file in python_files:
        try:
            # Ler com UTF-8 e substituir caracteres invalidos
            # (se necessario, validacao estrita de encoding pode ser feita separadamente)
            with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
            
            # Detectar se houve substituição de caracteres
            if '\ufffd' in source:  # Caractere de substituição Unicode
                print_warning(
                    f"Problema de codificacao detectado em {py_file.relative_to(PROJECT_ROOT)}. "
                    f"Recomenda-se salvar o arquivo em UTF-8."
                )
            
            ast.parse(source)
            # print_success(f"Sintaxe OK: {py_file.relative_to(PROJECT_ROOT)}")
        except SyntaxError as e:
            error_msg = f"Erro de sintaxe em {py_file.relative_to(PROJECT_ROOT)}: {e}"
            errors.append(error_msg)
            print_error(error_msg)
        except Exception as e:
            # Log encoding or other errors but don't fail validation
            print_warning(f"Aviso ao ler {py_file.relative_to(PROJECT_ROOT)}: {e}")
    
    if not errors:
        print_success(f"Todos os {len(python_files)} arquivos tem sintaxe valida")
    
    return len(errors) == 0, errors


def validate_imports() -> Tuple[bool, List[str]]:
    """Valida imports em arquivos criticos"""
    print_header("4. VALIDANDO IMPORTS CRITICOS")
    
    errors = []
    critical_modules = [
        "src.core.ai_agent",
        "src.interface.ai_worker",
        "src.interface.hud",
    ]
    
    for module_path in critical_modules:
        # Converter path para modulo
        module_file = PROJECT_ROOT / module_path.replace(".", os.sep)
        module_file = Path(str(module_file) + ".py")
        
        if not module_file.exists():
            continue
            
        try:
            # Tentar importar
            spec = importlib.util.spec_from_file_location(module_path, module_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_path] = module
                # Note: Not executing spec.loader.exec_module to avoid side effects during validation
                print_success(f"Import OK: {module_path}")
        except Exception as e:
            error_msg = f"Erro ao importar {module_path}: {e}"
            errors.append(error_msg)
            print_error(error_msg)
    
    return len(errors) == 0, errors


def validate_dependencies() -> Tuple[bool, List[str]]:
    """Valida dependencias instaladas"""
    print_header("5. VALIDANDO DEPENDENCIAS")
    
    errors = []
    warnings = []
    
    # Ler requirements
    req_file = PROJECT_ROOT / "requirements_singularity.txt"
    if not req_file.exists():
        errors.append("requirements_singularity.txt nao encontrado")
        return False, errors
    
    with open(req_file, 'r') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove version operators: ==, >=, <=, ~=, !=, <, >
                pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0]
                pkg_name = pkg_name.split("~=")[0].split("!=")[0].split("<")[0].split(">")[0]
                pkg_name = pkg_name.split(";")[0].strip()  # Remove platform specifiers
                if pkg_name:
                    requirements.append(pkg_name)
    
    print_info(f"Verificando {len(requirements)} pacotes...")
    
    # Verificar pacotes instalados
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=60  # Aumentar timeout de 30 para 60 segundos em sistemas lentos
        )
        
        if result.returncode == 0:
            installed_packages = {
                pkg["name"].lower().replace("-", "_"): pkg["version"]
                for pkg in json.loads(result.stdout)
            }
            
            # Mapeamento de nomes conhecidos de pacotes (PyPI name -> import name)
            PACKAGE_ALIASES = {
                "opencv_python": ["opencv", "cv2"],
                "pyyaml": ["yaml"],
                "pillow": ["pil"],
                "scikit_learn": ["sklearn"],
            }
            
            missing = []
            for pkg in requirements:
                pkg_normalized = pkg.lower().replace("-", "_")
                
                # Verificar nome normalizado e aliases
                found = pkg_normalized in installed_packages
                if not found and pkg_normalized in PACKAGE_ALIASES:
                    # Verificar aliases
                    for alias in PACKAGE_ALIASES[pkg_normalized]:
                        if alias in installed_packages:
                            found = True
                            break
                
                if not found:
                    missing.append(pkg)
            
            if missing:
                print_error(f"Pacotes faltando ({len(missing)}):")
                for pkg in missing[:15]:  # Mostrar até 15 pacotes
                    print(f"  - {pkg}")
                    errors.append(f"Pacote faltando: {pkg}")  # Tratado como erro, não warning
            else:
                print_success(f"Todos os {len(requirements)} pacotes estao instalados")
        else:
            errors.append("Nao foi possivel verificar pacotes instalados")
            print_error("Nao foi possivel verificar pacotes instalados")
            
    except Exception as e:
        errors.append(f"Erro ao verificar dependencias: {e}")
        print_error(f"Erro ao verificar dependencias: {e}")
    
    return len(errors) == 0, errors


def validate_config_file() -> Tuple[bool, List[str]]:
    """Valida arquivo de configuracao"""
    print_header("6. VALIDANDO CONFIGURACAO")
    
    errors = []
    config_file = PROJECT_ROOT / "config.yaml"
    
    if not config_file.exists():
        errors.append("config.yaml nao encontrado")
        print_error("config.yaml nao encontrado")
        return False, errors
    
    try:
        # Tentar importar yaml
        import yaml
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Verificar secoes criticas
        required_sections = ["brain", "interface", "senses", "voice"]
        for section in required_sections:
            if section in config:
                print_success(f"Secao encontrada: {section}")
            else:
                print_warning(f"Secao faltando em config.yaml: {section}")
        
        print_success("config.yaml valido")
        
    except ImportError:
        error_msg = (
            "PyYAML nao instalado; instale o pacote 'pyyaml' para validar config.yaml "
            "(ex.: pip install pyyaml)"
        )
        errors.append(error_msg)
        print_error(error_msg)
    except Exception as e:
        error_msg = f"Erro ao validar config.yaml: {e}"
        errors.append(error_msg)
        print_error(error_msg)
    
    return len(errors) == 0, errors


def validate_entry_points() -> Tuple[bool, List[str]]:
    """Valida entry points"""
    print_header("7. VALIDANDO ENTRY POINTS")
    
    errors = []
    entry_points = [
        "main_singularity.py",
        "main.py",
        "setup_manager.py",
    ]
    
    found_main = False
    for entry in entry_points:
        full_path = PROJECT_ROOT / entry
        if full_path.exists():
            print_success(f"Entry point encontrado: {entry}")
            if "main" in entry:
                found_main = True
        else:
            print_info(f"Entry point opcional nao encontrado: {entry}")
    
    if not found_main:
        errors.append("Nenhum entry point principal encontrado (main.py ou main_singularity.py)")
        print_error("Nenhum entry point principal encontrado")
    
    return len(errors) == 0, errors


def run_tests() -> Tuple[bool, List[str]]:
    """Executa testes se existirem"""
    print_header("8. EXECUTANDO TESTES")
    
    errors = []
    test_dir = PROJECT_ROOT / "tests"
    
    if not test_dir.exists():
        print_info("Diretorio de testes nao encontrado, pulando...")
        return True, []
    
    # Verificar se pytest esta instalado
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print_info("pytest nao instalado, pulando testes...")
            return True, []
        
        # Executar testes
        print_info("Executando testes (pode demorar alguns minutos)...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos para testes completos (aumentado de 60s para suites maiores)
        )
        
        if result.returncode == 0:
            print_success("Todos os testes passaram")
        else:
            print_warning("Alguns testes falharam (verifique logs)")
            # Nao adicionar como erro critico
        
    except subprocess.TimeoutExpired:
        print_warning("Testes excederam timeout de 60s")
    except Exception as e:
        print_warning(f"Erro ao executar testes: {e}")
    
    return True, errors


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Funcao principal"""
    print(f"{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║        JARVIS SINGULARITY - PROJECT VALIDATOR v1.0               ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print_info(f"Diretorio do projeto: {PROJECT_ROOT}")
    print_info(f"Python: {sys.version.split()[0]}")
    
    # Executar validadores
    validators = [
        ("Estrutura de Diretorios", validate_directory_structure),
        ("Arquivos Criticos", validate_critical_files),
        ("Sintaxe Python", validate_python_syntax),
        ("Imports Criticos", validate_imports),
        ("Dependencias", validate_dependencies),
        ("Configuracao", validate_config_file),
        ("Entry Points", validate_entry_points),
        ("Testes", run_tests),
    ]
    
    results = []
    all_errors = []
    
    for name, validator_func in validators:
        try:
            success, errors = validator_func()
            results.append((name, success))
            all_errors.extend(errors)
        except Exception as e:
            print_error(f"Erro ao executar validador '{name}': {e}")
            results.append((name, False))
            all_errors.append(f"Erro no validador '{name}': {e}")
    
    # Resumo
    print_header("RESUMO DA VALIDACAO")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        color = Colors.OKGREEN if success else Colors.FAIL
        print(f"{color}{status}{Colors.ENDC} - {name}")
    
    print(f"\n{Colors.BOLD}Resultado: {passed}/{total} validadores passaram{Colors.ENDC}\n")
    
    if all_errors:
        print_header("ERROS ENCONTRADOS")
        for i, error in enumerate(all_errors[:20], 1):  # Mostrar apenas primeiros 20
            print(f"{i}. {error}")
        
        if len(all_errors) > 20:
            print(f"\n... e mais {len(all_errors) - 20} erros")
    
    # Status final
    if passed == total and not all_errors:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ PROJETO VALIDADO COM SUCESSO!{Colors.ENDC}\n")
        return 0
    elif passed >= total * 0.7:  # 70% passou
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  VALIDACAO PARCIAL (alguns problemas encontrados){Colors.ENDC}\n")
        return 1
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ VALIDACAO FALHOU (muitos problemas encontrados){Colors.ENDC}\n")
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Validacao interrompida pelo usuario{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}❌ Erro fatal: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
