"""
JARVIS SINGULARITY - Setup & Installation Script
Instala dependências e configura o ambiente
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """Exibe banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗          ║
    ║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝          ║
    ║        ██║███████║██████╔╝██║   ██║██║███████╗          ║
    ║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║          ║
    ║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║          ║
    ║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝          ║
    ║                                                           ║
    ║              🚀 SINGULARITY SETUP 🚀                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica versão do Python"""
    print("\n🔍 Verificando versão do Python...")
    
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ necessário. Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_requirements():
    """Instala dependências"""
    print("\n📦 Instalando dependências...")
    
    requirements_file = Path("requirements_singularity.txt")
    
    if not requirements_file.exists():
        print(f"❌ Arquivo não encontrado: {requirements_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependências instaladas!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_rclone():
    """Verifica se rclone está instalado"""
    print("\n🔍 Verificando Rclone...")
    
    try:
        result = subprocess.run(
            ["rclone", "version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Rclone instalado")
            return True
    except:
        pass
    
    print("⚠️ Rclone não encontrado")
    print("📥 Instale: https://rclone.org/downloads/")
    print("   Windows: choco install rclone")
    return False

def create_config_template():
    """Cria template de configuração"""
    print("\n📝 Criando template de configuração...")
    
    config_file = Path("config.yaml")
    
    if config_file.exists():
        print("ℹ️ config.yaml já existe")
        return True
    
    # Config já foi criado anteriormente
    print("✅ Use o config.yaml existente")
    return True

def run_migration():
    """Executa migração de estrutura"""
    print("\n🏗️ Executando migração de estrutura...")
    
    migrate_script = Path("migrate_structure.py")
    
    if not migrate_script.exists():
        print(f"❌ Script não encontrado: {migrate_script}")
        return False
    
    print("⚠️ Isso vai reorganizar a estrutura do projeto")
    print("Um backup será criado em _backup_legacy/")
    print("\nDeseja continuar? (s/n): ", end="")
    
    choice = input().lower()
    
    if choice == 's':
        try:
            subprocess.check_call([sys.executable, str(migrate_script), "--auto"])
            print("✅ Migração concluída!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na migração: {e}")
            return False
    else:
        print("Migração cancelada")
        return False

def main():
    """Função principal"""
    print_banner()
    
    steps = [
        ("Verificar Python", check_python_version),
        ("Instalar Dependências", install_requirements),
        ("Verificar Rclone", check_rclone),
        ("Configuração", create_config_template),
        ("Migração de Estrutura", run_migration)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"  {step_name}")
        print(f"{'='*60}")
        
        result = step_func()
        results.append((step_name, result))
    
    # Resumo
    print(f"\n{'='*60}")
    print("  RESUMO DA INSTALAÇÃO")
    print(f"{'='*60}\n")
    
    for step_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {step_name}")
    
    all_success = all(r for _, r in results)
    
    if all_success:
        print(f"\n{'='*60}")
        print("  🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*60}")
        print("\n🚀 Próximos passos:")
        print("  1. Configure suas API keys em config.yaml")
        print("  2. Execute: python main_singularity.py")
        print("  3. Ou use o watchdog: watchdog_launcher.bat")
    else:
        print(f"\n{'='*60}")
        print("  ⚠️ INSTALAÇÃO INCOMPLETA")
        print(f"{'='*60}")
        print("\nResolva os problemas acima e execute novamente.")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
