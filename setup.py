#!/usr/bin/env python3
"""
Setup script para o Leitor de Tela Inteligente
Permite instalação como pacote Python e criação de executáveis
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages
import setuptools

# Diretório do projeto
PROJECT_DIR = Path(__file__).parent

# Metadados da aplicação
APP_NAME = "Jarvis 5.0"
APP_VERSION = "5.0.0"
APP_DESCRIPTION = "Assistente Virtual Avançado com Visão, Audição e Aprendizado Evolutivo"
APP_AUTHOR = "Desenvolvedor"
APP_AUTHOR_EMAIL = "contato@exemplo.com"
APP_URL = "https://github.com/username/leitor-tela"
APP_LICENSE = "MIT"

# Leitura do README
def read_readme():
    """Lê o arquivo README.md se existir"""
    readme_path = PROJECT_DIR / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            pass
    return APP_DESCRIPTION

# Leitura das dependências
def read_requirements():
    """Lê as dependências do requirements.txt"""
    requirements_path = PROJECT_DIR / "requirements.txt"
    if requirements_path.exists():
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                # Filtrar linhas vazias e comentários
                lines = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                return lines
        except Exception:
            pass

    # Dependências mínimas se requirements.txt não existir
    return [
        'Pillow>=9.0.0',
        'mss>=6.1.0',
        'pyautogui>=0.9.53',
        'SQLAlchemy>=1.4.0',
        'customtkinter>=5.1.3',
        'pytesseract>=0.3.10',
        'easyocr>=1.7.0',
        'opencv-python>=4.7.0',
        'pandas>=1.5.0',
        'numpy>=1.24.0',
        'spacy>=3.5.0',
        'pystray>=0.19.4'
    ]

# Configuração para PyInstaller (opcional)
def get_pyinstaller_data_files():
    """Retorna arquivos de dados para PyInstaller"""
    data_files = []

    # Incluir modelos do spaCy se existirem
    spacy_models_dir = PROJECT_DIR / "src" / "data" / "models"
    if spacy_models_dir.exists():
        for model_dir in spacy_models_dir.glob("*"):
            if model_dir.is_dir():
                data_files.append((str(model_dir), str(model_dir.relative_to(PROJECT_DIR))))

    return data_files

# Configuração do setup
setup(
    name=APP_NAME.lower().replace(' ', '-'),
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author=APP_AUTHOR,
    author_email=APP_AUTHOR_EMAIL,
    url=APP_URL,
    license=APP_LICENSE,

    # Classificação do projeto
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Text Processing :: Linguistic",
    ],

    # Palavras-chave
    keywords=[
        "screen capture", "ocr", "data extraction", "computer vision",
        "automation", "desktop application", "intelligent processing",
        "portuguese", "brazilian portuguese"
    ],

    # Pacotes Python
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Ponto de entrada principal
    entry_points={
        "console_scripts": [
            "leitor-tela=main:main",
            "leitor_tela=main:main",
        ],
        "gui_scripts": [
            "leitor-tela-gui=main:main",
        ]
    },

    # Dependências
    install_requires=read_requirements(),

    # Dependências extras
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "gpu": [
            "torch>=1.13.0",
            "torchvision>=0.14.0",
        ],
        "full": [
            "torch>=1.13.0",
            "torchvision>=0.14.0",
            "transformers>=4.21.0",
            "accelerate>=0.20.0",
            "huggingface-hub>=0.15.0",
        ]
    },

    # Dependências do sistema (para diferentes plataformas)
    python_requires=">=3.9",

    # Arquivos de dados
    include_package_data=True,
    package_data={
        "": [
            "*.txt",
            "*.md",
            "*.json",
            "*.yml",
            "*.yaml",
            "data/models/*",
            "config/*",
        ],
    },

    # Arquivos adicionais
    data_files=[
        # Configurações padrão
        ("config", ["config/settings.json"]) if (PROJECT_DIR / "config" / "settings.json").exists() else (),
        # Documentação
        ("docs", ["docs/*"]) if (PROJECT_DIR / "docs").exists() else (),
    ],

    # Scripts executáveis
    scripts=[
        "main.py",
    ],

    # Projetos relacionados
    project_urls={
        "Bug Reports": f"{APP_URL}/issues",
        "Source": APP_URL,
        "Documentation": f"{APP_URL}/wiki",
    },

    # Plataformas suportadas
    platforms=["Windows", "Linux"],

    # Configurações adicionais para desenvolvimento
    zip_safe=False,

    # Opções de instalação
    options={
        "bdist_wheel": {
            "universal": False,
        },
    },
)

# Script personalizado para pós-instalação
def post_install():
    """Executa tarefas após a instalação"""
    try:
        print("\n" + "="*60)
        print("Leitor de Tela Inteligente - Instalação Concluída!")
        print("="*60)

        print("\nPara executar a aplicação:")
        print("  python -m leitor_tela                # Interface gráfica")
        print("  python main.py                       # Interface gráfica")
        print("  leitor-tela                          # Linha de comando (se instalado)")
        print("  leitor-tela capture                  # Captura de tela")
        print("  leitor-tela --help                   # Ver todas as opções")

        print("\nDependências opcionais:")
        print("- Instale o Tesseract OCR para melhor qualidade:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print("- Instale modelos spaCy para português:")
        print("  python -m spacy download pt_core_news_sm")

        print("\nPara desenvolvimento:")
        print("  pip install -e .[dev]                # Dependências de desenvolvimento")
        print("  pytest                               # Executar testes")
        print("  black .                              # Formatar código")

        print("\n" + "="*60)

    except Exception as e:
        print(f"Aviso: Erro no pós-instalação: {e}")

# Executar pós-instalação se for uma instalação
if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] in ["install", "develop"]:
    # Isso será executado após a instalação
    import atexit
    atexit.register(post_install)
