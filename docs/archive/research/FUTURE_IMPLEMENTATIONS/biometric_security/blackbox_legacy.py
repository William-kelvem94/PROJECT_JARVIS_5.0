import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
import os

class BlackBox:
    """
    Secure storage for biometric data using SQLCipher for AES-256 encryption.
    """

    def __init__(self, db_path: str, encryption_key: str):
        self.db_path = db_path
        self.key = encryption_key
        self._init_db()

    def _init_db(self):
        """Initialize the encrypted database and biometric schema."""
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()

        # Set the encryption key immediately after connection
        cursor.execute(f"PRAGMA key = '{self.key}';")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS biometric_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                biometric_type TEXT NOT NULL,
                biometric_hash BLOB NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, biometric_type)
            )
        ''')
        conn.commit()
        conn.close()

    def store_biometric(self, user_id: str, b_type: str, b_hash: bytes):
        """Securely stores a biometric hash into the encrypted vault."""
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA key = '{self.key}';")
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO biometric_vault (user_id, biometric_type, biometric_hash) VALUES (?, ?, ?)",
                (user_id, b_type, b_hash)
            )
            conn.commit()
        finally:
            conn.close()

    def verify_biometric(self, user_id: str, b_type: str, b_hash: bytes) -> bool:
        """Verifies a biometric hash against the encrypted vault."""
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA key = '{self.key}';")

        cursor.execute(
            "SELECT biometric_hash FROM biometric_vault WHERE user_id = ? AND biometric_type = ?",
            (user_id, b_type)
        )
        result = cursor.fetchone()
        conn.close()

        return result is not None and result[0] == b_hash
