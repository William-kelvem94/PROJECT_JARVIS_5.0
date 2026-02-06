#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Auto-Configuration & Installation
=======================================================
Intelligent auto-installer with zero-error guarantee.

Features:
- Automatic dependency detection
- Platform-specific installation
- GPU/CPU capability detection
- Configuration file generation
- Error recovery mechanisms
- Progress reporting
"""

import os
import sys
import subprocess
import platform
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('singularity_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SingularityAutoInstaller:
    """Intelligent auto-installer for JARVIS Singularity"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.platform = platform.system()
        self.is_windows = (self.platform == "Windows")
        self.is_linux = (self.platform == "Linux")
        self.is_mac = (self.platform == "Darwin")
        
        # Detection results
        self.has_cuda = False
        self.python_version = sys.version_info
        self.pip_version = None
        
        # Installation status
        self.errors = []
        self.warnings = []
        self.installed_packages = []
        
        logger.info("="*70)
        logger.info("JARVIS SINGULARITY - Auto-Configuration")
        logger.info("="*70)
        logger.info(f"Platform: {self.platform}")
        logger.info(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
    def run(self) -> bool:
        """Run complete auto-installation"""
        try:
            logger.info("\n[1/8] Checking Python version...")
            if not self._check_python():
                return False
                
            logger.info("\n[2/8] Detecting GPU capabilities...")
            self._detect_gpu()
            
            logger.info("\n[3/8] Creating directory structure...")
            self._create_directories()
            
            logger.info("\n[4/8] Installing dependencies...")
            if not self._install_dependencies():
                return False
                
            logger.info("\n[5/8] Generating configuration...")
            self._generate_config()
            
            logger.info("\n[6/8] Setting up FaceID...")
            self._setup_faceid()
            
            logger.info("\n[7/8] Validating installation...")
            if not self._validate_installation():
                return False
                
            logger.info("\n[8/8] Final checks...")
            self._final_checks()
            
            logger.info("\n" + "="*70)
            logger.info("✅ INSTALLATION COMPLETE!")
            logger.info("="*70)
            self._print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fatal error during installation: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
    def _check_python(self) -> bool:
        """Check Python version compatibility"""
        if self.python_version < (3, 8):
            logger.error(f"❌ Python 3.8+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
            
        if self.python_version >= (3, 12):
            logger.warning(f"⚠️  Python {self.python_version.major}.{self.python_version.minor} - Some packages may have issues")
            logger.warning("    Recommended: Python 3.11")
            self.warnings.append("Python version newer than tested (3.11)")
            
        logger.info(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
        # Check pip
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.pip_version = result.stdout.strip()
                logger.info(f"✅ {self.pip_version}")
            else:
                logger.error("❌ pip not found")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to check pip: {e}")
            return False
            
        return True
        
    def _detect_gpu(self):
        """Detect GPU capabilities"""
        try:
            # Try to import torch and check CUDA
            import torch
            if torch.cuda.is_available():
                self.has_cuda = True
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"✅ CUDA GPU detected: {gpu_name}")
            else:
                logger.info("ℹ️  No CUDA GPU detected - Using CPU mode")
                
        except ImportError:
            logger.info("ℹ️  PyTorch not yet installed - Will detect after installation")
            
    def _create_directories(self):
        """Create required directory structure"""
        directories = [
            "data",
            "data/faces",
            "data/screenshots",
            "data/models",
            "data/logs",
            "data/temp",
            "data/audio",
            "data/voice_signatures",
            "models",
            "config",
        ]
        
        for dir_path in directories:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created: {dir_path}")
            
    def _install_dependencies(self) -> bool:
        """Install all dependencies with error handling"""
        requirements_file = self.root_dir / "requirements_singularity.txt"
        
        if not requirements_file.exists():
            logger.error(f"❌ Requirements file not found: {requirements_file}")
            return False
            
        logger.info(f"Installing from: {requirements_file}")
        
        try:
            # Upgrade pip first
            logger.info("Upgrading pip...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                timeout=300
            )
            
            # Install requirements
            logger.info("Installing dependencies (this may take several minutes)...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes max
            )
            
            if result.returncode != 0:
                logger.error("❌ Dependency installation failed")
                logger.error(result.stderr)
                
                # Try to continue with partial installation
                logger.warning("⚠️  Attempting to continue with partial installation...")
                self.warnings.append("Some dependencies may not have installed")
            else:
                logger.info("✅ All dependencies installed successfully")
                
            # Re-detect GPU after torch installation
            self._detect_gpu()
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Installation timed out (>30 minutes)")
            return False
        except Exception as e:
            logger.error(f"❌ Installation error: {e}")
            return False
            
    def _generate_config(self):
        """Generate configuration files"""
        config_path = self.root_dir / "config" / "singularity_config.json"
        
        config = {
            "version": "1.0.0",
            "platform": self.platform,
            "has_cuda": self.has_cuda,
            "paths": {
                "data": "data",
                "faces": "data/faces",
                "screenshots": "data/screenshots",
                "models": "data/models",
                "logs": "data/logs",
                "voice_signatures": "data/voice_signatures"
            },
            "vision": {
                "enabled": True,
                "faceid_enabled": True,
                "ocr_enabled": True,
                "yolo_enabled": True,
                "face_detection_model": "cnn" if self.has_cuda else "hog",
                "screenshot_dir": "data/screenshots"
            },
            "audio": {
                "enabled": True,
                "stt_model": "faster-whisper",
                "stt_model_size": "base",
                "tts_engine": "edge-tts",
                "voice_verification": True,
                "vad_enabled": True,
                "microphone_index": 0
            },
            "system": {
                "god_mode_enabled": True if self.is_windows else False,
                "volume_control": True if self.is_windows else False,
                "process_management": True,
                "window_control": True if self.is_windows else False,
                "audit_logging": True
            },
            "interface": {
                "default_mode": "hud",
                "hud_enabled": True,
                "dashboard_enabled": True,
                "system_tray": True,
                "keyboard_shortcuts": True
            },
            "ai": {
                "local_model": "ollama",
                "model_name": "llama3",
                "api_key": "",
                "use_cloud_fallback": False
            }
        }
        
        # Save config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, indent=4, fp=f)
            
        logger.info(f"✅ Configuration saved: {config_path}")
        
        # Also create yaml config if needed
        yaml_config = self.root_dir / "config.yaml"
        if not yaml_config.exists():
            self._create_yaml_config(yaml_config, config)
            
    def _create_yaml_config(self, path: Path, config: Dict):
        """Create YAML configuration"""
        yaml_content = f"""# JARVIS Singularity Configuration
# Auto-generated by setup_singularity_auto.py

app:
  name: "JARVIS Singularity"
  version: "1.0.0"
  data_dir: "{config['paths']['data']}"
  log_level: "INFO"

vision:
  enabled: {str(config['vision']['enabled']).lower()}
  faceid_enabled: {str(config['vision']['faceid_enabled']).lower()}
  face_detection_model: "{config['vision']['face_detection_model']}"
  
audio:
  enabled: {str(config['audio']['enabled']).lower()}
  stt_model: "{config['audio']['stt_model']}"
  tts_engine: "{config['audio']['tts_engine']}"
  
system:
  god_mode: {str(config['system']['god_mode_enabled']).lower()}
  
ai:
  local_model: "{config['ai']['local_model']}"
  model_name: "{config['ai']['model_name']}"
"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
            
        logger.info(f"✅ YAML config created: {path}")
        
    def _setup_faceid(self):
        """Setup FaceID system"""
        faces_dir = self.root_dir / "data" / "faces"
        
        # Create README for face enrollment
        readme = faces_dir / "README.txt"
        readme.write_text("""
FaceID Setup Instructions
=========================

To add authorized users:

1. Take a clear photo of the user's face (front view, good lighting)
2. Save as: username.jpg (e.g., admin.jpg, john.jpg)
3. Place in this directory

Requirements:
- JPEG format (.jpg or .jpeg)
- Face clearly visible
- Good lighting
- Front-facing view
- One face per image

The system will automatically load all faces from this directory.

For testing, you can use your webcam to capture a face:

python -c "import cv2; cam = cv2.VideoCapture(0); ret, frame = cam.read(); cv2.imwrite('data/faces/admin.jpg', frame); cam.release(); print('Face captured as admin.jpg')"
""")
        
        logger.info(f"✅ FaceID setup instructions created")
        
    def _validate_installation(self) -> bool:
        """Validate that critical components are installed"""
        critical_imports = [
            ("PyQt6.QtWidgets", "PyQt6"),
            ("numpy", "numpy"),
            ("torch", "torch"),
            ("cv2", "opencv-python"),
            ("psutil", "psutil"),
        ]
        
        optional_imports = [
            ("face_recognition", "face-recognition"),
            ("easyocr", "easyocr"),
            ("mss", "mss"),
            ("pycaw", "pycaw"),
        ]
        
        logger.info("Validating critical packages...")
        all_ok = True
        
        for module_name, package_name in critical_imports:
            try:
                __import__(module_name)
                logger.info(f"✅ {package_name}")
            except ImportError as e:
                logger.error(f"❌ {package_name} - CRITICAL")
                self.errors.append(f"Missing critical package: {package_name}")
                all_ok = False
                
        logger.info("\nValidating optional packages...")
        for module_name, package_name in optional_imports:
            try:
                __import__(module_name)
                logger.info(f"✅ {package_name}")
            except ImportError:
                logger.warning(f"⚠️  {package_name} - Optional (some features disabled)")
                self.warnings.append(f"Optional package not installed: {package_name}")
                
        return all_ok
        
    def _final_checks(self):
        """Final system checks"""
        # Check if main files exist
        critical_files = [
            "main_singularity.py",
            "src/interface/window_manager.py",
            "src/core/vision_system.py",
            "src/core/system_integrator.py",
        ]
        
        for file_path in critical_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                logger.info(f"✅ {file_path}")
            else:
                logger.warning(f"⚠️  {file_path} - Not found")
                self.warnings.append(f"Missing file: {file_path}")
                
    def _print_summary(self):
        """Print installation summary"""
        print("\n" + "="*70)
        print("INSTALLATION SUMMARY")
        print("="*70)
        
        print(f"\nPlatform: {self.platform}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"GPU: {'✅ CUDA Available' if self.has_cuda else '❌ CPU Only'}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("\n✅ No errors")
            
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        else:
            print("✅ No warnings")
            
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("1. Review configuration: config/singularity_config.json")
        print("2. Add authorized faces: data/faces/username.jpg")
        print("3. Run JARVIS: python main_singularity.py")
        print("4. Toggle dashboard: Ctrl+Shift+J")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        JARVIS SINGULARITY - AUTO-INSTALLER v1.0             ║
║                                                              ║
║  Intelligent auto-configuration with zero-error guarantee   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    installer = SingularityAutoInstaller()
    
    try:
        success = installer.run()
        
        if success:
            print("\n🎉 Installation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Installation failed. Check singularity_setup.log for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
