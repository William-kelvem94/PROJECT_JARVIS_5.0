#!/usr/bin/env python3
"""
JARVIS Ultimate - Script de Inicialização Rápida
Configura e inicia o JARVIS com verificações automáticas
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header():
    """Imprime cabeçalho estilizado."""
    print("""
🤖 JARVIS ULTIMATE - Inicialização Rápida
==========================================

Infraestrutura de Vida Artificial
""")

def check_python_version():
    """Verifica versão do Python."""
    print(" Verificando Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(" Python 3.11+ é necessário")
        sys.exit(1)
    print(f" Python {version.major}.{version.minor}.{version.micro}")

def check_ollama():
    """Verifica se Ollama está instalado e funcionando."""
    print("🤖 Verificando Ollama...")

    try:
        # Verificar se ollama está instalado
        result = subprocess.run(['ollama', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print(" Ollama não encontrado. Instale em: https://ollama.com")
            return False

        print(f" Ollama instalado: {result.stdout.strip()}")

        # Verificar se está rodando
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f" Ollama rodando com {len(models)} modelos")
                return True
            else:
                print("⚠️ Ollama instalado mas não está rodando")
                print(" Execute: ollama serve")
                return False
        except:
            print("⚠️ Ollama não está respondendo")
            print(" Execute: ollama serve")
            return False

    except FileNotFoundError:
        print(" Ollama não instalado")
        return False

def install_dependencies():
    """Instala dependências Python."""
    print(" Instalando dependências...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print(" Dependências instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Erro ao instalar dependências: {e}")
        return False

def setup_models():
    """Instala modelos essenciais."""
    print("🧠 Verificando modelos...")

    essential_models = ["codellama:7b", "mistral:7b"]

    for model in essential_models:
        print(f" Verificando {model}...")
        try:
            # Tentar listar modelos
            result = subprocess.run(['ollama', 'list'],
                                  capture_output=True, text=True, timeout=10)

            if model in result.stdout:
                print(f" {model} já instalado")
            else:
                print(f" Baixando {model}...")
                subprocess.run(['ollama', 'pull', model], check=True, timeout=300)
                print(f" {model} instalado")

        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout baixando {model}")
        except subprocess.CalledProcessError as e:
            print(f" Erro com {model}: {e}")

def create_directories():
    """Cria diretórios necessários."""
    print(" Criando diretórios...")

    dirs = ["data", "config", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

    print(" Diretórios criados")

def start_jarvis():
    """Inicia o JARVIS."""
    print(" Iniciando JARVIS Ultimate...")
    print()

    try:
        # Importar e executar
        from main import main
        main()
    except KeyboardInterrupt:
        print("\n JARVIS encerrado pelo usuário")
    except Exception as e:
        print(f" Erro ao iniciar JARVIS: {e}")
        return False

    return True

def main():
    """Função principal do script de inicialização."""
    print_header()

    # Verificações
    check_python_version()

    if not check_ollama():
        print("\n Instale e configure o Ollama primeiro:")
        print("   1. Baixe: https://ollama.com")
        print("   2. Execute: ollama serve")
        print("   3. Rode este script novamente")
        sys.exit(1)

    # Setup
    create_directories()

    if not install_dependencies():
        sys.exit(1)

    setup_models()

    print("\n Setup completo! Iniciando JARVIS...")
    print("=" * 50)

    # Iniciar
    start_jarvis()

if __name__ == "__main__":
    main()