"""
JARVIS 5.0 - Dependency Validator
Verifica se todas as dependências críticas estão instaladas
Retorna exit code 0 se OK, 1 se faltam dependências
"""
import sys
import subprocess

CRITICAL_PACKAGES = [
    ('PyQt6', 'PyQt6', False),  # False = fast import
    ('cv2', 'opencv-python', False),
    ('numpy', 'numpy', False),
    ('torch', 'torch', True),  # True = use pip show (slow import)
    ('ultralytics', 'ultralytics', False),
    ('onnxruntime', 'onnxruntime', True),  # Use pip show (DLL issues on import)
    ('transformers', 'transformers', True),  # Slow import
    ('sentence_transformers', 'sentence-transformers', True),  # Slow import
    ('chromadb', 'chromadb', True),  # Slow import
]

def check_package(import_name, pip_name, use_pip_show=False):
    """Verifica se um pacote está instalado"""
    try:
        # Para pacotes pesados, usar pip show ao invés de import
        if use_pip_show:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', pip_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0, None if result.returncode == 0 else pip_name
        else:
            # Import direto para pacotes leves
            __import__(import_name)
            return True, None
    except ImportError as e:
        return False, pip_name

def main():
    print("🔍 Validating JARVIS dependencies...")
    print("=" * 60)
    
    missing = []
    
    for import_name, pip_name, use_pip_show in CRITICAL_PACKAGES:
        installed, pkg = check_package(import_name, pip_name, use_pip_show)
        status = "✅" if installed else "❌"
        print(f"{status} {import_name:25} {'OK' if installed else 'MISSING'}")
        
        if not installed:
            missing.append(pkg)
    
    print("=" * 60)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} critical dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nRun INSTALL_JARVIS.bat to install missing packages.")
        return 1
    else:
        print("\n✅ All critical dependencies installed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
