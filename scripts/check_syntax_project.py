"""Verifica a sintaxe de todos os arquivos .py do repositório (ignora 'venv' e '.git').
Retorna código 0 se todos os arquivos compilarem corretamente, 1 caso contrário.
"""

import os
import py_compile
import sys

IGNORE_PARTS = ("/venv", "\\venv", "\\.venv", "env", "site-packages", ".git")

failed = []
for root, dirs, files in os.walk("."):
    if any(p in root for p in IGNORE_PARTS):
        continue
    for f in files:
        if not f.endswith(".py"):
            continue
        path = os.path.join(root, f)
        try:
            py_compile.compile(path, doraise=True)
        except Exception as e:
            failed.append((path, str(e)))

if failed:
    print(f"Found {len(failed)} files with syntax errors:")
    for p, err in failed:
        print(f" - {p}: {err}")
    sys.exit(1)

print("All project .py files compiled successfully.")
sys.exit(0)
