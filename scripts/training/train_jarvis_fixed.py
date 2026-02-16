# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Treinamento Corrigido
Versão melhorada com dashboard funcionando
"""
import sys
import os
import threading
import subprocess
import asyncio
sys.path.insert(0, 'src')

# Configurar logging para usar web_emitter
import logging
from src.utils.web_emitter import emit_log_sync

class WebSocketHandler(logging.Handler):
    """Handler customizado para enviar logs via WebSocket"""
    def emit(self, record):
        try:
            message = self.format(record)
            level = record.levelname
            # Usar função síncrona para não bloquear
            emit_log_sync(message, level)
        except Exception:
            pass  # Silenciar erros do logging

def setup_websocket_logging():
    """Configura logging para enviar via WebSocket"""
    # Criar handler customizado
    ws_handler = WebSocketHandler()
    ws_handler.setLevel(logging.INFO)
    ws_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Adicionar aos loggers principais
    loggers = ['src.learning.distributed_trainer', 'EXTERNAL-TRAINER', 'JARVIS-DISTILLER']
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(ws_handler)
        logger.setLevel(logging.INFO)

def start_web_server():
    """Inicia o web server em background"""
    import socket

    # Tentar portas alternativas se 5000 estiver ocupada
    ports = [5000, 5001, 5002, 8000, 8001]
    selected_port = None

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            selected_port = port
            break
        except OSError:
            continue

    if selected_port is None:
        print("❌ Não foi possível encontrar uma porta disponível")
        return

    try:
        from web.web_server import start_server
        import uvicorn

        async def run_server():
            config = uvicorn.Config('web.web_server:app', host='localhost', port=selected_port, log_level='error')
            server = uvicorn.Server(config)
            await server.serve()

        # Configurar logging antes de iniciar
        setup_websocket_logging()

        print(f"🌐 Dashboard iniciado na porta {selected_port}")
        asyncio.run(run_server())
    except Exception as e:
        print(f"⚠️  Web server: {e}")

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu():
    limpar_tela()
    print("🤖 JARVIS 5.0 - TREINAMENTO INTELIGENTE")
    print("=" * 60)
    print("🎯 Treine o JARVIS em QUALQUER tópico!")
    print()
    print("📚 EXEMPLOS (apenas sugestões - você pode escolher qualquer coisa):")
    print("• Python, JavaScript, Machine Learning")
    print("• Física Quântica, História, Biologia")
    print("• Música, Arte, Filosofia, Matemática")
    print("• Qualquer assunto que você quiser!")
    print("=" * 60)

def perguntar_topico():
    while True:
        topico = input("🎯 Qual tópico você quer que o JARVIS estude? ").strip()
        if topico:
            return topico
        print("❌ Digite um tópico válido.")

def perguntar_componente():
    print()
    print("🔧 COMPONENTES DISPONÍVEIS:")
    print("1. study     - Estudo geral (recomendado)")
    print("2. llm       - Foco em linguagem")
    print("3. vision    - Foco em visão computacional")
    print("4. distributed - Treinamento avançado")

    while True:
        escolha = input("Escolha (1-4) ou Enter para 'study': ").strip()
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
            print("❌ Escolha inválida.")

def executar_treinamento(topico, componente):
    print(f"\n🚀 Iniciando treinamento...")
    print(f"📚 Tópico: {topico}")
    print(f"🔧 Componente: {componente}")
    print("=" * 60)

    cmd = f'python scripts/training/external_trainer.py --component {componente} --topic "{topico}" --config config/training_config.yaml'

    try:
        print("⏳ Executando treinamento... (logs aparecerão no dashboard)")
        print()

        result = os.system(cmd)

        print()
        if result == 0:
            print("🎉 TREINAMENTO CONCLUÍDO COM SUCESSO!")
            print("📁 Dados salvos em: data/learning/training_data/")
        else:
            print(f"❌ Erro no treinamento (código: {result})")

    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    # Iniciar web server
    print("🌐 Iniciando dashboard...")
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    # Aguardar um pouco para o server iniciar
    import time
    time.sleep(2)

    print("📊 Dashboard estará disponível em uma das portas: 5000, 5001, 5002, 8000, 8001")
    print("🔍 Verifique qual porta está funcionando!")
    print()

    # Menu interativo
    mostrar_menu()

    topico = perguntar_topico()
    componente = perguntar_componente()

    executar_treinamento(topico, componente)

    print("\n💡 DICAS:")
    print("• Dashboard: Verifique uma das portas acima")
    print("• Execute novamente para treinar outros tópicos")
    print("• Dados ficam em: data/learning/training_data/")

    input("\n⏸️  Pressione Enter para sair...")

if __name__ == "__main__":
    main()