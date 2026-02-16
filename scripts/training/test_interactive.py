# -*- coding: utf-8 -*-
"""
Script de Teste Automático para Treinamento Interativo
Simula entrada do usuário para testar o sistema
"""

import sys
import subprocess


def test_interactive_training(topic="quantum computing", component="1"):
    """Testa o treinamento interativo com entradas simuladas"""

    # Criar arquivo temporário com as entradas
    input_data = f"{topic}\n{component}\n"

    # Caminho para o script interativo
    script_path = "scripts/training/start_training_interactive.py"

    print("🧪 Testando treinamento interativo...")
    print(f"📚 Tópico: {topic}")
    print(f"🔧 Componente: {component}")
    print("=" * 50)

    try:
        # Usar subprocess com input para simular entrada do usuário
        result = subprocess.run(
            [sys.executable, script_path],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=60,  # 60 segundos timeout
        )

        print("📤 SAÍDA DO SCRIPT:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  ERROS:")
            print(result.stderr)

        print(f"🔢 Código de saída: {result.returncode}")

        if result.returncode == 0:
            print("✅ Teste concluído com sucesso!")
        else:
            print("❌ Teste falhou!")

    except subprocess.TimeoutExpired:
        print("⏰ Timeout: O script demorou muito para responder")
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")


if __name__ == "__main__":
    # Testar com diferentes tópicos
    test_cases = [
        ("quantum computing", "1"),  # Avançado
        ("basic programming", "1"),  # Intermediário
        ("learning colors", "1"),  # Básico
    ]

    for topic, component in test_cases:
        print(f"\n{'='*60}")
        test_interactive_training(topic, component)
        print(f"{'='*60}")
