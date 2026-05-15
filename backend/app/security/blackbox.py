"""
JARVIS 5.0 - Biometric BlackBox Shim
This is a dummy implementation to maintain API compatibility while disabling
actual SQLCipher encryption.
"""
from loguru import logger

class BlackBox:
    """
    Shim for BlackBox. All biometric operations are now bypassed.
    """
    def __init__(self, db_path: str, encryption_key: str):
        self.db_path = db_path
        self.key = encryption_key
        logger.info("[Shim] BlackBox initialized in bypass mode.")

    def _init_db(self):
        # Do nothing - no database initialization needed for shim
        pass

    def store_biometric(self, user_id: str, b_type: str, b_hash: bytes):
        # Bypass storage
        pass

    def verify_biometric(self, user_id: str, b_type: str, b_hash: bytes) -> bool:
        # ALWAYS allow access in bypass mode
        return True
