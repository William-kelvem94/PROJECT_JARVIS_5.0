#!/usr/bin/env python3
"""
Script de Teste Rápido para Treinamento JARVIS 5.0
Testa o sistema de treinamento com simulação
"""

import sys
import os
from pathlib import Path

# Configurar path
script_dir = Path(__file__).resolve()
project_root = script_dir.parent.parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def test_training(topic="machine learning", component="study"):
    """Testa o treinamento com tópico e componente específicos"""
    print("🚀 JARVIS 5.0 - Teste de Treinamento Rápido")
    print("=" * 50)
    print(f"📚 Tópico: {topic}")
    print(f"🔧 Componente: {component}")
    print()

    # Importar e executar treinamento
    try:
        from scripts.training.external_trainer import train_study

        # Carregar config básica
        config = {
            "topic": topic,
            "output_dir": "data/learning/training_data",
            "model_name": "distilgpt2",
        }

        print("⏳ Iniciando treinamento simulado...")
        success = train_study(config, topic)

        if success:
            print("\n🎉 Teste concluído com sucesso!")
            print("✅ Sistema de treinamento funcionando corretamente")
            print("✅ Simulação de fine-tuning operacional")
            print("✅ Destilação de conhecimento ativa")
        else:
            print("\n❌ Teste falhou")
            return False

    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    # Aceitar argumentos de linha de comando
    topic = sys.argv[1] if len(sys.argv) > 1 else "machine learning"
    component = sys.argv[2] if len(sys.argv) > 2 else "study"

    success = test_training(topic, component)
    sys.exit(0 if success else 1)
