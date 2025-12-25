#!/usr/bin/env python3
"""
Script de Instalação Inteligente de Dependências do JARVIS 5.0
Instala dependências baseado no ambiente e capacidades do sistema
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def run_command(command, description=""):
    """Executa comando e trata erros"""
    print(f"[INSTALANDO] {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} - Concluido")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] {description} - Erro: {e}")
        print(f"Saída: {e.stdout}")
        print(f"Erro: {e.stderr}")
        return False


def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERRO] Python 3.8+ eh necessario")
        return False
    
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_basic_dependencies():
    """Instala dependências básicas"""
    print("\n=== Instalando Dependências Básicas ===")
    
    basic_packages = [
        "speechrecognition==3.10.0",
        "pyttsx3==2.90",
        "pyaudio==0.2.13",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "gtts==2.5.1",
        "playsound==1.2.2",
        "pygame==2.5.2",
        "edge-tts==6.1.9",
        "certifi==2023.11.17",
        "tabulate==0.9.0",
        "psutil>=5.9.0",
        "beautifulsoup4>=4.12.0",
        "pillow>=10.0.0"
    ]
    
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"Instalando {package}"):
            print(f"[AVISO] Falha ao instalar {package} - continuando...")


def install_ai_dependencies():
    """Instala dependências de IA"""
    print("\n=== Instalando Dependências de IA ===")
    
    ai_packages = [
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "joblib>=1.3.0"
    ]
    
    for package in ai_packages:
        if not run_command(f"pip install {package}", f"Instalando {package}"):
            print(f"[AVISO] Falha ao instalar {package}")
            return False
    
    # Tentar instalar spaCy
    if run_command("pip install spacy>=3.7.0", "Instalando spaCy"):
        # Baixar modelo português
        run_command("python -m spacy download pt_core_news_sm", "Baixando modelo spaCy português")
        if not Path("~/.local/lib/python*/site-packages/pt_core_news_sm").expanduser().exists():
            run_command("python -m spacy download en_core_web_sm", "Baixando modelo spaCy inglês (fallback)")
    
    # NLTK
    if run_command("pip install nltk>=3.8.1", "Instalando NLTK"):
        run_command("python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\"", 
                   "Baixando dados NLTK")
    
    return True


def install_vision_dependencies():
    """Instala dependências de visão computacional"""
    print("\n=== Instalando Dependências de Visão ===")
    
    # OpenCV
    if not run_command("pip install opencv-python>=4.8.0", "Instalando OpenCV"):
        print("[AVISO] Falha ao instalar OpenCV")
        return False
    
    # MediaPipe
    if not run_command("pip install mediapipe>=0.10.0", "Instalando MediaPipe"):
        print("[AVISO] Falha ao instalar MediaPipe")
    
    # Face Recognition (pode falhar em alguns sistemas)
    if platform.system() == "Windows":
        print("[AVISO] Face Recognition pode precisar de Visual Studio Build Tools no Windows")
    
    run_command("pip install face-recognition>=1.3.0", "Instalando Face Recognition")
    
    return True


def install_deep_learning_dependencies():
    """Instala dependências de deep learning (opcional)"""
    print("\n=== Instalando Dependências de Deep Learning (Opcional) ===")
    
    # PyTorch (CPU version)
    torch_success = run_command(
        "pip install torch>=2.0.0 torchvision>=0.15.0 --index-url https://download.pytorch.org/whl/cpu",
        "Instalando PyTorch (CPU)"
    )
    
    # TensorFlow
    tf_success = run_command("pip install tensorflow>=2.13.0", "Instalando TensorFlow")
    
    # YOLO para detecção de objetos
    run_command("pip install ultralytics>=8.0.0", "Instalando YOLO")
    
    return torch_success or tf_success


def install_windows_dependencies():
    """Instala dependências específicas do Windows"""
    if platform.system() != "Windows":
        return True
    
    print("\n=== Instalando Dependências do Windows ===")
    
    windows_packages = [
        "pywin32>=306",
        "pycaw>=20230407",
        "pyautogui>=0.9.54"
    ]
    
    for package in windows_packages:
        run_command(f"pip install {package}", f"Instalando {package}")
    
    return True


def test_installation():
    """Testa a instalação"""
    print("\n=== Testando Instalação ===")
    
    tests = [
        ("import jarvis", "Pacote JARVIS"),
        ("import numpy", "NumPy"),
        ("import pandas", "Pandas"),
        ("import sklearn", "Scikit-learn"),
        ("import cv2", "OpenCV"),
        ("import mediapipe", "MediaPipe"),
        ("import torch", "PyTorch"),
        ("import spacy", "spaCy")
    ]
    
    success_count = 0
    
    for test_import, name in tests:
        try:
            subprocess.run([sys.executable, "-c", test_import], 
                         check=True, capture_output=True)
            print(f"[OK] {name}")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"[ERRO] {name}")
    
    print(f"\n[RESULTADO] {success_count}/{len(tests)} componentes funcionando")
    
    if success_count >= len(tests) * 0.8:  # 80% de sucesso
        print("[SUCESSO] Instalacao bem-sucedida!")
        return True
    else:
        print("[AVISO] Instalacao parcial - algumas funcionalidades podem estar limitadas")
        return False


def main():
    """Função principal"""
    print("JARVIS 5.0 - Instalador Inteligente de Dependencias")
    print("=" * 60)
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Atualizar pip
    run_command("pip install --upgrade pip", "Atualizando pip")
    
    # Instalar dependências por categoria
    install_basic_dependencies()
    
    ai_success = install_ai_dependencies()
    vision_success = install_vision_dependencies()
    dl_success = install_deep_learning_dependencies()
    windows_success = install_windows_dependencies()
    
    # Testar instalação
    test_success = test_installation()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DA INSTALACAO")
    print("=" * 60)
    
    components = [
        ("Dependências Básicas", True),
        ("Inteligência Artificial", ai_success),
        ("Visão Computacional", vision_success),
        ("Deep Learning", dl_success),
        ("Windows (se aplicável)", windows_success),
        ("Testes", test_success)
    ]
    
    for component, success in components:
        status = "[OK]" if success else "[FALHOU]"
        print(f"{component}: {status}")
    
    print("\nPara executar o JARVIS:")
    print("python main.py")
    
    print("\nPara testar funcionalidades:")
    print("python tests/test_ai_learning.py")
    print("python tests/test_vision_system.py")
    print("python tests/test_conversation.py")
    
    if not test_success:
        print("\n[ATENCAO] Algumas dependencias falharam.")
        print("O JARVIS funcionara em modo limitado.")
        print("Consulte a documentacao para resolver problemas especificos.")


if __name__ == "__main__":
    main()
