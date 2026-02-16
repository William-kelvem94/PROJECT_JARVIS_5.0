import sys
from pathlib import Path

# Adicionar diretórios ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.management.maintenance_manager import maintenance_manager

print("--- TESTE DE ALINHAMENTO DE DEPENDÊNCIAS ---")
maintenance_manager.check_and_repair_all()
print("--- TESTE CONCLUÍDO ---")

import numpy as np

print(f"Versão final do NumPy: {np.__version__}")
