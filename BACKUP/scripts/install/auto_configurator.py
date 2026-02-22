"""
STARK Auto-Configurator - Sistema de Configuracao Automatica
Resolve problemas comuns do ambiente Windows automaticamente
"""

import os
import sys
import subprocess
import winreg
import ctypes
from pathlib import Path


class AutoConfigurator:
    """Configura automaticamente o ambiente Windows para JARVIS"""

    def __init__(self):
        self.is_admin = self.check_admin()
        self.fixed = []
        self.warnings = []

    def check_admin(self):
        """Verifica se tem privilégios de administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except BaseException:
            return False

    def log(self, level, msg):
        """Log com cores apropriadas para o sistema"""
        import platform

        if platform.system() == "Windows":
            # Windows CMD não suporta ANSI bem, usar texto simples
            prefix = {
                "INFO": "[INFO]",
                "OK": "[OK]",
                "WARN": "[WARN]",
                "ERROR": "[ERROR]",
            }.get(level, f"[{level}]")
            print(f"{prefix} {msg}")
        else:
            # ANSI colors para outros sistemas
            colors = {
                "INFO": "\033[96m",
                "OK": "\033[92m",
                "WARN": "\033[93m",
                "ERROR": "\033[91m",
                "END": "\033[0m",
            }
            print(f"{colors.get(level, '')}{msg}{colors['END']}")

    def install_vcredist(self):
        """Instala Visual C++ Redistributables se necessário"""
        self.log("INFO", "[AUTO-CONFIG] Checking Visual C++ Redistributables...")

        # Verifica se já está instalado
        try:
            key_path = r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.CloseKey(key)
            self.log("OK", "  [OK] Visual C++ already installed")
            return True
        except BaseException:
            pass

        if not self.is_admin:
            self.log("WARN", "  [WARN] Need admin rights to install Visual C++")
            self.log(
                "WARN",
                "  Please manually install: https://aka.ms/vs/17/release/vc_redist.x64.exe",
            )
            self.warnings.append("vcredist")
            return False

        self.log("INFO", "  Installing Visual C++ Redistributables...")
        try:
            # Download e instala
            import urllib.request
            import tempfile

            url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
            temp_file = os.path.join(tempfile.gettempdir(), "vc_redist.x64.exe")

            urllib.request.urlretrieve(url, temp_file)
            subprocess.run([temp_file, "/install", "/quiet", "/norestart"], check=True)
            os.remove(temp_file)

            self.fixed.append("vcredist")
            self.log("OK", "  [OK] Visual C++ installed!")
            return True
        except Exception as e:
            self.log("ERROR", f"  [ERR] Failed to install: {e}")
            self.warnings.append("vcredist")
            return False

    def configure_environment_variables(self):
        """Configura variáveis de ambiente necessárias"""
        self.log("INFO", "[AUTO-CONFIG] Configuring environment variables...")

        env_vars = {
            "KMP_DUPLICATE_LIB_OK": "TRUE",
            "PYTHONUTF8": "1",
            "OMP_NUM_THREADS": "4",  # Otimização para CPU
        }

        for var, value in env_vars.items():
            current = os.environ.get(var)
            if current != value:
                os.environ[var] = value
                self.log("OK", f"  [OK] Set {var}={value}")
                self.fixed.append(f"env_{var}")
            else:
                self.log("OK", f"  [OK] {var} already configured")

        return True

    def add_to_system_path(self, path_str):
        """Adiciona um caminho ao PATH do sistema"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS,
            )
            current_path, _ = winreg.QueryValueEx(key, "PATH")
            if path_str not in current_path:
                new_path = current_path + ";" + path_str
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)
                # Notifica o sistema da mudança
                ctypes.windll.user32.SendMessageW(
                    0xFFFF, 0x001A, 0, 0
                )  # WM_SETTINGCHANGE
                return True
        except Exception as e:
            self.log("WARN", f"  Failed to add to system PATH: {e}")
            return False

    def fix_path_for_ollama(self):
        """Adiciona Ollama ao PATH se instalado mas não encontrado"""
        self.log("INFO", "[AUTO-CONFIG] Checking Ollama in PATH...")

        # Verifica se ollama já está no PATH
        try:
            res = subprocess.run(["where", "ollama"], capture_output=True, text=False)
            if res.returncode == 0:
                self.log("OK", "  [OK] Ollama already in PATH")
                return True
        except BaseException:
            pass

        # Procura instalação padrão
        default_paths = [
            Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Ollama",
            Path(os.environ["USERPROFILE"])
            / "AppData"
            / "Local"
            / "Programs"
            / "Ollama",
        ]

        for path in default_paths:
            if (path / "ollama.exe").exists():
                self.log("INFO", f"  Found Ollama at {path}")
                path_str = str(path)
                if self.add_to_system_path(path_str):
                    os.environ["PATH"] = path_str + os.pathsep + os.environ["PATH"]
                    self.fixed.append("ollama_path")
                    self.log("OK", "  [OK] Added Ollama to system PATH")
                else:
                    self.log("WARN", "  [WARN] Could not add Ollama to system PATH")
                return True

        self.log("WARN", "  [WARN] Ollama not found - will be installed by launcher")
        return False

    def optimize_pip_config(self):
        """Otimiza configuração do pip para instalações mais rápidas"""
        self.log("INFO", "[AUTO-CONFIG] Optimizing pip configuration...")

        pip_config_dir = Path.home() / "pip"
        pip_config_file = pip_config_dir / "pip.ini"

        config_content = """[global]
timeout = 60
retries = 3

[install]
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
"""

        try:
            pip_config_dir.mkdir(exist_ok=True)

            if not pip_config_file.exists():
                with open(pip_config_file, "w") as f:
                    f.write(config_content)
                self.fixed.append("pip_config")
                self.log("OK", "  [OK] Pip configuration optimized")
            else:
                self.log("OK", "  [OK] Pip already configured")
            return True
        except Exception as e:
            self.log("WARN", f"  [WARN] Could not optimize pip config: {e}")
            return False

    def check_python_version(self):
        """Verifica se a versão do Python é compatível"""
        self.log("INFO", "[AUTO-CONFIG] Checking Python version...")

        version = sys.version_info
        if version.major == 3 and 10 <= version.minor <= 12:
            self.log(
                "OK", f"  [OK] Python {version.major}.{version.minor} is compatible"
            )
            return True
        else:
            self.log(
                "WARN",
                f"  [WARN] Python {version.major}.{version.minor} may have compatibility issues",
            )
            self.log("WARN", "  Recommended: Python 3.10, 3.11, or 3.12")
            self.warnings.append("python_version")
            return False

    def disable_windows_defender_for_venv(self):
        """Adiciona VENV às exclusões do Windows Defender (se admin)"""
        if not self.is_admin:
            return False

        self.log("INFO", "[AUTO-CONFIG] Adding VENV to Windows Defender exclusions...")

        project_root = Path(__file__).parent.parent
        venv_path = project_root / "venv"

        try:
            # Primeiro verifica se já está excluído
            check_cmd = f'Get-MpPreference | Select-Object -ExpandProperty ExclusionPath | Where-Object {{$_ -eq "{venv_path}"}}'
            result = subprocess.run(
                ["powershell", "-Command", check_cmd],
                capture_output=True,
                text=False,
                timeout=15,
            )

            stdout_text = result.stdout.decode("utf-8", errors="replace").strip()
            if stdout_text:
                self.log("OK", "  [OK] VENV already excluded from Windows Defender")
                return True

            # Tenta adicionar exclusão
            ps_cmd = f'Add-MpPreference -ExclusionPath "{venv_path}"'
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                check=True,
                capture_output=True,
                text=False,
                timeout=15,
            )
            self.fixed.append("defender_exclusion")
            self.log("OK", "  [OK] VENV excluded from Windows Defender")
            return True

        except subprocess.TimeoutExpired:
            self.log("WARN", "  [WARN] Windows Defender configuration timed out")
            return False
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                self.log(
                    "WARN",
                    "  [WARN] Windows Defender: Access denied or policy restriction",
                )
            else:
                self.log(
                    "WARN", f"  [WARN] Windows Defender error (code {e.returncode})"
                )
            return False
        except Exception as e:
            self.log("WARN", f"  [WARN] Could not configure Defender: {str(e)[:50]}...")
            return False

    def auto_configure_all(self):
        """Executa todas as configurações automáticas"""
        self.log("INFO", "\n" + "=" * 70)
        self.log("INFO", "STARK AUTO-CONFIGURATOR - Starting...")
        self.log("INFO", "=" * 70 + "\n")

        if self.is_admin:
            self.log("OK", "[✓] Running with Administrator privileges\n")
        else:
            self.log(
                "WARN", "[!] Not running as Administrator - some fixes may be limited\n"
            )

        # Lista de configurações
        configs = [
            ("Python Version", self.check_python_version),
            ("Environment Variables", self.configure_environment_variables),
            ("Ollama PATH", self.fix_path_for_ollama),
            ("Pip Config", self.optimize_pip_config),
            ("Visual C++ Redist", self.install_vcredist),
        ]

        if self.is_admin:
            configs.append(("Windows Defender", self.disable_windows_defender_for_venv))

        for name, func in configs:
            try:
                func()
                print()  # Espaço entre checks
            except Exception as e:
                self.log("ERROR", f"[AUTO-CONFIG] Error in {name}: {e}\n")

        # Relatório final
        self.log("INFO", "=" * 70)
        if self.fixed:
            self.log(
                "OK",
                f"[OK] AUTO-CONFIGURATOR: Applied {len(self.fixed)} optimizations:",
            )
            for item in self.fixed:
                print(f"   - {item}")

        if self.warnings:
            self.log("WARN", f"\n[WARN] {len(self.warnings)} items need attention:")
            for item in self.warnings:
                print(f"   - {item}")

            if "vcredist" in self.warnings:
                self.log("WARN", "\n   Please install Visual C++ Redistributables:")
                self.log("WARN", "   https://aka.ms/vs/17/release/vc_redist.x64.exe")

        if not self.fixed and not self.warnings:
            self.log("OK", "[OK] System already optimally configured!")

        self.log("INFO", "=" * 70 + "\n")
        return True


def main():
    """Execute auto-configuration"""
    configurator = AutoConfigurator()
    configurator.auto_configure_all()
    sys.exit(0)


if __name__ == "__main__":
    main()
