"""
🔧 JARVIS Auto-Configurator - Sistema de Configuração Automática
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
        except:
            return False
    
    def log(self, level, msg):
        """Log colorido"""
        colors = {
            'INFO': '\033[96m',
            'OK': '\033[92m',
            'WARN': '\033[93m',
            'ERROR': '\033[91m',
            'END': '\033[0m'
        }
        print(f"{colors.get(level, '')}{msg}{colors['END']}")
    
    def install_vcredist(self):
        """Instala Visual C++ Redistributables se necessário"""
        self.log('INFO', '[AUTO-CONFIG] Checking Visual C++ Redistributables...')
        
        # Verifica se já está instalado
        try:
            key_path = r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.CloseKey(key)
            self.log('OK', '  ✅ Visual C++ already installed')
            return True
        except:
            pass
        
        if not self.is_admin:
            self.log('WARN', '  ⚠️  Need admin rights to install Visual C++')
            self.log('WARN', '  Please manually install: https://aka.ms/vs/17/release/vc_redist.x64.exe')
            self.warnings.append('vcredist')
            return False
        
        self.log('INFO', '  Installing Visual C++ Redistributables...')
        try:
            # Download e instala
            import urllib.request
            import tempfile
            
            url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
            temp_file = os.path.join(tempfile.gettempdir(), "vc_redist.x64.exe")
            
            urllib.request.urlretrieve(url, temp_file)
            subprocess.run([temp_file, '/install', '/quiet', '/norestart'], check=True)
            os.remove(temp_file)
            
            self.fixed.append('vcredist')
            self.log('OK', '  ✅ Visual C++ installed!')
            return True
        except Exception as e:
            self.log('ERROR', f'  ❌ Failed to install: {e}')
            self.warnings.append('vcredist')
            return False
    
    def configure_environment_variables(self):
        """Configura variáveis de ambiente necessárias"""
        self.log('INFO', '[AUTO-CONFIG] Configuring environment variables...')
        
        env_vars = {
            'KMP_DUPLICATE_LIB_OK': 'TRUE',
            'PYTHONUTF8': '1',
            'OMP_NUM_THREADS': '4',  # Otimização para CPU
        }
        
        for var, value in env_vars.items():
            current = os.environ.get(var)
            if current != value:
                os.environ[var] = value
                self.log('OK', f'  ✅ Set {var}={value}')
                self.fixed.append(f'env_{var}')
            else:
                self.log('OK', f'  ✅ {var} already configured')
        
        return True
    
    def fix_path_for_ollama(self):
        """Adiciona Ollama ao PATH se instalado mas não encontrado"""
        self.log('INFO', '[AUTO-CONFIG] Checking Ollama in PATH...')
        
        # Verifica se ollama já está no PATH
        if subprocess.run(['where', 'ollama'], capture_output=True).returncode == 0:
            self.log('OK', '  ✅ Ollama already in PATH')
            return True
        
        # Procura instalação padrão
        default_paths = [
            Path(os.environ['LOCALAPPDATA']) / 'Programs' / 'Ollama',
            Path(os.environ['USERPROFILE']) / 'AppData' / 'Local' / 'Programs' / 'Ollama',
        ]
        
        for path in default_paths:
            if (path / 'ollama.exe').exists():
                self.log('INFO', f'  Found Ollama at {path}')
                os.environ['PATH'] = str(path) + os.pathsep + os.environ['PATH']
                self.fixed.append('ollama_path')
                self.log('OK', '  ✅ Added Ollama to PATH')
                return True
        
        self.log('WARN', '  ⚠️  Ollama not found - will be installed by launcher')
        return False
    
    def optimize_pip_config(self):
        """Otimiza configuração do pip para instalações mais rápidas"""
        self.log('INFO', '[AUTO-CONFIG] Optimizing pip configuration...')
        
        pip_config_dir = Path.home() / 'pip'
        pip_config_file = pip_config_dir / 'pip.ini'
        
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
                with open(pip_config_file, 'w') as f:
                    f.write(config_content)
                self.fixed.append('pip_config')
                self.log('OK', '  ✅ Pip configuration optimized')
            else:
                self.log('OK', '  ✅ Pip already configured')
            return True
        except Exception as e:
            self.log('WARN', f'  ⚠️  Could not optimize pip config: {e}')
            return False
    
    def check_python_version(self):
        """Verifica se a versão do Python é compatível"""
        self.log('INFO', '[AUTO-CONFIG] Checking Python version...')
        
        version = sys.version_info
        if version.major == 3 and 10 <= version.minor <= 12:
            self.log('OK', f'  ✅ Python {version.major}.{version.minor} is compatible')
            return True
        else:
            self.log('WARN', f'  ⚠️  Python {version.major}.{version.minor} may have compatibility issues')
            self.log('WARN', '  Recommended: Python 3.10, 3.11, or 3.12')
            self.warnings.append('python_version')
            return False
    
    def disable_windows_defender_for_venv(self):
        """Adiciona VENV às exclusões do Windows Defender (se admin)"""
        if not self.is_admin:
            return False
        
        self.log('INFO', '[AUTO-CONFIG] Adding VENV to Windows Defender exclusions...')
        
        project_root = Path(__file__).parent.parent.parent
        venv_path = project_root / 'venv'
        
        try:
            # PowerShell command para adicionar exclusão
            ps_cmd = f'Add-MpPreference -ExclusionPath "{venv_path}"'
            subprocess.run(['powershell', '-Command', ps_cmd], 
                         check=True, capture_output=True, timeout=10)
            self.fixed.append('defender_exclusion')
            self.log('OK', '  ✅ VENV excluded from Windows Defender')
            return True
        except Exception as e:
            self.log('WARN', f'  ⚠️  Could not configure Defender: {e}')
            return False
    
    def auto_configure_all(self):
        """Executa todas as configurações automáticas"""
        self.log('INFO', '\n' + '='*70)
        self.log('INFO', '🔧 JARVIS AUTO-CONFIGURATOR - Starting...')
        self.log('INFO', '='*70 + '\n')
        
        if self.is_admin:
            self.log('OK', '[✓] Running with Administrator privileges\n')
        else:
            self.log('WARN', '[!] Not running as Administrator - some fixes may be limited\n')
        
        # Lista de configurações
        configs = [
            ('Python Version', self.check_python_version),
            ('Environment Variables', self.configure_environment_variables),
            ('Ollama PATH', self.fix_path_for_ollama),
            ('Pip Config', self.optimize_pip_config),
            ('Visual C++ Redist', self.install_vcredist),
        ]
        
        if self.is_admin:
            configs.append(('Windows Defender', self.disable_windows_defender_for_venv))
        
        for name, func in configs:
            try:
                func()
                print()  # Espaço entre checks
            except Exception as e:
                self.log('ERROR', f'[AUTO-CONFIG] Error in {name}: {e}\n')
        
        # Relatório final
        self.log('INFO', '='*70)
        if self.fixed:
            self.log('OK', f'✅ AUTO-CONFIGURATOR: Applied {len(self.fixed)} optimizations:')
            for item in self.fixed:
                print(f'   - {item}')
        
        if self.warnings:
            self.log('WARN', f'\n⚠️  {len(self.warnings)} items need attention:')
            for item in self.warnings:
                print(f'   - {item}')
            
            if 'vcredist' in self.warnings:
                self.log('WARN', '\n   Please install Visual C++ Redistributables:')
                self.log('WARN', '   https://aka.ms/vs/17/release/vc_redist.x64.exe')
        
        if not self.fixed and not self.warnings:
            self.log('OK', '✅ System already optimally configured!')
        
        self.log('INFO', '='*70 + '\n')
        return True

def main():
    """Execute auto-configuration"""
    configurator = AutoConfigurator()
    configurator.auto_configure_all()
    sys.exit(0)

if __name__ == "__main__":
    main()
