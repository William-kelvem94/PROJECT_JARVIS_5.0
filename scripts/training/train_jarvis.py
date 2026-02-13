# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Sistema de Treinamento Interativo
Script que pergunta ao usuário o que treinar e inicia automaticamente
"""
import sys
import os
import threading
import subprocess
sys.path.insert(0, 'src')

def start_web_server():
    """Inicia o web server em background para monitoramento"""
    try:
        from web.web_server import start_server
        import asyncio
        import uvicorn
        async def run_server():
            config = uvicorn.Config('web.web_server:app', host='localhost', port=5000, log_level='warning')
            server = uvicorn.Server(config)
            await server.serve()
        asyncio.run(run_server())
    except Exception as e:
        print(f"⚠️  Web server não pôde ser iniciado: {e}")

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu_principal():
    """Mostra o menu principal do sistema de treinamento"""
    limpar_tela()
    print("🤖 JARVIS 5.0 - SISTEMA DE TREINAMENTO INTELIGENTE")
    print("=" * 65)
    print("🎯 Treine o JARVIS em qualquer tópico que você quiser!")
    print()
    print("📚 EXEMPLOS DE TÓPICOS:")
    print("• Inteligência Artificial")
    print("• Machine Learning")
    print("• Deep Learning")
    print("• Processamento de Linguagem Natural")
    print("• Visão Computacional")
    print("• Robótica")
    print("• Qualquer assunto técnico ou científico!")
    print()
    print("🔧 COMPONENTES DISPONÍVEIS:")
    print("• study     - Estudo geral (recomendado para começar)")
    print("• llm       - Modelo de Linguagem")
    print("• vision    - Visão Computacional")
    print("• distributed - Treinamento Distribuído")
    print("=" * 65)

def perguntar_topico():
    """Pergunta ao usuário qual tópico treinar"""
    while True:
        print()
        topico = input("🎯 Qual tópico você quer que o JARVIS estude? ").strip()
        if topico:
            return topico
        print("❌ Por favor, digite um tópico válido.")

def perguntar_componente():
    """Pergunta qual componente usar"""
    print()
    print("🔧 Escolha o tipo de treinamento:")
    print("1. study     - Estudo geral (recomendado)")
    print("2. llm       - Foco em linguagem")
    print("3. vision    - Foco em visão computacional")
    print("4. distributed - Treinamento avançado")

    while True:
        escolha = input("Escolha (1-4) ou pressione Enter para 'study': ").strip()
        if not escolha:
            return "study"
        if escolha == "1":
            return "study"
        elif escolha == "2":
            return "llm"
        elif escolha == "3":
            return "vision"
        elif escolha == "4":
            return "distributed"
        else:
            print("❌ Escolha inválida. Tente novamente.")

def executar_treinamento(topico, componente):
    """Executa o treinamento com os parâmetros escolhidos"""
    print(f"\n🚀 Iniciando treinamento...")
    print(f"📚 Tópico: {topico}")
    print(f"🔧 Componente: {componente}")
    print("=" * 65)

    # Comando para executar o treinamento
    cmd = f'python scripts/external_trainer.py --component {componente} --topic "{topico}" --config config/training_config.yaml'

    try:
        print("⏳ Executando treinamento... (pode demorar alguns minutos)")
        print()

        # Executar comando
        resultado = os.system(cmd)

        print()
        if resultado == 0:
            print("🎉 TREINAMENTO CONCLUÍDO COM SUCESSO!")
            print("📁 Dados salvos em: data/learning/training_data/")
            print("📊 Verifique o dashboard web para métricas detalhadas")
        else:
            print(f"❌ Erro durante o treinamento (código: {resultado})")
            print("🔍 Verifique os logs para mais detalhes")

    except Exception as e:
        print(f"❌ Erro ao executar treinamento: {e}")

def mostrar_instrucoes_finais():
    """Mostra instruções finais para o usuário"""
    print("\n" + "=" * 65)
    print("💡 DICAS PARA CONTINUAR:")
    print("• Acesse http://localhost:5000 para ver logs em tempo real")
    print("• Execute novamente este script para treinar outros tópicos")
    print("• Verifique data/learning/training_data/ para ver dados gerados")
    print("• Use 'python main.py' para interagir com o JARVIS treinado")
    print("=" * 65)

def main():
    """Função principal do programa"""
    # Iniciar web server em background
    print("🌐 Iniciando dashboard web...")
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    # Mostrar menu e coletar informações
    mostrar_menu_principal()

    topico = perguntar_topico()
    componente = perguntar_componente()

    # Executar treinamento
    executar_treinamento(topico, componente)

    # Mostrar instruções finais
    mostrar_instrucoes_finais()

    input("\n⏸️  Pressione Enter para sair...")

if __name__ == "__main__":
    main()