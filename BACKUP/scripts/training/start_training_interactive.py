# -*- coding: utf-8 -*-
"""
Script Interativo para Iniciar Treinamento JARVIS 5.0
Pergunta ao usuário o que treinar e inicia automaticamente com dashboard
"""

import sys
import os
import threading

sys.path.insert(0, "src")


def start_web_server():
    """Inicia o web server em background para monitoramento em tempo real"""
    try:
        import asyncio
        import uvicorn

        async def run_server():
            config = uvicorn.Config(
                "web.web_server:app", host="localhost", port=5000, log_level="warning"
            )
            server = uvicorn.Server(config)
            await server.serve()

        asyncio.run(run_server())
    except Exception as e:
        print(f"⚠️  Erro ao iniciar web server: {e}")
        print("📊 Dashboard pode não estar disponível")


def get_training_topic():
    """Pergunta ao usuário o que ele quer treinar"""
    print("\nJARVIS 5.0 - Sistema de Treinamento Inteligente")
    print("=" * 60)
    print("Sobre o que voce gostaria de treinar o JARVIS?")
    print("\nExemplos:")
    print("• Inteligencia Artificial")
    print("• Machine Learning")
    print("• Deep Learning")
    print("• Processamento de Linguagem Natural")
    print("• Visao Computacional")
    print("• Qualquer topico que voce quiser!")
    print()

    while True:
        topic = input("Digite o topico para treinamento: ").strip()
        if topic:
            return topic
        print("Por favor, digite um topico valido.")


def get_training_component():
    """Pergunta qual componente treinar"""
    print("\nQual componente voce quer treinar?")
    print("1. study  - Estudo geral (recomendado)")
    print("2. llm    - Modelo de Linguagem")
    print("3. vision - Visao Computacional")
    print("4. distributed - Treinamento Distribuido")
    print()

    while True:
        choice = input("Escolha (1-4) ou pressione Enter para 'study': ").strip()
        if not choice:
            return "study"
        if choice == "1":
            return "study"
        elif choice == "2":
            return "llm"
        elif choice == "3":
            return "vision"
        elif choice == "4":
            return "distributed"
        else:
            print("Escolha invalida. Tente novamente.")


def main():
    """Função principal"""
    # Limpar tela
    os.system("cls" if os.name == "nt" else "clear")

    # Iniciar web server em background
    print("Iniciando dashboard web...")
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    print("Dashboard iniciado em: http://localhost:5000")
    print("Abra seu navegador para ver logs em tempo real!")
    print()

    # Perguntar ao usuário
    topic = get_training_topic()
    component = get_training_component()

    print("\nIniciando treinamento...")
    print(f"Topico: {topic}")
    print(f"Componente: {component}")
    print("=" * 60)

    # Executar treinamento
    cmd = f'python scripts/training/external_trainer.py --component {component} --topic "{topic}" --config config/training_config.yaml'

    try:
        result = os.system(cmd)
        if result == 0:
            print("\nTreinamento concluido com sucesso!")
            print("Verifique os dados gerados em: data/learning/training_data/")
        else:
            print(f"\nErro durante o treinamento (codigo: {result})")
    except Exception as e:
        print(f"\nErro ao executar treinamento: {e}")

    print("\nDica: Mantenha o navegador aberto em http://localhost:5000")
    print("   para ver logs detalhados e metricas em tempo real!")


if __name__ == "__main__":
    main()
