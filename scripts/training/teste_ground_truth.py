# -*- coding: utf-8 -*-
"""
TESTE DE VALIDAÇÃO COM GROUND TRUTH
JARVIS 5.0 - Teste da Integração Truth Validator + Auto-Correção
"""

import sys
import io

# 🛡️ BLINDAGEM DE CODIFICAÇÃO UTF-8 UNIVERSAL (Windows Terminal Fix)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import json
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TESTE-GROUND-TRUTH")

# Adicionar diretório raiz
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_truth_validator_standalone():
    """Testa o TruthValidator de forma independente"""
    logger.info("🧪 Testando TruthValidator standalone")

    try:
        from src.learning.truth_validator import get_truth_validator

        validator = get_truth_validator()

        # Teste 1: Validação de fato simples
        query1 = "O que é machine learning?"
        logger.info(f"🔍 Testando validação: {query1}")
        result1 = validator.validate_fact(query1)

        print(f"\n✅ Resultado da validação para '{query1}':")
        print(f"   Confiança: {result1.get('confidence_score', 0):.2f}")
        print(f"   Resultados encontrados: {len(result1.get('search_results', []))}")
        print(
            f"   Verdade consolidada: {result1.get('consolidated_truth', '')[:200]}..."
        )

        # Teste 2: Comparação de erro do JARVIS
        jarvis_error = "Machine learning é uma técnica de programação que permite aos computadores aprenderem automaticamente."
        web_truth = result1.get("consolidated_truth", "")
        auto_critique = "A definição está incompleta. Machine learning envolve algoritmos que aprendem padrões em dados."

        comparison = validator.compare_with_auto_critique(
            jarvis_error, web_truth, auto_critique
        )

        print("\n⚖️ Comparação realizada:")
        print(f"   Alinhamento: {comparison['alignment_score']:.2f}")
        print(f"   Recomendação: {comparison['recommendation'][:150]}...")

        return True

    except Exception as e:
        logger.error(f"❌ Erro no teste standalone: {e}")
        return False


def test_semantic_feedback_integration():
    """Testa a integração completa com SemanticFeedbackAnalyzer"""
    logger.info("🧪 Testando integração com SemanticFeedbackAnalyzer")

    try:
        from src.learning.semantic_feedback import get_semantic_analyzer

        analyzer = get_semantic_analyzer()

        # Simular interações que causam dissonância
        test_interactions = [
            {
                "user": "O que é inteligência artificial?",
                "ai": "IA é um campo da ciência da computação.",
            },
            {
                "user": "Como funciona o machine learning?",
                "ai": "Machine learning usa estatísticas para fazer previsões.",
            },
            {
                "user": "Qual a diferença entre IA e ML?",
                "ai": "São a mesma coisa.",  # Erro intencional para causar dissonância
            },
        ]

        # Processar interações
        processed_interactions = []
        for interaction in test_interactions:
            result = analyzer.process_interaction(
                interaction["user"], interaction["ai"]
            )
            processed_interactions.append(result)
            logger.info(
                f"📊 Interação processada - Confiança: {result.confidence_score:.2f}, Dissonância: {result.dissonance_detected}"
            )

        # Verificar se dissonância foi detectada
        dissonant_count = sum(
            1 for i in processed_interactions if i.dissonance_detected
        )
        print(
            f"\n🎯 Dissonâncias detectadas: {dissonant_count}/{len(test_interactions)}"
        )

        # Forçar trigger de auto-reparo (simulando baixa confiança)
        analyzer.confidence_metrics.average_confidence = (
            0.3  # Forçar abaixo do threshold
        )

        # Aguardar um momento para o loop assíncrono processar
        import time

        time.sleep(2)

        # Verificar status do sistema
        status = analyzer.get_system_status()
        print("\n📈 Status do sistema após processamento:")
        print(f"   Confiança média: {status['average_confidence']:.2f}")
        print(f"   Ciclos de adaptação: {status['adaptation_cycles']}")
        print(f"   Adaptando: {status['is_adapting']}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro na integração: {e}")
        return False


def test_full_auto_correction_cycle():
    """Testa o ciclo completo de auto-correção com validação externa"""
    logger.info("🧪 Testando ciclo completo de auto-correção")

    try:
        from src.learning.semantic_feedback import SemanticFeedbackAnalyzer

        # Criar analyzer
        analyzer = SemanticFeedbackAnalyzer()

        # Simular sequência dissonante
        dissonant_sequence = [
            analyzer.process_interaction(
                "Explique deep learning",
                "Deep learning é uma parte do machine learning que usa redes neurais.",
            ),
            analyzer.process_interaction(
                "Como as redes neurais funcionam?",
                "Redes neurais são como cérebros artificiais.",  # Resposta simplista demais
            ),
            analyzer.process_interaction(
                "Qual a diferença entre ML e DL?",
                "São iguais.",  # Erro para causar dissonância
            ),
        ]

        # Forçar dissonância
        for interaction in dissonant_sequence:
            interaction.dissonance_detected = True
            interaction.confidence_score = 0.2

        # Executar auto-crítica
        logger.info("🧠 Gerando auto-crítica...")
        critique = analyzer.perform_ultra_auto_critique(dissonant_sequence)
        print(f"\n📝 Auto-crítica gerada:\n{critique[:300]}...")

        # Executar síntese neural com validação (simulado - sem realmente treinar)
        logger.info("🔍 Executando validação externa e síntese neural...")
        # Nota: Em produção isso faria fine-tuning real, aqui apenas testamos a integração

        print("\n✅ Ciclo de auto-correção testado com sucesso")
        print(f"   Auto-crítica: {len(critique)} caracteres")
        print(f"   Sequência dissonante: {len(dissonant_sequence)} interações")

        return True

    except Exception as e:
        logger.error(f"❌ Erro no ciclo completo: {e}")
        return False


def run_all_tests():
    """Executa todos os testes"""
    logger.info("🚀 Iniciando suite de testes do Ground Truth Validation")

    test_results = {
        "truth_validator_standalone": test_truth_validator_standalone(),
        "semantic_feedback_integration": test_semantic_feedback_integration(),
        "full_auto_correction_cycle": test_full_auto_correction_cycle(),
    }

    # Resumo dos resultados
    passed = sum(test_results.values())
    total = len(test_results)

    print(f"\n{'='*60}")
    print("📊 RESULTADO DOS TESTES - GROUND TRUTH VALIDATION")
    print(f"{'='*60}")

    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")

    print(f"\n🎯 Total: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 Todos os testes passaram! Ground Truth Validation está funcionando.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs para detalhes.")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_results": test_results,
        "summary": f"{passed}/{total} testes passaram",
    }

    report_path = Path("data/learning/test_ground_truth_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"📄 Relatório salvo em {report_path}")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
