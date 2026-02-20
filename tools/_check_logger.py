import sys
import os
sys.path.insert(0, os.getcwd())
try:
    print("Importing Blackbox...")
    from src.core.config.blackbox_logger import setup_blackbox_integration, blackbox_logger
    print("Setup Blackbox...")
    setup_blackbox_integration()
    print("Blackbox Setup Complete.")
    blackbox_logger.info("Test Log Entry")
    print("Log Entry Written.")
except Exception as e:
    print(f"FAIL: {e}")
