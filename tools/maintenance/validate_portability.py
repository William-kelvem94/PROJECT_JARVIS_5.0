#!/usr/bin/env python3
"""
JARVIS 5.0 - Portability Validator
Valida se o projeto pode rodar em qualquer PC
"""

import os
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
        r'C:\\Users\\willi',
        r'/home/willi',
        r'williamkelvem64@gmail\.com'
    ]

    for pattern in hardcoded_patterns:
        try:
            result = os.popen(f'grep -r "{pattern}" "{project_root}" --include="*.py" --include="*.md" 2>/dev/null').read()
            if result.strip():
                lines = result.strip().split('\n')
                issues.extend(lines[:5])  # Limitar a 5 exemplos
        except Exception:
            pass

    # 2. Verificar estrutura de arquivos
    print("📋 Verificando estrutura de arquivos...")
    required_files = [
        "main.py",
        "START_JARVIS.bat",
        "INSTALL_JARVIS.bat",
        "config/settings.json",
        "config/ai_config.yaml"
    ]

    for file_path in required_files:
        if not (project_root / file_path).exists():
            issues.append(f"Arquivo obrigatório não encontrado: {file_path}")

    # 3. Verificar caminhos relativos
    print("🔗 Verificando uso de caminhos relativos...")
    main_py = project_root / "main.py"
    if main_py.exists():
        with open(main_py, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Path(__file__)' not in content:
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
