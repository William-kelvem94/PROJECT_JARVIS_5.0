#!/usr/bin/env python3
"""
Script de Verificação Final - JARVIS Ultimate
Verifica se todos os componentes estão funcionando corretamente
"""

import sys
import importlib
import subprocess

def check_module(module_name, description):
    """Verifica se um módulo pode ser importado."""
    try:
        importlib.import_module(module_name)
        print(f"[OK] {description}")
        return True
    except ImportError as e:
        print(f"[ERRO] {description}: {e}")
        return False

def check_command(command, description):
    """Verifica se um comando externo funciona."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] {description}")
            return True
        else:
            print(f"[ERRO] {description}: {result.stderr.strip()}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"[AVISO] {description}: {e}")
        return False

def main():
    print("JARVIS Ultimate - Verificacao Final")
    print("=" * 50)

    all_good = True

    # Verificar Python
    print(f"Python {sys.version.split()[0]}")
    all_good &= sys.version_info >= (3, 11)

    # Verificar módulos principais
    print("\nVerificando Modulos Principais:")
    modules_to_check = [
        ("config", "Configuracoes"),
        ("core.brain", "Cerebro RAG"),
        ("core.hearing", "Sistema de Voz (STT)"),
        ("core.speech", "Sistema de Voz (TTS)"),
        ("core.hardware", "Monitoramento de Hardware"),
        ("tools.model_manager", "Gerenciador de Modelos"),
        ("core.local_llm", "Integracao Ollama"),
    ]

    for module, desc in modules_to_check:
        all_good &= check_module(module, desc)

    # Verificar dependências externas
    print("\nVerificando Dependencias Externas:")
    external_checks = [
        (["ollama", "--version"], "Ollama instalado"),
        (["python", "-c", "import chromadb"], "ChromaDB disponivel"),
    ]

    for cmd, desc in external_checks:
        all_good &= check_command(cmd, desc)

    # Verificar estrutura de arquivos
    print("\nVerificando Estrutura:")
    import os
    critical_files = [
        "main.py",
        "config.py",
        "core/brain.py",
        "core/hearing.py",
        "core/speech.py",
        "core/hardware.py",
        "requirements.txt",
        "README.md"
    ]

    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[ERRO] {file_path} - ARQUIVO AUSENTE")
            all_good = False

    # Resultado final
    print("\n" + "=" * 50)
    if all_good:
        print("JARVIS Ultimate esta pronto para uso!")
        print("\nExecute: python main.py")
    else:
        print("Alguns componentes precisam de atencao")
        print("Execute: pip install -r requirements.txt")
        print("Instale o Ollama: https://ollama.com")

    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())