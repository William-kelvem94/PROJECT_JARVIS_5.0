import subprocess
import time
import sys
import os
import shutil
import urllib.request
import tempfile
import logging

# Configuração do Logger para o Launcher
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LAUNCHER")

EXIT_CODE_REBIRTH = 777
OLLAMA_SERVER_URL = "http://localhost:11434"
OLLAMA_INSTALLER_URL = "https://ollama.com/download/OllamaSetup.exe"

def ensure_ollama_installed():
    """Verifica se Ollama está instalado, caso contrário instala automaticamente."""
    if shutil.which('ollama'):
        logger.info("✅ [INFRA] Ollama detectado no sistema.")
        return True

    logger.warning("⚠️ [INFRA] Ollama não detectado. Iniciando Protocolo de Instalação Automática...")
    
    try:
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "OllamaSetup.exe")
        
        logger.info(f"📥 Baixando instalador oficial de: {OLLAMA_INSTALLER_URL}")
        
        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                percent = (block_num * block_size * 100) / total_size
                if block_num % 100 == 0:
                    sys.stdout.write(f"\rProgresso: {percent:.1f}%")
                    sys.stdout.flush()

        urllib.request.urlretrieve(OLLAMA_INSTALLER_URL, installer_path, report_progress)
        print("\rProgresso: 100.0%")
        
        logger.info("🚀 Executando instalador... Por favor, siga as instruções na tela.")
        # Executa o instalador e aguarda
        install_process = subprocess.Popen(installer_path, shell=True)
        install_process.wait()
        
        # Pequena pausa para o SO registrar o novo binário no PATH
        time.sleep(5)
        
        logger.info("🔄 Atualizando variáveis de ambiente para a sessão atual...")
        
        # Caminho padrão do Ollama no Windows
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        ollama_path = os.path.join(local_app_data, 'Programs', 'Ollama')
        
        if os.path.exists(os.path.join(ollama_path, 'ollama.exe')):
            # Adiciona ao PATH da sessão atual para que o shutil.which encontre imediatamente
            os.environ["PATH"] += os.pathsep + ollama_path
            logger.info(f"✅ Caminho do Ollama injetado no PATH: {ollama_path}")
        else:
            logger.warning("⚠️ Caminho padrão de instalação não encontrado. O PATH pode estar desatualizado.")

        # Agora faz a verificação final
        if shutil.which('ollama'):
            logger.info("✅ [INFRA] Instalação concluída e PATH atualizado.")
            return True
        else:
            logger.error("❌ [ERRO] Falha na verificação pós-instalação. O comando 'ollama' ainda não foi encontrado.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ [ERRO CRÍTICO] Falha no protocolo de instalação: {e}")
        sys.exit(1)

def ensure_ollama_running():
    """Garante que o servidor Ollama está ativo, iniciando-o de forma invisível se necessário."""
    try:
        urllib.request.urlopen(OLLAMA_SERVER_URL, timeout=2)
        logger.info("✅ [INFRA] Servidor Neural Online.")
    except Exception:
        logger.warning("⚠️ [INFRA] Servidor Neural Offline. Inicializando motor local...")
        
        try:
            # Usar creationflags para ocultar a janela no Windows
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
                
            subprocess.Popen(["ollama", "serve"], creationflags=creationflags)
            
            # Health Check loop (15 segundos)
            logger.info("⏳ Aguardando ativação do motor (Health Check)...")
            start_time = time.time()
            while time.time() - start_time < 15:
                try:
                    urllib.request.urlopen(OLLAMA_SERVER_URL, timeout=1)
                    logger.info("🚀 [INFRA] Motor Neural ativado e pronto.")
                    return True
                except:
                    time.sleep(1)
            
            logger.error("❌ [ERRO] O servidor Ollama demorou demais para responder.")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"❌ [ERRO CRÍTICO] Falha ao iniciar Ollama: {e}")
            sys.exit(1)

def main():
    print("\n" + "="*80)
    print("🔥 [LAUNCHER] PROTOCOLO JARVIS DEMOCRÁTICO SINGULARITY v5.0")
    print("="*80)
    print(f"💎 Ambiente: {sys.executable}")
    print(f"🌐 Modo: DEMOCRÁTICO - Rede Inteligente")
    print(f"🔒 Identificação: Microsoft Account + Biometric")
    print(f"☁️ Sincronização: Google Drive Estruturado")
    print("="*80)
    
    # Validação de Infraestrutura
    ensure_ollama_installed()
    ensure_ollama_running()
    
    # ========================================================================
    # NOVO: PRÉ-INICIALIZAÇÃO DEMOCRÁTICA
    # ========================================================================
    print("\n🔥 [DEMOCRÁTICO] Inicializando Sistema de Poder Total...")
    
    try:
        # Detectar Microsoft Account e dispositivo
        print("🆔 [IDENT] Detectando conta Microsoft...")
        result = subprocess.run([
            sys.executable, "-c", 
            "from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier; "
            "import sys; "
            "mi = MicrosoftDeviceIdentifier('./data'); "
            "success = mi.initialize(); "
            "print(f'ACCOUNT:{mi.microsoft_account.account_email if mi.microsoft_account else \"None\"}'); "
            "print(f'DEVICE:{mi.device_fingerprint.device_id if mi.device_fingerprint else \"None\"}'); "
            "sys.exit(0 if success else 1)"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            account_line = next((line for line in lines if line.startswith('ACCOUNT:')), None)
            device_line = next((line for line in lines if line.startswith('DEVICE:')), None)
            
            if account_line and device_line:
                account = account_line.split(':', 1)[1]
                device = device_line.split(':', 1)[1]
                
                if account != "None" and device != "None":
                    print(f"   ✅ Conta: {account}")
                    print(f"   ✅ Dispositivo: {device[:16]}...")
                else:
                    print("   ⚠️ Identificação parcial - continuando...")
            else:
                print("   ⚠️ Resposta inesperada - continuando...")
        else:
            print("   ⚠️ Falha na detecção - continuando sem identificação...")
        
    except subprocess.TimeoutExpired:
        print("   ⚠️ Timeout na identificação - continuando...")
    except Exception as e:
        print(f"   ⚠️ Erro na identificação: {e} - continuando...")
    
    # Verificar Google Drive
    print("☁️ [DRIVE] Verificando integração Google Drive...")
    try:
        import os
        from pathlib import Path
        
        # Caminhos comuns do Google Drive
        drive_paths = [
            Path.home() / "Google Drive",
            Path("C:") / "Users" / os.getenv("USERNAME", "") / "Google Drive"
        ]
        
        drive_found = False
        for path in drive_paths:
            if path.exists():
                print(f"   ✅ Google Drive detectado: {path}")
                drive_found = True
                break
        
        if not drive_found:
            print("   ⚠️ Google Drive não detectado - funcionalidade limitada")
        
    except Exception as e:
        print(f"   ⚠️ Erro verificando Drive: {e}")
    
    print("\n🚀 [SISTEMA] Iniciando Arquitetura Democrática...")
    
    while True:
        try:
            # Roda o main.py no ambiente atual com args democráticos
            args = [sys.executable, "main.py"]
            
            # Adicionar flags democráticos
            if "--democratic" not in sys.argv:
                args.append("--democratic")
            
            process = subprocess.Popen(args)
            exit_code = process.wait()
            
            if exit_code == EXIT_CODE_REBIRTH:
                print("\n🧬 [EVOLUÇÃO] Atualização democrática detectada. Reiniciando Matriz...")
                time.sleep(2)
                continue 
            elif exit_code == 0:
                print("🛑 [SISTEMA] Sistema democrático encerrado normalmente.")
                break
            else:
                print(f"⚠️ [AVISO] O JARVIS democrático encerrou com código {exit_code}. Reiniciando em 5s...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 [SISTEMA] Interrupção manual detectada. Launcher democrático desligando...")
            break
        except Exception as e:
            logger.error(f"❌ [ERRO] Falha no loop de execução democrática: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
