import sys
import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SelfHealer")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))


def check_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        logger.info(f"✅ {package_name} is installed and importable.")
        return True
    except ImportError:
        logger.warning(f"❌ {package_name} is MISSING. Fixing...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
            logger.info(f"✅ {package_name} installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package_name}: {e}")
            return False


def fix_numpy():
    try:
        import numpy

        ver = numpy.__version__
        if ver.startswith("2."):
            logger.warning(
                f"⚠️ NumPy v{ver} detected. Downgrading to <2.0 for PyTorch compatibility..."
            )
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0"])
            logger.info("✅ NumPy downgraded.")
            return True
        else:
            logger.info(f"✅ NumPy v{ver} is good.")
            return True
    except ImportError:
        return check_package("numpy")


def fix_voice_controller():
    vc_path = PROJECT_ROOT / "src/core/audio/voice_controller.py"
    if not vc_path.exists():
        logger.error("❌ voice_controller.py not found!")
        return False

    try:
        content = vc_path.read_text(encoding="utf-8")
        if "if self.config.force_headless:" in content:
            logger.warning("⚠️ Legacy 'force_headless' check detected. Patching...")
            new_content = content.replace(
                "if self.config.force_headless:",
                "if getattr(self.config, 'force_headless', False):",
            )
            vc_path.write_text(new_content, encoding="utf-8")
            logger.info("✅ voice_controller.py patched.")
        else:
            logger.info("✅ voice_controller.py appears safe.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to patch voice_controller: {e}")
        return False


def main():
    logger.info("🩺 Starting Self-Healing Protocol...")

    # 1. Critical Dependencies
    check_package("pyautogui")
    fix_numpy()

    # 2. Code Patches
    fix_voice_controller()

    logger.info("✨ Self-Healing Complete.")


if __name__ == "__main__":
    main()
