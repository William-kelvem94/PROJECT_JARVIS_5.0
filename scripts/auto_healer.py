"""
STARK AUTO-HEALER - Sistema de Auto-Reparo Inteligente
Detecta e corrige problemas automaticamente sem interacao manual
"""
import sys
import subprocess
import importlib
import os
from pathlib import Path

class AutoHealer:
    """Sistema de auto-reparo para dependências e problemas comuns"""
    
    def __init__(self, project_root=None):
        self.root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.fixed = []
        self.failed = []
        
    def run_command_safe(self, cmd, capture=True):
        """Executa comando de forma segura com tratamento de encoding"""
        try:
            if capture:
                result = subprocess.run(cmd, check=True, capture_output=True, text=False)
                stdout = ""
                if result.stdout:
                    try:
                        stdout = result.stdout.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            stdout = result.stdout.decode('cp1252', errors='replace')
                        except:
                            stdout = result.stdout.decode('utf-8', errors='replace')
                return stdout
            else:
                return ""
    
    def log(self, level, msg):
        """Log com niveis de gravidade"""
        print(f"[{level}] {msg}")

    def check_and_fix_pytorch(self):
        """Verifica e corrige problemas com PyTorch"""
        self.log('INFO', '[AUTO-HEAL] Checking PyTorch...')
        
        # Tenta importar
        try:
            import torch
            import torchvision
            # Testa operação básica
            x = torch.tensor([1.0])
            self.log('OK', '  [OK] PyTorch OK')
            return True
        except ImportError:
            self.log('WARN', '  [WARN] PyTorch missing - installing...')
        except Exception as e:
            self.log('WARN', f'  [WARN] PyTorch broken ({type(e).__name__}) - reinstalling...')
        
        # Auto-fix: instala PyTorch
        try:
            quick_fix = self.root / "scripts" / "install" / "quick_fix_torch.py"
            if quick_fix.exists():
                self.run_command_safe([sys.executable, str(quick_fix)], capture=False)
                # After PyTorch installation, ensure NumPy is compatible
                self.run_command_safe([sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'numpy==1.26.4'], capture=False)
                self.fixed.append('torch')
                self.log('OK', '  [OK] PyTorch fixed!')
                return True
            else:
                # Fallback: instalação manual
                self.log('INFO', '  Installing PyTorch (CPU)...')
                self.run_command_safe([
                    sys.executable, '-m', 'pip', 'install',
                    'torch==2.4.1+cpu', 'torchvision==0.19.1+cpu',
                    '--index-url', 'https://download.pytorch.org/whl/cpu'
                ], capture=False)
                self.fixed.append('torch')
                self.log('OK', '  [OK] PyTorch installed!')
                return True
        except Exception as e:
            self.log('ERROR', f'  [ERR] Failed to fix PyTorch: {e}')
            self.failed.append(('torch', str(e)))
            return False
    
    def check_and_fix_package(self, import_name, pip_name):
        """Verifica e corrige um pacote específico"""
        self.log('INFO', f'[AUTO-HEAL] Checking {import_name}...')
        
        try:
            __import__(import_name)
            self.log('OK', f'  [OK] {import_name} OK')
            return True
        except ImportError:
            self.log('WARN', f'  [WARN] {import_name} missing - installing...')
        except Exception as e:
            self.log('WARN', f'  [WARN] {import_name} broken - reinstalling...')
        
        # Auto-fix: instala o pacote
        try:
            self.run_command_safe([
                sys.executable, '-m', 'pip', 'install', pip_name
            ], capture=False)
            self.fixed.append(import_name)
            self.log('OK', f'  [OK] {import_name} fixed!')
            return True
        except Exception as e:
            self.log('ERROR', f'  [ERR] Failed to fix {import_name}: {e}')
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
                self.log('WARN', f'  [WARN] NumPy {np.__version__} incompatible - downgrading...')
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'numpy==1.26.4'
                ], check=True, capture_output=True)
                self.fixed.append('numpy')
                self.log('OK', '  [OK] NumPy downgraded to compatible version!')
                return True
            else:
                self.log('OK', f'  [OK] NumPy {np.__version__} OK')
                return True
        except Exception as e:
            self.log('ERROR', f'  ❌ NumPy check failed: {e}')
            return False
    
    def auto_heal_all(self):
        """Executa todos os reparos automáticos"""
        self.log('INFO', '\n' + '='*60)
        self.log('INFO', 'STARK AUTO-HEALER - Starting...')
        self.log('INFO', '='*60 + '\n')
        
        # Lista de verificações - Priorizar NumPy Version
        checks = [
            ('numpy_version', self.check_and_fix_numpy_version),
            ('pytorch', self.check_and_fix_pytorch),
            ('PyQt6', lambda: self.check_and_fix_package('PyQt6', 'PyQt6')),
            ('cv2', lambda: self.check_and_fix_package('cv2', 'opencv-python')),
            ('ultralytics', lambda: self.check_and_fix_package('ultralytics', 'ultralytics')),
            ('easyocr', lambda: self.check_and_fix_package('easyocr', 'easyocr')),
            ('openvino', lambda: self.check_and_fix_package('openvino', 'openvino-dev >= 2024.1.0')),
            ('optimum', lambda: self.check_and_fix_package('optimum.intel', 'optimum-intel[openvino,nncf]')),
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
            self.log('OK', f'[OK] AUTO-HEALER: Fixed {len(self.fixed)} issues:')
            for item in self.fixed:
                print(f'   - {item}')
        
        if self.failed:
            self.log('WARN', f'\n[WARN] {len(self.failed)} issues need manual attention:')
            for item, error in self.failed:
                print(f'   - {item}: {error[:50]}...')
        
        if not self.fixed and not self.failed:
            self.log('OK', '[OK] AUTO-HEALER: System healthy - no repairs needed!')
        
        self.log('INFO', '='*60 + '\n')
        
        return len(self.failed) == 0

def main():
    """Execute auto-healing"""
    healer = AutoHealer()
    success = healer.auto_heal_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
