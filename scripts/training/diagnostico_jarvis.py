# -*- coding: utf-8 -*-
"""
Diagnóstico Completo do JARVIS 5.0
Verifica status do web server, dados de treinamento e conectividade
"""

import sys
import os
import socket
import requests
import json
import asyncio
import webbrowser

sys.path.insert(0, "src")


def verificar_web_server():
    """Verifica se o web server está funcionando"""
    print("🌐 VERIFICANDO WEB SERVER...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", 5000))
        sock.close()

        if result == 0:
            print("✅ Porta 5000 está ocupada - web server ativo")

            # Testar resposta HTTP
            try:
                response = requests.get("http://localhost:5000", timeout=5)
                if response.status_code == 200:
                    print("✅ Dashboard responde corretamente (HTTP 200)")
                    if "JARVIS" in response.text:
                        print("✅ Conteúdo do dashboard carregado")
                    else:
                        print("⚠️  Conteúdo pode estar incompleto")
                else:
                    print(f"❌ Erro HTTP: {response.status_code}")
            except Exception as e:
                print(f"❌ Erro ao acessar dashboard: {e}")

        else:
            print("❌ Porta 5000 está livre - web server não está rodando")
            return False

    except Exception as e:
        print(f"❌ Erro ao verificar porta: {e}")
        return False

    return True


def verificar_dados_treinamento():
    """Verifica dados de treinamento gerados"""
    print("\n📚 VERIFICANDO DADOS DE TREINAMENTO...")
    training_dir = "data/learning/training_data"

    if not os.path.exists(training_dir):
        print("❌ Diretório de treinamento não existe")
        return False

    files = [f for f in os.listdir(training_dir) if f.endswith(".json")]
    print(f"📁 Total de arquivos de treinamento: {len(files)}")

    if files:
        print("✅ Arquivos encontrados:")
        for f in files[-3:]:  # últimos 3
            print(f"  • {f}")

        # Verificar último arquivo
        latest_file = max([os.path.join(training_dir, f)
                           for f in files], key=os.path.getmtime)

        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ Último arquivo válido: {os.path.basename(latest_file)}")
            print(
                f"   📊 Exemplos: {data.get('metadata', {}).get('total_examples', 'N/A')}"
            )
        except Exception as e:
            print(f"❌ Erro no último arquivo: {e}")

    return len(files) > 0


def testar_websocket():
    """Testa conectividade WebSocket"""
    print("\n🔌 VERIFICANDO WEBSOCKET...")
    try:
        import websockets
        import asyncio

        async def test_ws():
            try:
                async with websockets.connect("ws://localhost:5000/ws") as websocket:
                    print("✅ WebSocket conectado com sucesso")
                    await websocket.send(json.dumps({"test": "connection"}))
                    response = await websocket.recv()
                    print(f"✅ WebSocket responde: {response[:50]}...")
                    return True
            except Exception as e:
                print(f"❌ Erro WebSocket: {e}")
                return False

        return asyncio.run(test_ws())

    except ImportError:
        print("⚠️  Biblioteca websockets não disponível para teste completo")
        print("   WebSocket pode estar funcionando mesmo assim")
        return None


def abrir_dashboard():
    """Abre o dashboard no navegador"""
    print("\n🌐 ABRINDO DASHBOARD...")
    try:
        webbrowser.open("http://localhost:5000")
        print("✅ Navegador aberto automaticamente")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")
        print("   Acesse manualmente: http://localhost:5000")


def iniciar_web_server():
    """Inicia o web server se não estiver rodando"""
    print("\n🚀 TENTANDO INICIAR WEB SERVER...")
    try:
        import uvicorn
        import threading

        def run_server():
            config = uvicorn.Config(
                "web.web_server:app",
                host="localhost",
                port=5000,
                log_level="warning")
            server = uvicorn.Server(config)
            asyncio.run(server.serve())

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print("✅ Web server iniciado em background")
        return True

    except Exception as e:
        print(f"❌ Erro ao iniciar web server: {e}")
        return False


def main():
    """Função principal de diagnóstico"""
    print("🔍 JARVIS 5.0 - DIAGNÓSTICO COMPLETO")
    print("=" * 50)

    # Verificações
    web_ok = verificar_web_server()
    dados_ok = verificar_dados_treinamento()
    ws_ok = testar_websocket()

    print("\n" + "=" * 50)
    print("📋 RESUMO DO DIAGNÓSTICO:")

    if web_ok:
        print("✅ Web Server: Funcionando")
    else:
        print("❌ Web Server: Problema detectado")
        if iniciar_web_server():
            print("✅ Web Server: Iniciado com sucesso")

    if dados_ok:
        print("✅ Dados de Treinamento: OK")
    else:
        print("❌ Dados de Treinamento: Problema")

    if ws_ok is True:
        print("✅ WebSocket: Funcionando")
    elif ws_ok is False:
        print("❌ WebSocket: Problema")
    else:
        print("⚠️  WebSocket: Status desconhecido")

    print("\n💡 INSTRUÇÕES:")
    print("1. Acesse: http://localhost:5000")
    print("2. Aguarde alguns segundos para carregar")
    print("3. Deve aparecer interface cyberpunk com logs")
    print("4. Se não funcionar, recarregue a página (F5)")

    # Abrir navegador
    abrir_dashboard()

    print("\n⏸️  Pressione Enter para continuar...")
    input()


if __name__ == "__main__":
    main()
