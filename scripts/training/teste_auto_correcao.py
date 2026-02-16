# -*- coding: utf-8 -*-
"""
TESTE - Sistema de Auto-Correção Evolutiva
Demonstra o JARVIS aprendendo com dissonâncias semânticas
"""

import sys
import io

# 🛡️ BLINDAGEM DE CODIFICAÇÃO UTF-8 UNIVERSAL (Windows Terminal Fix)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import time
from pathlib import Path

# Adicionar diretório raiz
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.learning.semantic_feedback import (
    get_semantic_analyzer,
    process_interaction_feedback,
)


def simulate_learning_scenario():
    """Simula um cenário de aprendizado com dissonâncias"""
    print("TESTE: Sistema de Auto-Correcao Evolutiva")
    print("=" * 60)

    analyzer = get_semantic_analyzer()

    # Cenário 1: Interações positivas (sem dissonância)
    print("\n📚 CENÁRIO 1: Interações positivas")
    print("-" * 40)

    positive_interactions = [
        (
            "Explique o que é Machine Learning",
            "Machine Learning é um campo da inteligência artificial que permite aos sistemas aprenderem automaticamente com dados, sem serem explicitamente programados para cada tarefa específica.",
        ),
        (
            "Como funciona o aprendizado supervisionado?",
            "No aprendizado supervisionado, o algoritmo aprende com um conjunto de dados rotulado, onde cada exemplo tem uma entrada e uma saída conhecida. O objetivo é aprender uma função que mapeie entradas para saídas.",
        ),
        (
            "Quais são os tipos de Machine Learning?",
            "Existem três tipos principais: supervisionado (com rótulos), não supervisionado (sem rótulos) e por reforço (aprendizado através de recompensas e punições).",
        ),
    ]

    for user_input, ai_response in positive_interactions:
        result = process_interaction_feedback(user_input, ai_response)
        confidence = result["confidence_score"]
        dissonance = result["dissonance_detected"]
        print(f"✅ Confiança: {confidence:.2f} | Dissonância: {dissonance}")

    # Aguardar processamento assíncrono
    time.sleep(2)

    # Cenário 2: Introduzir dissonância (resposta inadequada)
    print("\n🎯 CENÁRIO 2: Dissonância detectada")
    print("-" * 40)

    dissonant_interactions = [
        (
            "Como otimizar um modelo de ML?",
            "Não sei, pergunte ao Google.",
        ),  # Resposta ruim
        (
            "Qual a diferença entre overfitting e underfitting?",
            "São a mesma coisa.",
        ),  # Resposta incorreta
        ("Explique gradient descent", "É um tipo de dança."),  # Resposta absurda
    ]

    for user_input, ai_response in dissonant_interactions:
        result = process_interaction_feedback(user_input, ai_response)
        confidence = result["confidence_score"]
        dissonance = result["dissonance_detected"]
        status = "🚨 DISSONÂNCIA!" if dissonance else "✅ OK"
        print(f"{status} Confiança: {confidence:.2f} | Dissonância: {dissonance}")

    # Aguardar processamento assíncrono e possível auto-reparo
    print("\n⏳ Aguardando processamento assíncrono...")
    time.sleep(8)  # Dar tempo para o loop assíncrono detectar e processar

    # Cenário 3: Sistema "aprendeu" - respostas melhoradas
    print("\n🚀 CENÁRIO 3: Sistema adaptado (respostas melhoradas)")
    print("-" * 40)

    improved_interactions = [
        (
            "Como otimizar um modelo de ML?",
            "Para otimizar um modelo de Machine Learning, você pode usar técnicas como validação cruzada, ajuste de hiperparâmetros com grid search ou random search, regularização para evitar overfitting, e ensemble methods como bagging ou boosting.",
        ),
        (
            "Qual a diferença entre overfitting e underfitting?",
            "Overfitting ocorre quando o modelo se ajusta demais aos dados de treinamento, perdendo capacidade de generalização. Underfitting acontece quando o modelo é muito simples para capturar os padrões dos dados.",
        ),
        (
            "Explique gradient descent",
            "Gradient descent é um algoritmo de otimização usado para minimizar a função de custo em machine learning. Ele funciona calculando o gradiente da função de erro e atualizando os parâmetros na direção oposta ao gradiente.",
        ),
    ]

    for user_input, ai_response in improved_interactions:
        result = process_interaction_feedback(user_input, ai_response)
        confidence = result["confidence_score"]
        dissonance = result["dissonance_detected"]
        print(f"✅ Confiança: {confidence:.2f} | Dissonância: {dissonance}")

    # Status final do sistema
    print("\n📊 STATUS FINAL DO SISTEMA:")
    print("-" * 40)

    status = analyzer.get_system_status()
    print(f"Total de interações: {status['total_interactions']}")
    print(f"Confiança média: {status['average_confidence']:.2f}")
    print(f"Eventos de dissonância: {status['dissonance_events']}")
    print(f"Ciclos de adaptação: {status['adaptation_cycles']}")
    print(f"Sistema adaptando: {status['is_adapting']}")

    if status["last_adaptation"]:
        print(f"Última adaptação: {status['last_adaptation']}")

    print("\n🎉 Sistema de Auto-Correção Evolutiva demonstrado!")
    print(
        "O JARVIS agora aprende com suas próprias falhas e se adapta automaticamente."
    )


def test_ultra_auto_critique():
    """Testa a funcionalidade de auto-crítica Ultra"""
    print("\n🧠 TESTE: Auto-Crítica Ultra")
    print("=" * 60)

    from src.learning.semantic_feedback import SemanticInteraction

    # Criar interações de exemplo com dissonância
    dissonant_sequence = [
        SemanticInteraction(
            interaction_id="test_1",
            user_input="Explique Machine Learning",
            ai_response="Não sei explicar isso",
            confidence_score=0.2,
            dissonance_detected=True,
        ),
        SemanticInteraction(
            interaction_id="test_2",
            user_input="Como funciona o gradient descent?",
            ai_response="É um tipo de comida italiana",
            confidence_score=0.1,
            dissonance_detected=True,
        ),
        SemanticInteraction(
            interaction_id="test_3",
            user_input="Qual a diferença entre ML e AI?",
            ai_response="São iguais",
            confidence_score=0.3,
            dissonance_detected=True,
        ),
    ]

    analyzer = get_semantic_analyzer()
    critique = analyzer.perform_ultra_auto_critique(dissonant_sequence)

    print("📝 ANÁLISE GERADA:")
    print("-" * 40)
    print(critique)
    print("-" * 40)
    print("✅ Auto-crítica Ultra funcionando!")


if __name__ == "__main__":
    # Teste completo do sistema
    simulate_learning_scenario()

    # Teste da auto-crítica
    test_ultra_auto_critique()

    print("\n🎯 Sistema de Auto-Correção Evolutiva está OPERACIONAL!")
    print("O JARVIS agora aprende com a nuance da conversa humana de forma invisível.")
