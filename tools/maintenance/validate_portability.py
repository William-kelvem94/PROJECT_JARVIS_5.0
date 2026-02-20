#!/usr/bin/env python3
"""
JARVIS 5.0 - Portability Validator
Valida se o projeto pode rodar em qualquer PC
"""

import sys

from pathlib import Path


def validate_portability():
    """Valida portabilidade do projeto"""
    print("🔍 JARVIS 5.0 - Validador de Portabilidade")
    print("=" * 50)

    project_root = Path(__file__).parent.parent
    issues = []

    # 1. Verificar caminhos hardcoded
    print("📁 Verificando caminhos hardcoded...")
    hardcoded_patterns = [
        r"C:\\Users\\willi",
        r"/home/willi",
        r"williamkelvem64@gmail\.com",
    ]

    # Buscar padrões de forma multiplataforma usando pathlib e leitura de
    # arquivos
    search_files = list(project_root.rglob("*.py")) + list(project_root.rglob("*.md"))

    for pattern in hardcoded_patterns:
        examples_for_pattern = 0
        for file_path in search_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for lineno, line in enumerate(f, start=1):
                        if pattern in line:
                            issues.append(f"{file_path}:{lineno}:{line.rstrip()}")
                            examples_for_pattern += 1
                            if (
                                examples_for_pattern >= 5
                            ):  # Limitar a 5 exemplos por padrão
                                break
            except (OSError, UnicodeError):
                # Ignorar arquivos que não puderem ser lidos
                continue
            if examples_for_pattern >= 5:
                break

    # 2. Verificar estrutura de arquivos
    print("📋 Verificando estrutura de arquivos...")
    required_files = [
        "main.py",
        "START_JARVIS.bat",
        "INSTALL_JARVIS.bat",
        "config/settings.json",
        "config/ai_config.yaml",
    ]

    for file_path in required_files:
        if not (project_root / file_path).exists():
            issues.append(f"Arquivo obrigatório não encontrado: {file_path}")

    # 3. Verificar caminhos relativos
    print("🔗 Verificando uso de caminhos relativos...")
    main_py = project_root / "main.py"
    if main_py.exists():
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()
            if "Path(__file__)" not in content:
                issues.append("main.py não usa caminhos relativos")

    # Resultado
    print("\n📊 RESULTADO DA VALIDAÇÃO:")
    if issues:
        print(f"⚠️  ENCONTRADOS {len(issues)} PROBLEMAS:")
        for issue in issues[:10]:  # Mostrar apenas os primeiros 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... e mais {len(issues) - 10} problemas")
        print("\n❌ PROJETO NÃO É TOTALMENTE PORTÁVEL")
        return False
    else:
        print("✅ NENHUM PROBLEMA ENCONTRADO")
        print("✅ PROJETO TOTALMENTE PORTÁVEL")
        return True


if __name__ == "__main__":
    success = validate_portability()
    sys.exit(0 if success else 1)
