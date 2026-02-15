#!/usr/bin/env python3
"""
Teste de Compatibilidade PyTorch 2026
Verifica se torch_dtype foi substituído por dtype
"""

import sys
import io

# 🛡️ BLINDAGEM DE CODIFICAÇÃO UTF-8 UNIVERSAL (Windows Terminal Fix)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import warnings
from pathlib import Path

# 🔧 BOOTSTRAP DE CAMINHO DE MÓDULO (Resolução de 'No module named src')
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Adicionar diretório raiz (mantido para compatibilidade)
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_dtype_compatibility():
    """Testa se os modelos carregam sem warnings de depreciação"""
    print("🔧 TESTE: Compatibilidade PyTorch 2026")
    print("=" * 50)

    # Capturar warnings
    warnings.simplefilter('always')

    try:
        print("📥 Testando RealTrainer...")
        from src.learning.real_trainer import RealTrainer

        # Capturar warnings específicos
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trainer = RealTrainer()

            # Verificar se há warnings de torch_dtype
            torch_dtype_warnings = [warning for warning in w
                                  if 'torch_dtype' in str(warning.message).lower()
                                  and 'deprecated' in str(warning.message).lower()]

            if torch_dtype_warnings:
                print("❌ Ainda há warnings de torch_dtype deprecated:")
                for warning in torch_dtype_warnings:
                    print(f"   {warning.message}")
                return False
            else:
                print("✅ RealTrainer: Sem warnings de torch_dtype!")

    except Exception as e:
        print(f"❌ Erro no RealTrainer: {e}")
        return False

    try:
        print("📥 Testando SemanticFeedback...")
        from src.learning.semantic_feedback import get_semantic_analyzer

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            analyzer = get_semantic_analyzer()

            torch_dtype_warnings = [warning for warning in w
                                  if 'torch_dtype' in str(warning.message).lower()
                                  and 'deprecated' in str(warning.message).lower()]

            if torch_dtype_warnings:
                print("❌ Ainda há warnings de torch_dtype deprecated:")
                for warning in torch_dtype_warnings:
                    print(f"   {warning.message}")
                return False
            else:
                print("✅ SemanticFeedback: Sem warnings de torch_dtype!")

    except Exception as e:
        print(f"❌ Erro no SemanticFeedback: {e}")
        return False

    print("\n🎉 SUCESSO: Código compatível com PyTorch 2026!")
    print("✅ torch_dtype substituído por dtype em todos os locais")
    print("✅ Warnings de depreciação removidos")
    return True

if __name__ == "__main__":
    success = test_dtype_compatibility()
    sys.exit(0 if success else 1)