import numpy as np
from src.core.management.maintenance_manager import maintenance_manager
import sys
from pathlib import Path

# Adicionar diretórios ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


print("--- TESTE DE ALINHAMENTO DE DEPENDÊNCIAS ---")
maintenance_manager.check_and_repair_all()
print("--- TESTE CONCLUÍDO ---")


print(f"Versão final do NumPy: {np.__version__}")
