#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - INSTALADOR AUTOMÁTICO
Instalação completa do sistema 100% local
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
import urllib.request
import hashlib

class JarvisInstaller:
    """Instalador automático do JARVIS Local"""

    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.jarvis_dir = self.project_root / "jarvis_local"

        print("🚀 JARVIS 5.0 - Instalador Automático")
        print("=" * 50)

    def check_python_version(self):
        """Verificar versão do Python"""
        print("🐍 Verificando Python...")
        version = sys.version_info

        if version < (3, 8):
            print(f"❌ Python {version.major}.{version.minor} - Necessário 3.8+")
            return False

        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True

    def install_system_dependencies(self):
        """Instalar dependências do sistema"""
        print("\n🔧 Instalando dependências do sistema...")

        if self.system == "windows":
            return self._install_windows_deps()
        elif self.system == "linux":
            return self._install_linux_deps()
        elif self.system == "darwin":  # macOS
            return self._install_macos_deps()
        else:
            print(f"❌ Sistema {self.system} não suportado")
            return False

    def _install_windows_deps(self):
        """Instalar dependências Windows"""
        try:
            # Verificar se pip está instalado
            subprocess.run([sys.executable, "-m", "pip", "--version"],
                         capture_output=True, check=True)

            # Instalar pip se necessário
            subprocess.run([sys.executable, "-m", "ensurepip", "--default-pip"],
                         capture_output=True)

            print("✅ Dependências Windows OK")
            return True
        except:
            print("❌ Erro nas dependências Windows")
            return False

    def _install_linux_deps(self):
        """Instalar dependências Linux"""
        try:
            # Verificar se estamos em distro com apt
            result = subprocess.run(["which", "apt"], capture_output=True)
            if result.returncode == 0:
                # Ubuntu/Debian
                deps = [
                    "python3-pip",
                    "python3-dev",
                    "portaudio19-dev",
                    "ffmpeg",
                    "libasound2-dev"
                ]

                print("📦 Instalando dependências Ubuntu/Debian...")
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y"] + deps, check=True)

            print("✅ Dependências Linux OK")
            return True
        except:
            print("❌ Erro nas dependências Linux")
            return False

    def _install_macos_deps(self):
        """Instalar dependências macOS"""
        try:
            # Verificar Homebrew
            result = subprocess.run(["which", "brew"], capture_output=True)
            if result.returncode != 0:
                print("⚠️ Homebrew não encontrado. Instale manualmente: https://brew.sh/")
                return False

            # Instalar dependências via brew
            deps = [
                "portaudio",
                "ffmpeg"
            ]

            print("📦 Instalando dependências macOS...")
            subprocess.run(["brew", "install"] + deps, check=True)

            print("✅ Dependências macOS OK")
            return True
        except:
            print("❌ Erro nas dependências macOS")
            return False

    def install_python_packages(self):
        """Instalar pacotes Python"""
        print("\n🐍 Instalando pacotes Python...")

        requirements_file = self.jarvis_dir / "requirements_local.txt"

        if not requirements_file.exists():
            print(f"❌ Arquivo de requisitos não encontrado: {requirements_file}")
            return False

        try:
            # Atualizar pip
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)

            # Instalar requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)

            print("✅ Pacotes Python instalados")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na instalação Python: {e}")
            return False

    def download_essential_models(self):
        """Baixar modelos essenciais"""
        print("\n📥 Baixando modelos essenciais...")

        try:
            # Importar downloader
            sys.path.insert(0, str(self.jarvis_dir))
            from download_models import ModelDownloader

            downloader = ModelDownloader(str(self.jarvis_dir))

            # Baixar apenas modelos essenciais (não os grandes)
            essential_models = [
                "whisper_base",
                "piper_tts_en",
                "piper_tts_config"
            ]

            success_count = 0
            for model in essential_models:
                if downloader.download_model(model):
                    success_count += 1

            print(f"✅ {success_count}/{len(essential_models)} modelos essenciais baixados")

            if success_count < len(essential_models):
                print("⚠️ Alguns modelos não foram baixados. Você pode baixá-los depois.")

            return True
        except Exception as e:
            print(f"❌ Erro no download de modelos: {e}")
            return False

    def create_default_config(self):
        """Criar configuração padrão"""
        print("\n⚙️ Criando configuração padrão...")

        config_dir = self.jarvis_dir / "config"
        config_file = config_dir / "settings.json"

        config_dir.mkdir(parents=True, exist_ok=True)

        default_config = {
            "system": {
                "name": "JARVIS Local 5.0",
                "version": "5.0.0",
                "privacy_mode": "local_only",
                "install_date": str(Path(__file__).stat().st_mtime)
            },
            "models_dir": "./models",
            "data_dir": "./data",
            "vision": {
                "enabled": True,
                "camera_id": 0,
                "face_recognition": True,
                "object_detection": False,
                "gesture_recognition": True
            },
            "audio": {
                "enabled": True,
                "sample_rate": 16000,
                "whisper_model": "base",
                "piper_voice": "en_US-lessac-medium"
            },
            "nlp": {
                "enabled": False,
                "llm_model": "llama-2-7b-chat.Q4_0.gguf",
                "embedding_model": "local"
            },
            "memory": {
                "enabled": False,
                "vector_db": "chromadb",
                "max_memories": 1000
            },
            "learning": {
                "enabled": False,
                "continuous_learning": True,
                "fine_tuning_enabled": False
            },
            "message_bus": {
                "enabled": False,
                "port": 5555
            }
        }

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            print(f"✅ Configuração criada: {config_file}")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar configuração: {e}")
            return False

    def create_directories(self):
        """Criar estrutura de diretórios"""
        print("\n📁 Criando estrutura de diretórios...")

        directories = [
            self.jarvis_dir / "models",
            self.jarvis_dir / "models/fine_tuned_jarvis",
            self.jarvis_dir / "models/piper_voices",
            self.jarvis_dir / "models/facenet",
            self.jarvis_dir / "data",
            self.jarvis_dir / "data/memory",
            self.jarvis_dir / "data/user_faces",
            self.jarvis_dir / "data/conversation_history",
            self.jarvis_dir / "checkpoints",
            self.jarvis_dir / "config",
            self.jarvis_dir / "logs"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        print("✅ Estrutura de diretórios criada")
        return True

    def run_tests(self):
        """Executar testes básicos"""
        print("\n🧪 Executando testes básicos...")

        try:
            # Testar imports básicos
            import cv2
            import torch
            import speech_recognition as sr
            print("✅ Imports básicos OK")

            # Testar câmera
            try:
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print("✅ Câmera OK")
                    else:
                        print("⚠️ Câmera detectada mas sem imagem")
                    cap.release()
                else:
                    print("⚠️ Câmera não disponível")
            except Exception as e:
                print(f"⚠️ Erro na câmera: {e}")

            # Testar microfone
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microfone OK")
            except Exception as e:
                print(f"⚠️ Erro no microfone: {e}")

            return True
        except Exception as e:
            print(f"❌ Erro nos testes: {e}")
            return False

    def create_desktop_shortcut(self):
        """Criar atalho na área de trabalho"""
        print("\n🔗 Criando atalho na área de trabalho...")

        try:
            if self.system == "windows":
                self._create_windows_shortcut()
            elif self.system == "linux":
                self._create_linux_shortcut()
            elif self.system == "darwin":
                self._create_macos_shortcut()

            print("✅ Atalho criado")
            return True
        except Exception as e:
            print(f"⚠️ Erro ao criar atalho: {e}")
            return False

    def _create_windows_shortcut(self):
        """Criar atalho Windows"""
        try:
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "JARVIS Local.lnk")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.project_root / "start_jarvis_local.py")
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = sys.executable
            shortcut.save()

        except ImportError:
            print("⚠️ winshell não disponível. Atalho não criado.")
        except Exception as e:
            print(f"⚠️ Erro no atalho Windows: {e}")

    def _create_linux_shortcut(self):
        """Criar atalho Linux"""
        try:
            desktop_file = Path.home() / ".local" / "share" / "applications" / "jarvis-local.desktop"

            desktop_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""[Desktop Entry]
Name=JARVIS Local 5.0
Comment=Sistema de IA Local Completo
Exec=python3 {self.project_root}/start_jarvis_local.py --start
Icon=python3
Terminal=true
Type=Application
Categories=Utility;Development;
"""

            with open(desktop_file, 'w') as f:
                f.write(content)

            # Tornar executável
            os.chmod(desktop_file, 0o755)

        except Exception as e:
            print(f"⚠️ Erro no atalho Linux: {e}")

    def _create_macos_shortcut(self):
        """Criar atalho macOS"""
        # macOS usa .app bundles, mais complexo
        print("⚠️ Atalho macOS não implementado ainda")

    def show_completion_message(self):
        """Mostrar mensagem de conclusão"""
        print("\n" + "=" * 60)
        print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1️⃣ Iniciar sistema:")
        print("   python start_jarvis_local.py --start")
        print()
        print("2️⃣ Testar componentes:")
        print("   python start_jarvis_local.py --test")
        print()
        print("3️⃣ Baixar modelos avançados (opcional):")
        print("   python jarvis_local/download_models.py")
        print()
        print("📖 DOCUMENTAÇÃO:")
        print("   jarvis_local/README_LOCAL.md")
        print()
        print("🎮 COMANDOS DISPONÍVEIS:")
        print("   • 'Olá JARVIS'")
        print("   • 'Abrir Chrome'")
        print("   • 'Que horas são?'")
        print("   • 'Sair'")
        print()
        print("🔒 O SISTEMA É 100% LOCAL E PRIVADO!")
        print("=" * 60)

    def run_installation(self):
        """Executar instalação completa"""
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Criar diretórios", self.create_directories),
            ("Instalar dependências sistema", self.install_system_dependencies),
            ("Instalar pacotes Python", self.install_python_packages),
            ("Criar configuração", self.create_default_config),
            ("Baixar modelos essenciais", self.download_essential_models),
            ("Executar testes", self.run_tests),
            ("Criar atalho", self.create_desktop_shortcut)
        ]

        completed_steps = 0

        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if step_func():
                    print(f"✅ {step_name} - OK")
                    completed_steps += 1
                else:
                    print(f"❌ {step_name} - FALHA")
                    break
            except Exception as e:
                print(f"❌ {step_name} - ERRO: {e}")
                break

        if completed_steps == len(steps):
            self.show_completion_message()
            return True
        else:
            print(f"\n❌ Instalação incompleta: {completed_steps}/{len(steps)} passos concluídos")
            print("Tente executar novamente ou verifique os erros acima.")
            return False


def main():
    """Função principal do instalador"""
    try:
        installer = JarvisInstaller()
        success = installer.run_installation()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⚠️ Instalação interrompida pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
