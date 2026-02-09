import sys
import subprocess
import importlib.util
import pkg_resources
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REQUIREMENTS_FILE = "requirements.txt"

def install_package(package):
    """Instala um pacote usando pip"""
    logger.info(f"Instalando {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        logger.info(f"{package} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Falha ao instalar {package}: {e}")
        return False

def check_and_install_requirements():
    """Verifica e instala dependencias faltantes do requirements.txt"""
    if not os.path.exists(REQUIREMENTS_FILE):
        logger.error(f"{REQUIREMENTS_FILE} não encontrado.")
        return

    logger.info("Verificando dependências do sistema...")
    
    with open(REQUIREMENTS_FILE, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    missing_packages = []

    for req in requirements:
        # Extrair nome do pacote (ignorando versões para verificação simples)
        package_name = req.split('==')[0].split('>=')[0].split('<')[0].strip()
        
        # Mapping especial para pacotes com nomes diferentes na importação
        import_name = package_name
        if package_name == "opencv-python": import_name = "cv2"
        elif package_name == "SpeechRecognition": import_name = "speech_recognition"
        elif package_name == "gTTS": import_name = "gtts"
        elif package_name == "pillow": import_name = "PIL"
        elif package_name == "fiona": import_name = "fiona" # Exemplo
        
        # Verificação rápida por importação
        if importlib.util.find_spec(import_name) is None:
            # Tentar verificar via pkg_resources (pip freeze) para ter certeza
            try:
                pkg_resources.get_distribution(package_name)
            except pkg_resources.DistributionNotFound:
                missing_packages.append(req)

    if missing_packages:
        logger.warning(f"Pacotes faltando detectados: {len(missing_packages)}")
        logger.info(f"Lista: {', '.join(missing_packages)}")
        print("\n[AUTO-SETUP] Iniciando instalação automática de dependências faltantes...\n")
        
        # Instalar em lote para ser mais rápido (exceto numpy que precisa de cuidado)
        # Separar numpy do resto
        others = [p for p in missing_packages if 'numpy' not in p]
        numpy_req = next((p for p in missing_packages if 'numpy' in p), None)
        
        if numpy_req:
            install_package(numpy_req)
            
        if others:
            # Tentar instalar tudo de uma vez
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + others)
                logger.info("Todos os pacotes instalados com sucesso!")
            except subprocess.CalledProcessError:
                logger.warning("Instalação em lote falhou. Tentando um por um...")
                for pkg in others:
                    install_package(pkg)
    else:
        logger.info("Todas as dependências parecem estar satisfeitas.")

import os
if __name__ == "__main__":
    check_and_install_requirements()
