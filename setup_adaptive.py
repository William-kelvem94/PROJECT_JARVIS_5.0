#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦎 CHAMELEON ADAPTIVE INSTALLER
================================

Intelligent hardware-aware installer that adapts to any machine.

This installer:
1. Detects hardware (RAM, GPU, VRAM, CUDA)
2. Determines profile (LITE/HYBRID/ULTIMATE)
3. Installs appropriate dependencies
4. Generates system_profile.json config
5. Validates installation

Profiles:
- LITE: No GPU, CPU-only, 45 packages
- HYBRID: 4-6GB VRAM, light training, 58 packages  
- ULTIMATE: 8GB+ VRAM, full ML stack, 70 packages

Usage:
    python setup_adaptive.py

Author: JARVIS Singularity Team
Version: 1.0.0
"""

import sys
import os
import json
import platform
import subprocess
import ctypes
from pathlib import Path
from typing import Dict, Tuple, Optional, List

# Ensure we can find local modules
sys.path.insert(0, str(Path(__file__).parent))


class HardwareDetector:
    """Detects system hardware capabilities without external dependencies."""
    
    def __init__(self):
        self.os_name = platform.system()
        self.cpu_count = os.cpu_count() or 1
        
    def get_ram_gb(self) -> float:
        """Get total system RAM in GB using ctypes."""
        try:
            if self.os_name == "Windows":
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", c_ulong),
                        ("dwMemoryLoad", c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                memoryStatus = MEMORYSTATUSEX()
                memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
                return memoryStatus.ullTotalPhys / (1024**3)
            
            elif self.os_name == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            kb = int(line.split()[1])
                            return kb / (1024**2)
            
            elif self.os_name == "Darwin":  # macOS
                result = subprocess.run(['sysctl', 'hw.memsize'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    bytes_ram = int(result.stdout.split(':')[1].strip())
                    return bytes_ram / (1024**3)
                    
        except Exception as e:
            print(f"⚠️  Could not detect RAM: {e}")
            
        return 8.0  # Default fallback
    
    def get_gpu_info(self) -> Dict:
        """Detect NVIDIA GPU using nvidia-smi."""
        gpu_info = {
            'available': False,
            'name': 'None',
            'vram_gb': 0.0,
            'cuda_version': 'N/A',
            'driver_version': 'N/A'
        }
        
        try:
            # Try to run nvidia-smi
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = [p.strip() for p in lines[0].split(',')]
                    if len(parts) >= 3:
                        gpu_info['available'] = True
                        gpu_info['name'] = parts[0]
                        gpu_info['vram_gb'] = float(parts[1]) / 1024  # MB to GB
                        gpu_info['driver_version'] = parts[2]
                        
                        # Try to get CUDA version
                        cuda_result = subprocess.run(
                            ['nvidia-smi'],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if cuda_result.returncode == 0:
                            for line in cuda_result.stdout.split('\n'):
                                if 'CUDA Version:' in line:
                                    cuda_ver = line.split('CUDA Version:')[1].strip().split()[0]
                                    gpu_info['cuda_version'] = cuda_ver
                                    break
                                    
        except FileNotFoundError:
            print("ℹ️  nvidia-smi not found (no NVIDIA GPU or drivers not installed)")
        except subprocess.TimeoutExpired:
            print("⚠️  nvidia-smi timed out")
        except Exception as e:
            print(f"⚠️  GPU detection error: {e}")
            
        return gpu_info
    
    def determine_profile(self, ram_gb: float, gpu_info: Dict) -> str:
        """Determine hardware profile based on capabilities."""
        if not gpu_info['available'] or gpu_info['vram_gb'] < 4:
            return "LITE"
        elif gpu_info['vram_gb'] < 8:
            return "HYBRID"
        else:
            return "ULTIMATE"
    
    def detect_all(self) -> Dict:
        """Run full hardware detection."""
        print("\n[1/6] Detecting Hardware...")
        
        ram_gb = self.get_ram_gb()
        print(f"  ✓ OS: {self.os_name}")
        print(f"  ✓ CPU Cores: {self.cpu_count}")
        print(f"  ✓ RAM: {ram_gb:.1f} GB")
        
        gpu_info = self.get_gpu_info()
        if gpu_info['available']:
            print(f"  ✓ GPU: {gpu_info['name']}")
            print(f"  ✓ VRAM: {gpu_info['vram_gb']:.1f} GB")
            print(f"  ✓ CUDA: {gpu_info['cuda_version']}")
            print(f"  ✓ Driver: {gpu_info['driver_version']}")
        else:
            print(f"  ✓ GPU: None detected")
        
        profile = self.determine_profile(ram_gb, gpu_info)
        
        return {
            'os': self.os_name,
            'cpu_cores': self.cpu_count,
            'ram_gb': ram_gb,
            'gpu_available': gpu_info['available'],
            'gpu_name': gpu_info['name'],
            'vram_gb': gpu_info['vram_gb'],
            'cuda_version': gpu_info['cuda_version'],
            'driver_version': gpu_info['driver_version'],
            'profile': profile,
            'training_enabled': profile in ['HYBRID', 'ULTIMATE'],
            'full_ml_stack': profile == 'ULTIMATE'
        }


class AdaptiveInstaller:
    """Manages adaptive dependency installation."""
    
    def __init__(self, hardware_info: Dict):
        self.hw = hardware_info
        self.profile = hardware_info['profile']
        
    def get_requirements_file(self) -> str:
        """Get the appropriate requirements file for this profile."""
        files = {
            'LITE': 'requirements_lite.txt',
            'HYBRID': 'requirements_hybrid.txt',
            'ULTIMATE': 'requirements_ultimate.txt'
        }
        return files.get(self.profile, 'requirements_lite.txt')
    
    def install_dependencies(self) -> bool:
        """Install dependencies for detected profile."""
        print(f"\n[3/6] Installing Dependencies for {self.profile} Profile...")
        
        req_file = self.get_requirements_file()
        req_path = Path(__file__).parent / req_file
        
        if not req_path.exists():
            print(f"⚠️  Requirements file not found: {req_file}")
            print("  Using fallback: requirements_singularity.txt")
            req_path = Path(__file__).parent / 'requirements_singularity.txt'
            
        if not req_path.exists():
            print("❌ No requirements file found!")
            return False
        
        print(f"  Installing from: {req_file}")
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(req_path), 
                 '--upgrade', '--quiet'],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes max
            )
            
            if result.returncode == 0:
                print(f"  ✓ Dependencies installed successfully")
                return True
            else:
                print(f"⚠️  Some packages may have failed:")
                print(result.stderr[:500])
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  Installation timed out (30min)")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    def validate_installation(self) -> bool:
        """Validate critical packages are installed."""
        print(f"\n[4/6] Validating Installation...")
        
        critical_packages = ['PyQt6', 'psutil', 'requests']
        optional_packages = {
            'LITE': [],
            'HYBRID': ['torch', 'bitsandbytes'],
            'ULTIMATE': ['torch', 'unsloth', 'peft']
        }
        
        all_ok = True
        
        # Check critical
        for pkg in critical_packages:
            try:
                __import__(pkg.lower().replace('-', '_'))
                print(f"  ✓ {pkg}")
            except ImportError:
                print(f"  ❌ {pkg} - MISSING (critical!)")
                all_ok = False
        
        # Check optional
        for pkg in optional_packages.get(self.profile, []):
            try:
                __import__(pkg.lower().replace('-', '_'))
                print(f"  ✓ {pkg}")
            except ImportError:
                print(f"  ⚠️  {pkg} - missing (optional)")
        
        return all_ok
    
    def generate_config(self) -> bool:
        """Generate system_profile.json config file."""
        print(f"\n[5/6] Generating System Config...")
        
        config_dir = Path(__file__).parent / 'config'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'system_profile.json'
        
        config_data = {
            'version': '1.0.0',
            'detected_at': str(Path(__file__).parent),
            'profile': self.hw['profile'],
            'hardware': {
                'os': self.hw['os'],
                'cpu_cores': self.hw['cpu_cores'],
                'ram_gb': self.hw['ram_gb'],
                'gpu_available': self.hw['gpu_available'],
                'gpu_name': self.hw['gpu_name'],
                'vram_gb': self.hw['vram_gb'],
                'cuda_version': self.hw['cuda_version']
            },
            'features': {
                'training_enabled': self.hw['training_enabled'],
                'full_ml_stack': self.hw['full_ml_stack'],
                'gpu_acceleration': self.hw['gpu_available'],
                'voice': True,
                'vision': True,
                'hud': True,
                'dashboard': True
            },
            'dependencies': {
                'requirements_file': self.get_requirements_file(),
                'torch_available': self.profile in ['HYBRID', 'ULTIMATE'],
                'ml_training_available': self.profile == 'ULTIMATE'
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"  ✓ Config saved to: {config_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False


def main():
    """Main installation routine."""
    print("\n" + "="*50)
    print("🦎 CHAMELEON ADAPTIVE INSTALLER")
    print("="*50)
    
    # Step 1: Detect hardware
    detector = HardwareDetector()
    hw_info = detector.detect_all()
    
    # Step 2: Show profile
    print(f"\n[2/6] Determined Profile...")
    print(f"  ✓ Profile: {hw_info['profile']}")
    print(f"  ✓ Training: {'Enabled' if hw_info['training_enabled'] else 'Disabled'}")
    print(f"  ✓ Full ML Stack: {'Yes' if hw_info['full_ml_stack'] else 'No'}")
    
    # Step 3-4: Install and validate
    installer = AdaptiveInstaller(hw_info)
    install_ok = installer.install_dependencies()
    valid_ok = installer.validate_installation()
    
    # Step 5: Generate config
    config_ok = installer.generate_config()
    
    # Step 6: Summary
    print(f"\n[6/6] Installation Summary")
    print("="*50)
    
    if install_ok and config_ok:
        print("✅ Installation Complete!")
        print(f"\nProfile: {hw_info['profile']}")
        print(f"Features: ", end="")
        if hw_info['training_enabled']:
            print("Full Training + Inference")
        else:
            print("Inference Only (CPU)")
        
        print(f"\nNext steps:")
        print(f"  1. Run: python main_singularity_integrated.py")
        print(f"  2. Or use: INICIAR_ADAPTATIVO.bat")
        
        return 0
    else:
        print("⚠️  Installation completed with warnings")
        print("Some features may not be available")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)