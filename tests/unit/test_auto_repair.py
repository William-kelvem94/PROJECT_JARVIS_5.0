#!/usr/bin/env python3
"""
Script de teste para validar o sistema de auto-reparo expandido
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.management.maintenance_manager import maintenance_manager

print("=" * 60)
print("   TESTE DE AUTO-REPARO TOTAL - JARVIS 5.0")
print("=" * 60)
print()

# Callback para mostrar progresso
def show_progress(message):
    print(f"[PROGRESSO] {message}")

maintenance_manager.on_progress = show_progress

print("Iniciando verificação completa...")
print()

maintenance_manager.check_and_repair_all()

print()
print("=" * 60)
print("   VERIFICAÇÃO CONCLUÍDA")
print("=" * 60)
print()

# Validar resultados
print("Validando instalações:")
print()

# 1. Verificar CMake
import subprocess
try:
    result = subprocess.run(["cmake", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✅ CMake:", result.stdout.split()[2])
    else:
        print("❌ CMake não encontrado")
except:
    print("❌ CMake não encontrado")

# 2. Verificar Vosk
vosk_path = Path("models/vosk-model-small-pt-0.22")
if vosk_path.exists() and (vosk_path / "am" / "final.mdl").exists():
    print("✅ Modelo Vosk PT-BR instalado")
else:
    print("❌ Modelo Vosk PT-BR não encontrado")

# 3. Verificar face_recognition
try:
    import face_recognition
    print("✅ face_recognition disponível")
except ImportError:
    print("❌ face_recognition não disponível")

# 4. Verificar NumPy
import numpy as np
print(f"✅ NumPy: {np.__version__}")

# 5. Verificar Protobuf
try:
    import google.protobuf
    print(f"✅ Protobuf: {google.protobuf.__version__}")
except:
    print("❌ Protobuf não disponível")

print()
print("=" * 60)
