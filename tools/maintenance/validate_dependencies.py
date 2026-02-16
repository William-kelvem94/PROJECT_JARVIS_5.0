"""
JARVIS 5.0 - Dependency Validator v2.0
Verifica se todas as dependências críticas estão instaladas
Sistema inteligente: distingue "missing" de "broken"
Retorna exit code 0 se OK, 1 se faltam dependências
"""
import sys
import subprocess

CRITICAL_DEPS = [
    ('PyQt6', 'PyQt6', False),
    ('cv2', 'opencv-python', False),
    ('numpy', 'numpy', False),
    ('torch', 'torch', False),
    ('torchvision', 'torchvision', False),
    ('ultralytics', 'ultralytics', True),
    ('onnxruntime', 'onnxruntime', True),
    ('transformers', 'transformers', True),
    ('sentence_transformers', 'sentence-transformers', True),
    ('chromadb', 'chromadb', True),
    # Novos pacotes obrigatórios (Biometria, Áudio, Monitoramento)
    ('face_recognition', 'face-recognition', False),
    ('dlib', 'dlib', False),
    ('pyaudio', 'pyaudio', False),
    ('librosa', 'librosa', False),
    ('soundfile', 'soundfile', False),
    ('psutil', 'psutil', False),
    ('wmi', 'wmi', False),
    ('tktooltip', 'tkinter-tooltip', False),
]

def check_package(import_name, pip_name, use_pip_show=False):
    """Verifica se um pacote está instalado"""
    try:
        # Pre-check for numpy incompatibility
        if import_name == 'numpy':
            import numpy as np
            version = tuple(map(int, np.__version__.split('.')[:2]))
            if version[0] >= 2:
                print(f"    [WARN] NumPy {np.__version__} detectado. Incompatível com torch atual.")
                return False, pip_name

        # Para pacotes pesados, usar pip show ao invés de import
        if use_pip_show:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', pip_name],
                capture_output=True,
                text=False,
                timeout=10
            )
            return result.returncode == 0, None if result.returncode == 0 else pip_name
        else:
            # Import direto para pacotes leves
            # Wrap in more specific try to catch NumPy/Torch errors
            try:
                __import__(import_name)
                return True, None
            except (ImportError, RuntimeError, Exception):
                # Fallback to pip show
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', pip_name],
                    capture_output=True,
                    text=False,
                    timeout=10
                )
                if result.returncode == 0:
                    return False, None # Return False but no pkg name means "Installed but Broken"
                return False, pip_name
    except Exception:
        return False, pip_name

def install_package(pip_name):
    """Tenta instalar um pacote via pip"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name], check=True, capture_output=True, timeout=60)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("[CHECK] Validating JARVIS dependencies...")
    print("=" * 60)
    
    missing = []
    broken = []
    
    for import_name, pip_name, use_pip_show in CRITICAL_DEPS:
        try:
            installed, pkg = check_package(import_name, pip_name, use_pip_show)
            
            if installed:
                print(f"[OK] {import_name:25} OK")
            elif pkg is None:
                print(f"[WARN] {import_name:25} INSTALLED (BROKEN - Needs repair)")
                broken.append(pip_name)
            else:
                print(f"[ERROR] {import_name:25} MISSING")
                missing.append(pkg)
        except Exception:
            print(f"[ERROR] {import_name:25} ERROR (Check Failed)")
            missing.append(pip_name)
    
    print("=" * 60)
    
    if missing:
        print(f"\n[INFO] Tentando instalar {len(missing)} pacotes faltantes automaticamente...")
        for pkg in missing[:]:  # Copia para modificar
            if install_package(pkg):
                print(f"[OK] {pkg} instalado com sucesso!")
                missing.remove(pkg)
            else:
                print(f"[ERROR] Falha ao instalar {pkg}")

    if broken:
        print(f"\n[INFO] Tentando reparar {len(broken)} pacotes quebrados...")
        for pkg in broken[:]:
            if install_package(f"--force-reinstall {pkg}"):
                print(f"[OK] {pkg} reparado!")
                broken.remove(pkg)
            else:
                print(f"[ERROR] Falha ao reparar {pkg}")

    # Retorne 0 apenas se tudo estiver OK após tentativas
    if missing or broken:
        print("\n[ERROR] Alguns pacotes ainda estão faltando ou quebrados. Execute novamente ou verifique manualmente.")
        return 1
    else:
        print("\n[OK] Todas as dependências validadas/instaladas!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
