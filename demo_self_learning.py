#!/usr/bin/env python3
"""
JARVIS 5.0 - Self-Learning Engine Demo
Demonstração do sistema de auto-aprendizado
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def demo_self_learning():
    """Demonstra o Self-Learning Engine em ação"""
    print("🚀 JARVIS 5.0 - Self-Learning Engine Demo")
    print("=" * 60)

    try:
        from src.core.evolution.self_learning_engine import SelfLearningEngine

        # Inicializar engine
        PROJECT_ROOT = Path(__file__).parent
        learning_engine = SelfLearningEngine(PROJECT_ROOT)

        print("🧠 Self-Learning Engine inicializado")
        print("📊 Iniciando análise completa do sistema...")

        # Análise completa
        start_time = time.time()
        learning_engine._analyze_entire_system()
        analysis_time = time.time() - start_time

        print(".2f"
        # Gerar insights
        print("\\n💡 Gerando insights baseados na análise...")
        learning_engine._generate_insights()

        # Sugerir melhorias
        print("🚀 Sugerindo melhorias...")
        learning_engine._suggest_improvements()

        # Gerar documentação
        print("📄 Gerando documentação automática...")
        learning_engine._generate_auto_documentation()

        # Mostrar estatísticas
        stats = learning_engine.get_learning_stats()
        print("\\n📊 ESTATÍSTICAS DA ANÁLISE:"        print(f"  • Arquivos analisados: {stats['analysis_count']}")
        print(f"  • Insights gerados: {stats['insights_generated']}")
        print(f"  • Melhorias sugeridas: {stats['improvements_suggested']}")

        # Mostrar alguns insights
        if "insights" in learning_engine.knowledge_base:
            insights = learning_engine.knowledge_base["insights"]
            print("\\n💡 PRINCIPAIS INSIGHTS:")
            for insight in insights[:3]:  # Top 3
                print(f"  • {insight['title']} ({insight['priority'].upper()})")

        # Mostrar melhorias
        if learning_engine.auto_improvements:
            print("\\n🚀 MELHORIAS SUGERIDAS:")
            for imp in learning_engine.auto_improvements[:3]:  # Top 3
                print(f"  • {imp['title']} ({imp.get('priority', 'medium').upper()})")

        # Salvar conhecimento
        print("\\n💾 Salvando conhecimento adquirido...")
        learning_engine._save_knowledge_base()

        print("\\n✅ Demo concluída com sucesso!")
        print("\\n📁 Verifique as seguintes pastas para ver os resultados:")
        print("  • docs/auto_generated/ - Documentação gerada automaticamente")
        print("  • data/learning/self_knowledge/ - Base de conhecimento")

        # Simular aprendizado contínuo por alguns segundos
        print("\\n🔄 Iniciando aprendizado contínuo por 10 segundos...")
        learning_engine.start_continuous_learning()
        await asyncio.sleep(10)
        learning_engine.stop_continuous_learning()

        print("\\n🧠 Aprendizado contínuo finalizado e conhecimento salvo!")

    except Exception as e:
        print(f"❌ Erro na demo: {e}")
        import traceback
        traceback.print_exc()

async def test_learning_commands():
    """Testa os comandos especiais de aprendizado"""
    print("\\n\\n🧪 Testando comandos especiais de aprendizado...")
    print("=" * 60)

    try:
        from src.core.intelligence.ai_agent import ai_agent

        # Testar comando de status
        print("📊 Testando comando 'status aprendizado'...")
        response = await ai_agent.process_command("status aprendizado")
        print(f"Resposta: {response[:200]}...")

        # Testar comando de análise
        print("\\n🔍 Testando comando 'analise sistema'...")
        response = await ai_agent.process_command("analise sistema")
        print(f"Resposta: {response[:200]}...")

        # Testar comando de melhorias
        print("\\n🚀 Testando comando 'melhorias sugeridas'...")
        response = await ai_agent.process_command("melhorias sugeridas")
        print(f"Resposta: {response[:200]}...")

        print("\\n✅ Testes de comandos concluídos!")

    except Exception as e:
        print(f"❌ Erro nos testes de comandos: {e}")

async def main():
    """Função principal da demo"""
    await demo_self_learning()
    await test_learning_commands()

    print("\\n🎉 Demo do Self-Learning Engine concluída!")
    print("\\n💡 O JARVIS agora pode:")
    print("  • Aprender continuamente sobre seu próprio código")
    print("  • Identificar problemas e sugerir melhorias")
    print("  • Gerar documentação automaticamente")
    print("  • Melhorar seu próprio desempenho")
    print("  • Salvar conhecimento quando encerrado")
    print("\\n🧠 O futuro da IA está aqui - JARVIS aprendendo sobre si mesmo!")

if __name__ == "__main__":
    asyncio.run(main())