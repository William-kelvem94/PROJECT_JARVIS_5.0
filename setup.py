#!/usr/bin/env python3
"""
Setup script para JARVIS 5.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# Ler requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding='utf-8').strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="jarvis-assistant",
    version="5.0.0",
    author="JARVIS Team",
    author_email="jarvis@example.com",
    description="Assistente de voz inteligente com reconhecimento e síntese de fala natural",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jarvis-team/jarvis-5.0",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "audio": [
            "pyaudio>=0.2.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "jarvis=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jarvis": ["*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
)
