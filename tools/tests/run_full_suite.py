import os
import sys
import subprocess
import time
from pathlib import Path


def setup_path():
    """Adiciona o diretório raiz ao PYTHONPATH"""
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    os.environ["PYTHONPATH"] = str(project_root)
    return project_root


def run_tests(project_root):
    """Executa a suíte de testes completa"""
    print("=" * 60)
    print(" JARVIS 5.0 - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    test_dirs = [
        project_root / "tests" / "unit",
        project_root / "tests" / "integration",
    ]

    # Validar diretórios
    valid_dirs = [str(d) for d in test_dirs if d.exists()]

    if not valid_dirs:
        print("[ERROR] No valid test directories found!")
        return 1

    print(f"[INFO] Discovered test directories: {len(valid_dirs)}")
    for d in valid_dirs:
        print(f"  - {d}")

    print("\n[INFO] Starting pytest...")
    start_time = time.time()

    # Configuração do Pytest
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",  # Verbose
        "--durations=5",  # Show slowest tests
        # "--tb=short",          # Shorter tracebacks
    ] + valid_dirs

    try:
        result = subprocess.run(
            cmd, cwd=project_root, capture_output=False, check=False
        )
        duration = time.time() - start_time

        print("\n" + "=" * 60)
        if result.returncode == 0:
            print(f" [SUCCESS] All tests passed in {duration:.2f}s")
        else:
            print(f" [FAILURE] Tests failed with exit code {result.returncode}")
        print("=" * 60)

        return result.returncode

    except Exception as e:
        print(
            f"\n[CRITICAL] Failed to execute pytest command {cmd} "
            f"in directory {project_root}: {e}"
        )
        return 1


if __name__ == "__main__":
    root = setup_path()
    sys.exit(run_tests(root))
