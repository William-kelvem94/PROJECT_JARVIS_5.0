#!/usr/bin/env python3
"""
Jarvis 5.0 - Launcher Profissional
Sistema de inicialização automática e inteligente
"""

import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_launcher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProfessionalLauncher:
    """Launcher profissional para o Jarvis 5.0"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        self.python_exe = self._find_python()
        self.is_admin = self._check_admin()

        print("Jarvis 5.0 - Launcher Profissional")
        print("=" * 60)

    def _find_python(self) -> str:
        """Encontra o executável Python mais adequado"""
        # Tentar python3/python primeiro
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    logger.info(f"Python encontrado via comando: {cmd}")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        # Caminhos específicos do Windows
        if self.system == 'windows':
            program_files_paths = [
                r"C:\Program Files\Python311\python.exe",
                r"C:\Program Files\Python310\python.exe",
                r"C:\Python311\python.exe",
                r"C:\Python310\python.exe",
            ]

            for path in program_files_paths:
                if Path(path).exists():
                    logger.info(f"Python encontrado em: {path}")
                    return path

        logger.error("Python não encontrado")
        return None

    def _check_admin(self) -> bool:
        """Verifica se está rodando como administrador"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def check_system_requirements(self) -> dict:
        """Verifica requisitos do sistema"""
        requirements = {
            'python': {'status': False, 'message': 'Python 3.9+ não encontrado'},
            'pip': {'status': False, 'message': 'Pip não encontrado'},
            'tkinter': {'status': False, 'message': 'Tkinter não encontrado'},
            'dependencies': {'status': False, 'message': 'Dependências não instaladas'}
        }

        # Verificar Python
        if self.python_exe:
            try:
                result = subprocess.run([self.python_exe, '--version'],
                                      capture_output=True, text=True, timeout=5)
                if 'Python 3' in result.stdout:
                    version = result.stdout.strip().split()[1]
                    major, minor = map(int, version.split('.')[:2])
                    if major >= 3 and minor >= 9:
                        requirements['python']['status'] = True
                        requirements['python']['message'] = f'Python {version} OK'
                    else:
                        requirements['python']['message'] = f'Python {version} - requer 3.9+'
            except Exception as e:
                requirements['python']['message'] = f'Erro ao verificar Python: {e}'

        # Verificar Pip
        if self.python_exe:
            try:
                result = subprocess.run([self.python_exe, '-m', 'pip', '--version'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    requirements['pip']['status'] = True
                    requirements['pip']['message'] = 'Pip OK'
            except Exception as e:
                requirements['pip']['message'] = f'Erro ao verificar Pip: {e}'

        # Verificar Tkinter
        if self.python_exe:
            try:
                result = subprocess.run([self.python_exe, '-c', 'import tkinter'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    requirements['tkinter']['status'] = True
                    requirements['tkinter']['message'] = 'Tkinter OK'
                else:
                    requirements['tkinter']['message'] = 'Tkinter não encontrado'
            except Exception as e:
                requirements['tkinter']['message'] = f'Erro ao verificar Tkinter: {e}'

        # Verificar dependências
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            try:
                # Tentar importar bibliotecas essenciais
                essential_libs = ['PIL', 'cv2', 'numpy', 'sqlalchemy', 'pytesseract', 'customtkinter']
                all_installed = True

                for lib in essential_libs:
                    try:
                        result = subprocess.run([self.python_exe, '-c', f'import {lib}'],
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode != 0:
                            all_installed = False
                            break
                    except:
                        all_installed = False
                        break

                if all_installed:
                    requirements['dependencies']['status'] = True
                    requirements['dependencies']['message'] = 'Dependências OK'
                else:
                    requirements['dependencies']['message'] = 'Dependências não instaladas'
            except Exception as e:
                requirements['dependencies']['message'] = f'Erro ao verificar dependências: {e}'
        else:
            requirements['dependencies']['message'] = 'Arquivo requirements.txt não encontrado'

        return requirements

    def install_dependencies(self) -> bool:
        """Instala dependências"""
        if not self.python_exe:
            print("Python nao encontrado. Instale Python primeiro.")
            return False

        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            print("Arquivo requirements.txt nao encontrado.")
            return False

        print("Instalando dependencias...")
        try:
            result = subprocess.run([self.python_exe, '-m', 'pip', 'install', '-r', str(requirements_file)],
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("Dependencias instaladas com sucesso!")
                return True
            else:
                print(f"Erro na instalacao: {result.stderr}")
                return False
        except Exception as e:
            print(f"Erro na instalacao: {e}")
            return False

    def run_application(self) -> bool:
        """Executa a aplicação principal"""
        if not self.python_exe:
            print("Python nao encontrado.")
            return False

        main_file = self.project_root / 'main.py'
        if not main_file.exists():
            print("Arquivo main.py nao encontrado.")
            return False

        print("Iniciando aplicacao...")
        print()

        try:
            result = subprocess.run([self.python_exe, str(main_file)])
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\nAplicacao interrompida pelo usuario.")
            return True
        except Exception as e:
            print(f"Erro ao executar aplicacao: {e}")
            return False

    def run_automatic_mode(self):
        """Executa modo automático inteligente"""
        print("\nMODO AUTOMATICO - VERIFICACAO INTELIGENTE")
        print("=" * 60)

        print("Analisando sistema...")
        requirements = self.check_system_requirements()

        system_ok = all(info['status'] for info in requirements.values())

        if system_ok:
            print("Sistema totalmente configurado!")
            print("Iniciando aplicacao automaticamente...")
            self.run_application()
            return

        print("Detectados problemas no sistema:")

        missing_deps = not requirements['dependencies']['status']

        if missing_deps:
            print("Dependencias nao instaladas!")
            print("Instalando automaticamente...")
            install_result = self.install_dependencies()

            if install_result:
                print("Dependencias instaladas!")
                print("Iniciando aplicacao...")
                self.run_application()
            else:
                print("Falha na instalacao das dependencias")

def main():
    """Função principal"""
    try:
        launcher = ProfessionalLauncher()

        # Modo automático por padrão
        launcher.run_automatic_mode()

    except KeyboardInterrupt:
        print("\nLauncher interrompido pelo usuario.")
    except Exception as e:
        logger.error(f"Erro fatal no launcher: {e}")
        print(f"Erro fatal: {e}")
        print("Verifique o arquivo launcher.log para detalhes.")
        sys.exit(1)

if __name__ == '__main__':
    # Branding Update
    print("Jarvis 5.0 - Inicializando...")
    main()
