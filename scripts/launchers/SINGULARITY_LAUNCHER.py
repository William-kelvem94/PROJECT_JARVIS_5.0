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

# Carregar configuração externalizada
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    from utils.env_manager import get_config
    config = get_config()
    OLLAMA_SERVER_URL = config.ollama_url
    logger.info(f"[OK] [CONFIG] URL Ollama carregada: {OLLAMA_SERVER_URL}")
except Exception as e:
    logger.warning(f"[WARN] [CONFIG] Erro ao carregar configuracao, usando padrao: {e}")
    OLLAMA_SERVER_URL = "http://localhost:11434"

OLLAMA_INSTALLER_URL = "https://ollama.com/download/OllamaSetup.exe"

# Ajustar CWD para o root do projeto se disparado de dentro de /scripts/launchers
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if os.path.exists(os.path.join(PROJECT_ROOT, "main.py")):
    os.chdir(PROJECT_ROOT)
    logger.info(f"📂 [INFRA] Diretório de trabalho ajustado para: {PROJECT_ROOT}")

def ensure_ollama_installed():
<<<<<<< Updated upstream
    """Verifica se Ollama está instalado, caso contrário instala automaticamente."""
    if shutil.which('ollama'):
=======
    """
    Verifica se Ollama está instalado, caso contrário instala automaticamente.
    """
    if shutil.which("ollama"):
>>>>>>> Stashed changes
        logger.info("[OK] [INFRA] Ollama detectado no sistema.")
        return True

    logger.warning("[WARN] [INFRA] Ollama nao detectado. Iniciando Protocolo de Instalacao Automatica...")
    
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
<<<<<<< Updated upstream
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        ollama_path = os.path.join(local_app_data, 'Programs', 'Ollama')
        
        if os.path.exists(os.path.join(ollama_path, 'ollama.exe')):
            # Adiciona ao PATH da sessão atual para que o shutil.which encontre imediatamente
=======
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        ollama_path = os.path.join(local_app_data, "Programs", "Ollama")

        if os.path.exists(os.path.join(ollama_path, "ollama.exe")):
            # Adiciona ao PATH da sessão atual para que o shutil.which encontre
            # imediatamente
>>>>>>> Stashed changes
            os.environ["PATH"] += os.pathsep + ollama_path
            logger.info(f"✅ Caminho do Ollama injetado no PATH: {ollama_path}")
        else:
            logger.warning("⚠️ Caminho padrão de instalação não encontrado. O PATH pode estar desatualizado.")

        # Agora faz a verificação final
        if shutil.which('ollama'):
            logger.info("[OK] [INFRA] Instalacao concluida e PATH atualizado.")
            return True
        else:
            logger.error("[ERR] [ERRO] Falha na verificacao pos-instalacao. O comando 'ollama' ainda nao foi encontrado.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"[ERR] [ERRO CRITICO] Falha no protocolo de instalacao: {e}")
        sys.exit(1)

<<<<<<< Updated upstream
=======

"""
Garante que o servidor Ollama está ativo, iniciando-o de forma invisível se necessário.
"""


>>>>>>> Stashed changes
def ensure_ollama_running():
    """
    Garante que o servidor Ollama está ativo, iniciando-o de forma invisível se necessário.
    """
    try:
        urllib.request.urlopen(OLLAMA_SERVER_URL, timeout=2)
        logger.info("[OK] [INFRA] Servidor Neural Online.")
    except Exception:
        logger.warning("[WARN] [INFRA] Servidor Neural Offline. Inicializando motor local...")
        
        try:
            # Usar creationflags para ocultar a janela no Windows
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
                
            subprocess.Popen(["ollama", "serve"], creationflags=creationflags)
            
            # Health Check loop (15 segundos)
            logger.info("[WAIT] Aguardando ativacao do motor (Health Check)...")
            start_time = time.time()
            while time.time() - start_time < 15:
                try:
                    urllib.request.urlopen(OLLAMA_SERVER_URL, timeout=1)
                    logger.info("[OK] [INFRA] Motor Neural ativado e pronto.")
                    return True
                except:
                    time.sleep(1)
            
            logger.error("[ERR] [ERRO] O servidor Ollama demorou demais para responder.")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"[ERR] [ERRO CRITICO] Falha ao iniciar Ollama: {e}")
            sys.exit(1)

def main():
    print("\n" + "="*80)
    print("✨ [LAUNCHER] PROTOCOLO JARVIS STARK 2.0 SINGULARITY v5.0")
    print("="*80)
    print(f"💎 Ambiente: {sys.executable}")
    print(f"🌐 Modo: Hibrido (Local + Elite Search)")
    print(f"🔒 Identificação: Biometric + Identity Guard")
    print(f"🚀 Status: Tronco Encefalico Ativo")
    print("="*80)

    # ========================================================================
    # FIX: Configurar encoding UTF-8 para evitar erros de codificação
    # ========================================================================
    import locale
    import os

    # Forçar UTF-8 no ambiente
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    # Tentar definir locale para UTF-8
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            pass  # Usar locale padrão se UTF-8 não estiver disponível

    print(f"🔤 Encoding configurado: {locale.getpreferredencoding()}")

    # Validação de Infraestrutura
    ensure_ollama_installed()
    ensure_ollama_running()
    
    # ========================================================================
    # PRÉ-INICIALIZAÇÃO STARK
    # ========================================================================
    print("\n✨ [STARK] Inicializando Sequencia de Boot Stark 2.0...")
    try:
        # Detectar Microsoft Account e dispositivo (com timeout reduzido)
        print("🆔 [IDENT] Verificando Identidade Stark...")
        result = subprocess.run([
            sys.executable, "-c",
            "from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier; "
            "import sys; "
            "mi = MicrosoftDeviceIdentifier('./data'); "
            "success = mi.initialize(); "
            "print(f'ACCOUNT:{mi.microsoft_account.account_email if mi.microsoft_account else \"None\"}'); "
            "print(f'DEVICE:{mi.device_fingerprint.device_id if mi.device_fingerprint else \"None\"}'); "
            "sys.exit(0 if success else 1)"
        ], capture_output=True, text=False, timeout=10)  # Timeout reduzido e text=False para evitar crash

        if result.returncode == 0:
            stdout_text = result.stdout.decode('utf-8', errors='replace')
            lines = stdout_text.strip().split('\n')
            account_line = next((line for line in lines if line.startswith('ACCOUNT:')), None)
            device_line = next((line for line in lines if line.startswith('DEVICE:')), None)

            if account_line and device_line:
                account = account_line.split(':', 1)[1]
                device = device_line.split(':', 1)[1]

                if account != "None" and device != "None":
                    print(f"   [OK] Conta: {account}")
                    print(f"   [OK] Dispositivo: {device[:16]}...")
                else:
                    print(f"   [WARN] Identificacao parcial - continuando...")
            else:
                print(f"   [WARN] Resposta inesperada - continuando...")
        else:
            print(f"   [WARN] Falha na deteccao - continuando sem identificacao...")

    except subprocess.TimeoutExpired:
        print("   [WARN] Timeout na identificacao - pulando para inicializacao rapida...")
    except Exception as e:
        print(f"   [WARN] Erro na identificacao: {e} - pulando para inicializacao rapida...")

    print(">> [LAUNCHER] Indo direto para inicializacao do JARVIS...")

    # Configurar ambiente para main.py
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    env['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

    # Executar main.py diretamente
    args = [sys.executable, "main.py"]

    print("++ [LAUNCHER] Inicializando JARVIS completo...")
    result = subprocess.run(args, env=env)

    # Verificar resultado
    exit_code = result.returncode

    if exit_code == 123: # Código personalizado para Rebirth se necessário
        print("\n[*] [EVOLUCAO] Atualizacao Stark detectada. Reiniciando Matriz...")
        time.sleep(2)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    elif exit_code == 0:
        print("[!] [SISTEMA] JARVIS encerrado normalmente.")
    else:
        print(f"[WARN] [AVISO] JARVIS encerrou com codigo {exit_code}. Verifique os logs.")
        print("\n" + "="*80)
        print("++ [DIAGNOSTICO] POSSIVEIS CAUSAS E SOLUCOES:")
        print("="*80)
        print("1. [ERR] DEPENDENCIAS PROBLEMATICAS:")
        print("   * PyTorch/Torchvision com conflitos de versao")
        print("   * Transformers/Faster-Whisper com encoding UTF-8")
        print("   * Conflitos entre bibliotecas ML")
        print()
        print("2. [FIX] SOLUCOES RECOMENDADAS:")
        print("   • Execute: pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
        print("   • Execute: pip install --upgrade transformers faster-whisper")
        print("   • Execute: pip install --upgrade --force-reinstall torch")
        print("   • Verifique se há múltiplas versões do Python/PyTorch")
        print()
        print("3. [SCAN] DIAGNOSTICO DETALHADO:")
        print("   * Execute: python scripts/install/dependency_doctor.py")
        print("   * Execute: python scripts/install/validate_environment.py")
        print("   * Execute: python -c \"import torch; print('Torch OK:', torch.__version__)\"")
        print()
        print("4. >> SOLUCAO TEMPORARIA:")
        print("   * Use o JARVIS Lite: python main_lite.py")
        print("   * Funciona sem dependencias pesadas de ML")
        print("="*80)
        input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
