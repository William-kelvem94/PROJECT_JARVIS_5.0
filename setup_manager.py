#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Setup Manager
Organizador Inteligente e Instalador Automático
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
BACKUP_DIR = PROJECT_ROOT / "_backup_legacy"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements_singularity.txt"

# Arquivos considerados "legado" ou "lixo" para mover para backup
LEGACY_FILES = [
    "launcher.py",
    "start_jarvis.py",
    "Jarvis.bat",
    "setup.py",  # setup.py antigo
    "requirements.txt",  # requirements.txt antigo (não singularity)
]

# Pastas essenciais que devem existir
ESSENTIAL_DIRS = [
    "src/interface",
    "src/core",
    "data",
    "data/screenshots",
    "data/temp",
    "_backup_legacy",
]

# Pastas SAGRADAS que NUNCA devem ser tocadas
SACRED_DIRS = [
    "src",
    "data",
    "models",
    "config",
    ".git",
    "docs",
    "legacy",
]


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num, text):
    """Imprime passo numerado"""
    print(f"\n[{step_num}] {text}")


def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"  ✅ {text}")


def print_warning(text):
    """Imprime aviso"""
    print(f"  ⚠️  {text}")


def print_error(text):
    """Imprime erro"""
    print(f"  ❌ {text}")


def print_info(text):
    """Imprime informação"""
    print(f"  ℹ️  {text}")


# ============================================================================
# ETAPAS DE SETUP
# ============================================================================
def step_1_verify_structure():
    """Passo 1: Verificar e criar estrutura de pastas essenciais"""
    print_step(1, "Verificando estrutura de pastas...")
    
    created_count = 0
    for dir_path in ESSENTIAL_DIRS:
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Criado: {dir_path}")
            created_count += 1
        else:
            print_info(f"OK: {dir_path}")
    
    if created_count == 0:
        print_success("Estrutura de pastas completa!")
    else:
        print_success(f"Criadas {created_count} pastas faltantes")


def step_2_archive_legacy():
    """Passo 2: Mover arquivos legados para backup"""
    print_step(2, "Arquivando arquivos legados...")
    
    # Garantir que backup dir existe
    BACKUP_DIR.mkdir(exist_ok=True)
    
    moved_count = 0
    for filename in LEGACY_FILES:
        source = PROJECT_ROOT / filename
        
        if source.exists() and source.is_file():
            # Criar nome com timestamp para evitar sobrescrever
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_name = f"{source.stem}_{timestamp}{source.suffix}"
            dest = BACKUP_DIR / dest_name
            
            try:
                shutil.move(str(source), str(dest))
                print_success(f"Movido: {filename} → _backup_legacy/{dest_name}")
                moved_count += 1
            except Exception as e:
                print_error(f"Erro ao mover {filename}: {e}")
        else:
            print_info(f"Não encontrado (OK): {filename}")
    
    if moved_count == 0:
        print_success("Nenhum arquivo legado para arquivar")
    else:
        print_success(f"Arquivados {moved_count} arquivos legados")


def step_3_promote_main():
    """Passo 3: Promover main_singularity_v2.py para main.py"""
    print_step(3, "Promovendo entry point oficial...")
    
    source = PROJECT_ROOT / "main_singularity_v2.py"
    dest = PROJECT_ROOT / "main.py"
    
    if source.exists():
        # Se main.py já existe, fazer backup primeiro
        if dest.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"main_old_{timestamp}.py"
            backup_path = BACKUP_DIR / backup_name
            shutil.move(str(dest), str(backup_path))
            print_warning(f"main.py antigo movido para _backup_legacy/{backup_name}")
        
        # Renomear (mover) main_singularity_v2.py para main.py
        shutil.move(str(source), str(dest))
        print_success("main_singularity_v2.py → main.py (novo padrão oficial)")
    else:
        print_warning("main_singularity_v2.py não encontrado - pulando promoção")


def step_4_install_dependencies():
    """Passo 4: Instalar dependências com versões travadas"""
    print_step(4, "Instalando dependências (pode demorar alguns minutos)...")
    
    if not REQUIREMENTS_FILE.exists():
        print_error(f"Arquivo não encontrado: {REQUIREMENTS_FILE}")
        print_error("Não é possível instalar dependências!")
        return False
    
    print_info(f"Usando: {REQUIREMENTS_FILE.name}")
    
    # -------------------------------------------------------------------------
    # PASSO 4.1: DESINSTALAR NUMPY AGRESSIVAMENTE
    # -------------------------------------------------------------------------
    print_info("\n[4.1] Removendo NumPy existente (se houver)...")
    try:
        uninstall_cmd = [
            sys.executable,
            "-m",
            "pip",
            "uninstall",
            "numpy",
            "-y"
        ]
        
        print_info(f"Comando: {' '.join(uninstall_cmd)}")
        result = subprocess.run(
            uninstall_cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode == 0:
            print_success("NumPy removido com sucesso")
        else:
            print_info("NumPy não estava instalado (OK)")
    except Exception as e:
        print_warning(f"Erro ao desinstalar numpy: {e}")
        print_info("Continuando mesmo assim...")
    
    # -------------------------------------------------------------------------
    # PASSO 4.2: INSTALAR REQUIREMENTS COM FORCE-REINSTALL
    # -------------------------------------------------------------------------
    print_info("\n[4.2] Instalando dependências com versões travadas...")
    print_info("Forçando reinstalação para garantir versões corretas...")
    
    try:
        # Usar --force-reinstall para garantir que numpy 2.x seja removido
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "-r",
            str(REQUIREMENTS_FILE)
        ]
        
        print_info(f"Comando: {' '.join(cmd)}")
        print_info("Aguarde (pode demorar 5-10 minutos)...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode == 0:
            print_success("Dependências instaladas com sucesso!")
            
            # Verificar numpy version
            try:
                # Reimportar numpy para pegar versão atualizada
                import importlib
                if 'numpy' in sys.modules:
                    importlib.reload(sys.modules['numpy'])
                import numpy
                numpy_version = numpy.__version__
                if numpy_version.startswith("1."):
                    print_success(f"NumPy versão correta: {numpy_version}")
                else:
                    print_warning(f"NumPy versão: {numpy_version} (esperado: 1.x)")
                    print_warning("Execute novamente: pip install --force-reinstall numpy==1.26.4")
            except ImportError:
                print_warning("NumPy não pôde ser verificado")
            
            return True
        else:
            print_error("Erro durante instalação!")
            print_error(f"Código de saída: {result.returncode}")
            if result.stderr:
                print_error("Erros:")
                print(result.stderr[:500])  # Primeiros 500 chars
            return False
            
    except Exception as e:
        print_error(f"Exceção durante instalação: {e}")
        return False



def step_5_verify_critical_files():
    """Passo 5: Verificar arquivos críticos"""
    print_step(5, "Verificando arquivos críticos...")
    
    critical_files = [
        "src/core/ai_agent.py",
        "src/interface/ai_worker.py",
        "main.py",
        "requirements_singularity.txt",
    ]
    
    all_ok = True
    for filepath in critical_files:
        full_path = PROJECT_ROOT / filepath
        if full_path.exists():
            print_success(f"OK: {filepath}")
        else:
            print_error(f"FALTANDO: {filepath}")
            all_ok = False
    
    if all_ok:
        print_success("Todos os arquivos críticos presentes!")
    else:
        print_warning("Alguns arquivos críticos estão faltando")
    
    return all_ok


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Função principal"""
    print_header("JARVIS SINGULARITY - SETUP MANAGER")
    print(f"Diretório: {PROJECT_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    
    try:
        # Executar etapas
        step_1_verify_structure()
        step_2_archive_legacy()
        step_3_promote_main()
        
        # Instalação (pode falhar se pip tiver problemas)
        install_success = step_4_install_dependencies()
        
        # Verificação final
        files_ok = step_5_verify_critical_files()
        
        # Resumo final
        print_header("RESUMO")
        
        if install_success and files_ok:
            print_success("✅ Setup concluído com SUCESSO!")
            print_info("\nPróximos passos:")
            print_info("1. Configure GOOGLE_API_KEY: set GOOGLE_API_KEY=sua_chave")
            print_info("2. Execute: python main.py")
            return 0
        elif files_ok:
            print_warning("⚠️  Setup parcialmente concluído")
            print_warning("Dependências podem ter falhado, mas arquivos estão OK")
            print_info("Tente instalar manualmente: pip install -r requirements_singularity.txt")
            return 1
        else:
            print_error("❌ Setup com problemas")
            print_error("Verifique os erros acima")
            return 2
            
    except KeyboardInterrupt:
        print_warning("\n\n⚠️  Setup interrompido pelo usuário")
        return 130
    except Exception as e:
        print_error(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\nCódigo de saída: {exit_code}")
    sys.exit(exit_code)
