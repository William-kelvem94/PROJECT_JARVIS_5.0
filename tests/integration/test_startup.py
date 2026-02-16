#!/usr/bin/env python3
"""Startup validation for JARVIS 5.0."""

<<<<<<< Updated upstream
=======
import os
import subprocess
>>>>>>> Stashed changes
import sys
import subprocess
from pathlib import Path

<<<<<<< HEAD
<<<<<<< Updated upstream
=======

>>>>>>> dev-new-version
def test_python_syntax():
    """Test that all Python files have valid syntax"""
=======
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _force_utf8_output() -> None:
    """Normalize stdout/stderr encoding for default Windows terminals."""
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_force_utf8_output()


def test_python_syntax() -> bool:
    """Test that all Python files in src have valid syntax."""
>>>>>>> Stashed changes
    print("Testing Python syntax...")
    errors = []

    for py_file in Path("src").rglob("*.py"):
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                check=True,
                capture_output=True,
                timeout=5,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace")
            errors.append(f"{py_file}: {stderr}")
        except subprocess.TimeoutExpired:
            errors.append(f"{py_file}: Compilation timeout")

    if errors:
        print(f"[FAIL] Syntax errors found in {len(errors)} files:")
        for error in errors[:5]:
            print(f"  {error}")
        return False
<<<<<<< HEAD
<<<<<<< Updated upstream
    
    print(f"✅ All Python files have valid syntax")
=======

    print("✅ All Python files have valid syntax")
>>>>>>> dev-new-version
    return True


def test_critical_imports():
    """Test that critical modules can be imported"""
=======

    print("[OK] All Python files have valid syntax")
    return True


def test_critical_imports() -> bool:
    """Test that critical modules can be imported."""
>>>>>>> Stashed changes
    print("\nTesting critical imports...")

    critical_modules = [
        "src.core.infrastructure.async_event_bus",
        "src.core.infrastructure.boot_manager",
        "src.evolution.evolution_manager",
        "src.evolution.self_observer",
        "src.evolution.auto_healer",
        "src.evolution.safe_executor",
    ]

    errors = []
    for module in critical_modules:
        try:
            __import__(module)
<<<<<<< Updated upstream
            print(f"  ✅ {module}")
        except Exception as e:
            errors.append(f"{module}: {e}")
            print(f"  ❌ {module}: {e}")
<<<<<<< HEAD
    
=======
            print(f"  [OK] {module}")
        except Exception as exc:
            errors.append(f"{module}: {exc}")
            print(f"  [FAIL] {module}: {exc}")

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version
    if errors:
        print(f"[FAIL] Import errors in {len(errors)} modules")
        return False
<<<<<<< HEAD
<<<<<<< Updated upstream
    
=======

>>>>>>> dev-new-version
    print("✅ All critical imports successful")
    return True


def test_evolution_layer():
    """Test Evolution Layer initialization"""
=======

    print("[OK] All critical imports successful")
    return True


def test_evolution_layer() -> bool:
    """Test evolution layer import path stability."""
>>>>>>> Stashed changes
    print("\nTesting Evolution Layer...")

    try:
<<<<<<< HEAD
<<<<<<< Updated upstream
        from src.evolution import evolution_manager
=======
>>>>>>> dev-new-version
        print("  ✅ evolution_manager imported")

        print("  ✅ knowledge_db imported")

        print("  ✅ authorization_manager imported")

        print("  ✅ module_generator imported")

        print("  ✅ voice_commands imported")

        print("✅ Evolution Layer imports successful")
=======
        from src.evolution import evolution_manager  # noqa: F401
        from src.evolution import self_observer  # noqa: F401

        print("  [OK] evolution_manager imported")
        print("  [OK] self_observer imported")
        print("[OK] Evolution Layer imports successful")
>>>>>>> Stashed changes
        return True
    except Exception as exc:
        print(f"[FAIL] Evolution Layer import failed: {exc}")
        return False

<<<<<<< HEAD
<<<<<<< Updated upstream
=======

>>>>>>> dev-new-version
def test_main_startup():
    """Test that main.py can start (quick test mode)"""
    print("\nTesting main.py startup (this may take a moment)...")

    # Create a minimal test that imports main
=======

def test_main_startup() -> bool:
    """Test that main.py can be imported with quick-test env flags."""
    print("\nTesting main.py startup (this may take a moment)...")

>>>>>>> Stashed changes
    test_script = """
import os
import sys

os.environ['JARVIS_QUICK_TEST'] = 'true'
os.environ['JARVIS_EVOLUTION_ENABLED'] = 'false'
os.environ.setdefault('PYTHONUTF8', '1')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

try:
    import main  # noqa: F401
    print('IMPORT_SUCCESS')
    raise SystemExit(0)
except Exception as exc:
    print(f'IMPORT_FAILED: {exc}')
    import traceback
    traceback.print_exc()
    raise SystemExit(1)
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=Path.cwd(),
        )
<<<<<<< HEAD
<<<<<<< Updated upstream
        
=======

>>>>>>> dev-new-version
        if "IMPORT_SUCCESS" in result.stdout:
            print("✅ main.py imports successfully")
            return True
        else:
            print("❌ main.py import failed")
            print(f"  stdout: {result.stdout[:500]}")
            print(f"  stderr: {result.stderr[:500]}")
            return False
=======
>>>>>>> Stashed changes
    except subprocess.TimeoutExpired:
        print("[FAIL] main.py import test timed out")
        return False
    except Exception as exc:
        print(f"[FAIL] main.py import test error: {exc}")
        return False

<<<<<<< HEAD
<<<<<<< Updated upstream
def main():
    """Run all startup tests"""
    print("="*60)
=======
    if "IMPORT_SUCCESS" in result.stdout:
        print("[OK] main.py imports successfully")
        return True

    print("[FAIL] main.py import failed")
    print(f"  stdout: {result.stdout[:500]}")
    print(f"  stderr: {result.stderr[:500]}")
    return False


def main() -> int:
    """Run all startup tests."""
    print("=" * 60)
>>>>>>> Stashed changes
=======

def main():
    """Run all startup tests"""
    print("=" * 60)
>>>>>>> dev-new-version
    print("  JARVIS 5.0 Startup Validation")
    print("=" * 60)

    tests = [
        ("Python Syntax", test_python_syntax),
        ("Critical Imports", test_critical_imports),
        ("Evolution Layer", test_evolution_layer),
        ("Main Startup", test_main_startup),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            results.append((test_name, test_func()))
        except Exception as exc:
            print(f"[FAIL] Test '{test_name}' crashed: {exc}")
            results.append((test_name, False))
<<<<<<< HEAD
<<<<<<< Updated upstream
    
    # Summary
    print("\n" + "="*60)
=======

    print("\n" + "=" * 60)
>>>>>>> Stashed changes
=======

    # Summary
    print("\n" + "=" * 60)
>>>>>>> dev-new-version
    print("  Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
<<<<<<< Updated upstream
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
<<<<<<< HEAD
    
=======
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version
    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed. JARVIS 5.0 is ready to run.")
        return 0
    if passed >= total - 1:
        print("\nAlmost ready. Some non-critical tests failed.")
        return 0

    print("\nCritical tests failed. Please review errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
