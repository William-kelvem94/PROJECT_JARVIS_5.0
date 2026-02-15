#!/usr/bin/env python3
"""
JARVIS 5.0 - Minimal Test Script
Testa apenas os componentes essenciais sem dependências pesadas
"""

import sys
import os
import warnings
import time
import platform

# Supress warnings
warnings.filterwarnings('ignore')

print("🚀 JARVIS 5.0 - Minimal Test")
print("=" * 50)

# Test basic Python
print("✅ Python version:", sys.version.split()[0])

# Test platform
print("✅ Platform:", platform.system(), platform.release())

# Test basic imports
try:
    import pygame
    print("✅ Pygame available")
except ImportError as e:
    print("❌ Pygame failed:", e)

# Test config - commented out to avoid heavy imports
# try:
#     sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
#     from utils.config import config
#     print("✅ Config system available")
# except ImportError as e:
#     print("❌ Config failed:", e)

print("ℹ️  Config system test skipped (heavy dependencies)")

print("\n🎯 JARVIS Core Components Test Complete!")
print("💡 Use START_JARVIS.bat for full system initialization")