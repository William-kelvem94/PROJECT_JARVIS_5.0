import os
import hashlib
import platform
import subprocess
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class SentinelSecurity:
    """
    Sentinel v3 Security Core.
    Handles HWID-based key derivation, BlackBox integration, and Real-Time Command Validation.
    """

    def __init__(self, blackbox_instance=None):
        self.ph = PasswordHasher()
        self.blackbox = blackbox_instance
        # Constant salt for HWID derivation to ensure consistency across reboots
        self.system_salt = b"JARVIS_SENTINEL_v3_SALT_2026"

    def get_hwid(self) -> str:
        """
        Generates a unique Hardware ID (HWID) based on the system's motherboard/UUID.
        Works on Windows (via wmic) and Linux.
        """
        try:
            if platform.system() == "Windows":
                # Get UUID from wmic
                cmd = "wmic csproduct get uuid"
                uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
                return uuid
            else:
                # Get machine-id from Linux
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
        except Exception as e:
            # Fallback to a combination of node and platform if UUID fails
            import socket
            fallback = f"{platform.node()}-{platform.processor()}-{platform.machine()}"
            return hashlib.sha256(fallback.encode()).hexdigest()

    def derive_system_key(self) -> str:
        """
        Derives a cryptographic key using Argon2id and the system's HWID.
        This key is used to unlock the BlackBox.
        """
        hwid = self.get_hwid()
        # We use the HWID as the password and a static salt to derive a consistent system key
        # Argon2id is the recommended variant for password hashing and key derivation
        key_hash = self.ph.hash(hwid + self.system_salt.decode())
        # Return a truncated version of the hash as the encryption key string
        return hashlib.sha256(key_hash.encode()).hexdigest()

    async def validate_llm_command(self, command: str, parser) -> bool:
        """
        Real-Time Sentinel: Intercepts LLM commands and validates them via the sentinel_parser.
        """
        if not command:
            return True

        is_safe = parser.validate_command(command)
        if not is_safe:
            # Log security breach attempt (could be integrated with telemetry)
            print(f"[SENTINEL ALERT] Blocked dangerous command: {command}")

        return is_safe

    def authenticate_user_biometric(self, user_id: str, b_type: str, b_hash: bytes) -> bool:
        """
        Integrates BlackBox into the authentication flow.
        """
        if not self.blackbox:
            raise RuntimeError("BlackBox not initialized in SentinelSecurity")

        return self.blackbox.verify_biometric(user_id, b_type, b_hash)
