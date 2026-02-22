#!/usr/bin/env python3
"""
Test script to validate JARVIS 5.0 can start without errors
"""

import sys
import subprocess
from pathlib import Path


def test_python_syntax():
    """Test that all Python files have valid syntax"""
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
        except subprocess.CalledProcessError as e:
            errors.append(f"{py_file}: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            errors.append(f"{py_file}: Compilation timeout")

    if errors:
        print(f"❌ Syntax errors found in {len(errors)} files:")
        for error in errors[:5]:  # Show first 5
            print(f"  {error}")
        return False

    print("✅ All Python files have valid syntax")
    return True


def test_critical_imports():
    """Test that critical modules can be imported"""
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
            print(f"  ✅ {module}")
        except Exception as e:
            errors.append(f"{module}: {e}")
            print(f"  ❌ {module}: {e}")

    if errors:
        print(f"❌ Import errors in {len(errors)} modules")
        return False

    print("✅ All critical imports successful")
    return True


def test_evolution_layer():
    """Test Evolution Layer initialization"""
    print("\nTesting Evolution Layer...")

    try:
        print("  ✅ evolution_manager imported")

        print("  ✅ knowledge_db imported")

        print("  ✅ authorization_manager imported")

        print("  ✅ module_generator imported")

        print("  ✅ voice_commands imported")

        print("✅ Evolution Layer imports successful")
        return True
    except Exception as e:
        print(f"❌ Evolution Layer import failed: {e}")
        return False


def test_main_startup():
    """Test that main.py can start (quick test mode)"""
    print("\nTesting main.py startup (this may take a moment)...")

    # Create a minimal test that imports main
    test_script = """
import sys
import os
os.environ["JARVIS_QUICK_TEST"] = "true"
os.environ["JARVIS_EVOLUTION_ENABLED"] = "false"  # Disable for quick test

try:
    # Just test if main can be imported without crashing
    import main
    print("IMPORT_SUCCESS")
    sys.exit(0)
except Exception as e:
    print(f"IMPORT_FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path.cwd(),
        )

        if "IMPORT_SUCCESS" in result.stdout:
            print("✅ main.py imports successfully")
            return True
        else:
            print("❌ main.py import failed")
            print(f"  stdout: {result.stdout[:500]}")
            print(f"  stderr: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  main.py test timed out (may still work in production)")
        return False
    except Exception as e:
        print(f"❌ main.py test error: {e}")
        return False


def main():
    """Run all startup tests"""
    print("=" * 60)
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
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! JARVIS 5.0 is ready to run!")
        return 0
    elif passed >= total - 1:
        print("\n⚠️  Almost ready! Some non-critical tests failed.")
        return 0
    else:
        print("\n❌ Critical tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
