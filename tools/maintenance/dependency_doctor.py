#!/usr/bin/env python3
"""
JARVIS Dependency Diagnostic and Repair Tool
Diagnoses and fixes common dependency issues
"""

import os
import sys
import subprocess
import shlex
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DEPENDENCY_DOCTOR")


def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        logger.info(f"🔧 {description}...")
        args = shlex.split(cmd) if isinstance(cmd, str) else cmd
        result = subprocess.run(args, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info(f"✅ {description} - SUCCESS")
            return True
        else:
            logger.error(f"❌ {description} - FAILED")
            logger.error(f"Output: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        logger.error(f"💥 {description} - ERROR: {e}")
        return False


def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        logger.info(f"✅ {description} - OK")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ {description} - MISSING: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - ERROR: {e}")
        return False


def diagnose_issues():
    """Diagnose common dependency issues"""
    logger.info("🔍 DIAGNOSTICANDO DEPENDÊNCIAS...")

    issues = []

    # Test basic imports
    if not test_import("torch", "PyTorch"):
        issues.append("torch")
    if not test_import("torchvision", "TorchVision"):
        issues.append("torchvision")
    if not test_import("transformers", "Transformers"):
        issues.append("transformers")
    if not test_import("faster_whisper", "Faster Whisper"):
        issues.append("faster_whisper")

    return issues


def repair_issues(issues):
    """Attempt to repair identified issues"""
    logger.info("🔧 TENTANDO CORREÇÕES AUTOMÁTICAS...")

    success_count = 0

    # Fix PyTorch issues
    if "torch" in issues or "torchvision" in issues:
        logger.info("🔧 Corrigindo PyTorch...")
        # Try CPU-only PyTorch first
        if run_command(
            "pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
            "Instalando PyTorch CPU-only",
        ):
            success_count += 1

    # Fix transformers/faster-whisper
    if "transformers" in issues or "faster_whisper" in issues:
        logger.info("🔧 Corrigindo Transformers/Faster-Whisper...")
        if run_command(
            "pip install --upgrade transformers faster-whisper",
            "Atualizando Transformers",
        ):
            success_count += 1

    # Force reinstall torch if still failing
    if "torch" in issues:
        logger.info("🔧 Forçando reinstalação do PyTorch...")
        if run_command(
            "pip install --upgrade --force-reinstall torch",
            "Forçando reinstalação PyTorch",
        ):
            success_count += 1

    return success_count


def main():
    print("=" * 80)
    print("🔧 JARVIS DEPENDENCY DOCTOR")
    print("Diagnóstico e correção automática de dependências")
    print("=" * 80)

    # Set environment
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # Diagnose
    issues = diagnose_issues()

    if not issues:
        logger.info("🎉 Todas as dependências estão OK!")
        return 0

    logger.warning(f"⚠️ Encontrados {len(issues)} problemas: {', '.join(issues)}")

    # Ask for repair
    try:
        response = (
            input("\n🔧 Deseja tentar correções automáticas? (y/N): ").strip().lower()
        )
        if response in ["y", "yes", "s", "sim"]:
            success_count = repair_issues(issues)

            if success_count > 0:
                logger.info(f"✅ {success_count} correções aplicadas com sucesso!")
                logger.info("🔄 Testando novamente...")

                # Re-test
                remaining_issues = diagnose_issues()
                if not remaining_issues:
                    logger.info("🎉 Todos os problemas foram resolvidos!")
                    return 0
                else:
                    logger.warning(f"⚠️ Ainda restam {len(remaining_issues)} problemas")
            else:
                logger.error("❌ Nenhuma correção automática funcionou")
        else:
            logger.info("⏭️ Pulando correções automáticas")

    except KeyboardInterrupt:
        logger.info("🛑 Cancelado pelo usuário")

    # Show manual solutions
    print("\n" + "=" * 80)
    print("🔧 SOLUÇÕES MANUAIS RECOMENDADAS:")
    print("=" * 80)
    print("1. PyTorch Issues:")
    print("   pip uninstall torch torchvision torchaudio")
    print(
        "   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    )
    print()
    print("2. Encoding Issues:")
    print("   chcp 65001  # Windows UTF-8")
    print("   set PYTHONUTF8=1")
    print()
    print("3. Version Conflicts:")
    print("   pip install --upgrade --force-reinstall torch transformers")
    print()
    print("4. Alternative - Use JARVIS Lite:")
    print("   python main_lite.py  # No heavy dependencies")
    print("=" * 80)

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
