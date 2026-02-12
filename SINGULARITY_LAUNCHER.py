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
    print("\n" + "="*60)
    print("🛡️ [LAUNCHER] PROTOCOLO JARVIS SINGULARITY v5.0")
    print("="*60)
    print(f"💎 Ambiente: {sys.executable}")
    
    # Validação de Infraestrutura
    ensure_ollama_installed()
    ensure_ollama_running()
    
    print("\n🚀 [SISTEMA] Iniciando Arquitetura Fênix...")
    
    while True:
        try:
            # Roda o main.py no ambiente atual
            process = subprocess.Popen([sys.executable, "main.py"])
            exit_code = process.wait()
            
            if exit_code == EXIT_CODE_REBIRTH:
                print("\n🧬 [EVOLUÇÃO] Atualização do núcleo detectada. Reiniciando Matriz...")
                time.sleep(2)
                continue 
            elif exit_code == 0:
                print("🛑 [SISTEMA] Sistema encerrado normalmente.")
                break
            else:
                print(f"⚠️ [AVISO] O JARVIS encerrou com código {exit_code}. Reiniciando em 5s...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 [SISTEMA] Interrupção manual detectada. Launcher desligando...")
            break
        except Exception as e:
            logger.error(f"❌ [ERRO] Falha no loop de execução: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
