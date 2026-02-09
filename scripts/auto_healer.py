"""
🛠️ JARVIS AUTO-HEALER - Sistema de Auto-Reparo Inteligente
Detecta e corrige problemas automaticamente sem interação manual
"""
import sys
import subprocess
import importlib
import os
from pathlib import Path

class AutoHealer:
    """Sistema de auto-reparo para dependências e problemas comuns"""
    
    def __init__(self, project_root=None):
        self.root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.fixed = []
        self.failed = []
        
    def log(self, level, msg):
        """Log com cores"""
        colors = {
            'INFO': '\033[96m',
            'OK': '\033[92m',
            'WARN': '\033[93m',
            'ERROR': '\033[91m',
            'END': '\033[0m'
        }
        print(f"{colors.get(level, '')}{msg}{colors['END']}")
    
    def check_and_fix_pytorch(self):
        """Verifica e corrige problemas com PyTorch"""
        self.log('INFO', '[AUTO-HEAL] Checking PyTorch...')
        
        # Tenta importar
        try:
            import torch
            import torchvision
            # Testa operação básica
            x = torch.tensor([1.0])
            self.log('OK', '  ✅ PyTorch OK')
            return True
        except ImportError:
            self.log('WARN', '  ⚠️  PyTorch missing - installing...')
        except Exception as e:
            self.log('WARN', f'  ⚠️  PyTorch broken ({type(e).__name__}) - reinstalling...')
        
        # Auto-fix: instala PyTorch
        try:
            quick_fix = self.root / "scripts" / "install" / "quick_fix_torch.py"
            if quick_fix.exists():
                subprocess.run([sys.executable, str(quick_fix)], check=True)
                self.fixed.append('torch')
                self.log('OK', '  ✅ PyTorch fixed!')
                return True
            else:
                # Fallback: instalação manual
                self.log('INFO', '  Installing PyTorch (CPU)...')
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    'torch==2.2.2', 'torchvision==0.17.2',
                    '--index-url', 'https://download.pytorch.org/whl/cpu'
                ], check=True, capture_output=True)
                self.fixed.append('torch')
                self.log('OK', '  ✅ PyTorch installed!')
                return True
        except Exception as e:
            self.log('ERROR', f'  ❌ Failed to fix PyTorch: {e}')
            self.failed.append(('torch', str(e)))
            return False
    
    def check_and_fix_package(self, import_name, pip_name):
        """Verifica e corrige um pacote específico"""
        self.log('INFO', f'[AUTO-HEAL] Checking {import_name}...')
        
        try:
            __import__(import_name)
            self.log('OK', f'  ✅ {import_name} OK')
            return True
        except ImportError:
            self.log('WARN', f'  ⚠️  {import_name} missing - installing...')
        except Exception as e:
            self.log('WARN', f'  ⚠️  {import_name} broken - reinstalling...')
        
        # Auto-fix: instala o pacote
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', pip_name
            ], check=True, capture_output=True)
            self.fixed.append(import_name)
            self.log('OK', f'  ✅ {import_name} fixed!')
            return True
        except Exception as e:
            self.log('ERROR', f'  ❌ Failed to fix {import_name}: {e}')
            self.failed.append((import_name, str(e)))
            return False
    
    def check_and_fix_venv(self):
        """Verifica e cria VENV se necessário"""
        venv_python = self.root / "venv" / "Scripts" / "python.exe"
        
        if venv_python.exists():
            self.log('OK', '[AUTO-HEAL] VENV OK')
            return True
        
        self.log('WARN', '[AUTO-HEAL] VENV missing - creating...')
        try:
            subprocess.run([
                'python', '-m', 'venv', str(self.root / 'venv')
            ], check=True)
            self.fixed.append('venv')
            self.log('OK', '  ✅ VENV created!')
            return True
        except Exception as e:
            self.log('ERROR', f'  ❌ Failed to create VENV: {e}')
            self.failed.append(('venv', str(e)))
            return False
    
    def check_and_fix_numpy_version(self):
        """Verifica versão do numpy (deve ser < 2.0)"""
        self.log('INFO', '[AUTO-HEAL] Checking NumPy version...')
        
        try:
            import numpy as np
            version = tuple(map(int, np.__version__.split('.')[:2]))
            
            if version[0] >= 2:
                self.log('WARN', f'  ⚠️  NumPy {np.__version__} incompatible - downgrading...')
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'numpy<2.0'
                ], check=True, capture_output=True)
                self.fixed.append('numpy')
                self.log('OK', '  ✅ NumPy downgraded to compatible version!')
                return True
            else:
                self.log('OK', f'  ✅ NumPy {np.__version__} OK')
                return True
        except Exception as e:
            self.log('ERROR', f'  ❌ NumPy check failed: {e}')
            return False
    
    def auto_heal_all(self):
        """Executa todos os reparos automáticos"""
        self.log('INFO', '\n' + '='*60)
        self.log('INFO', '🛠️  JARVIS AUTO-HEALER - Starting...')
        self.log('INFO', '='*60 + '\n')
        
        # Lista de verificações - Priorizar NumPy Version
        checks = [
            ('numpy_version', self.check_and_fix_numpy_version),
            ('pytorch', self.check_and_fix_pytorch),
            ('PyQt6', lambda: self.check_and_fix_package('PyQt6', 'PyQt6')),
            ('cv2', lambda: self.check_and_fix_package('cv2', 'opencv-python')),
            ('ultralytics', lambda: self.check_and_fix_package('ultralytics', 'ultralytics')),
        ]
        
        success_count = 0
        for name, check_func in checks:
            try:
                if check_func():
                    success_count += 1
            except Exception as e:
                self.log('ERROR', f'[AUTO-HEAL] Unexpected error in {name}: {e}')
        
        # Relatório final
        self.log('INFO', '\n' + '='*60)
        if self.fixed:
            self.log('OK', f'✅ AUTO-HEALER: Fixed {len(self.fixed)} issues:')
            for item in self.fixed:
                print(f'   - {item}')
        
        if self.failed:
            self.log('WARN', f'\n⚠️  AUTO-HEALER: {len(self.failed)} issues need manual attention:')
            for item, error in self.failed:
                print(f'   - {item}: {error[:50]}...')
        
        if not self.fixed and not self.failed:
            self.log('OK', '✅ AUTO-HEALER: System healthy - no repairs needed!')
        
        self.log('INFO', '='*60 + '\n')
        
        return len(self.failed) == 0

def main():
    """Execute auto-healing"""
    healer = AutoHealer()
    success = healer.auto_heal_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
