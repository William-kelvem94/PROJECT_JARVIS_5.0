import os
import numpy as np
from loguru import logger
from typing import Optional

class BiometricVault:
    """
    Secure storage for biometric embeddings.
    Currently implements file-based storage for Voice Prints.
    """
    def __init__(self, vault_dir: str = None):
        if vault_dir is None:
            # Resolve path relative to app root
            self.vault_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "voices"
            )
        else:
            self.vault_dir = vault_dir

        os.makedirs(self.vault_dir, exist_ok=True)

    def save_voice_print(self, name: str, embedding: np.ndarray) -> str:
        """Saves a voice embedding to the vault."""
        try:
            path = os.path.join(self.vault_dir, f"{name}.npy")
            np.save(path, embedding)
            logger.success(f"[BiometricVault] ✅ Voice print saved for {name} at {path}")
            return path
        except Exception as e:
            logger.error(f"[BiometricVault] Error saving voice print: {e}")
            raise e

    def get_voice_print(self, name: str) -> Optional[np.ndarray]:
        """Retrieves a voice embedding from the vault."""
        try:
            path = os.path.join(self.vault_dir, f"{name}.npy")
            if os.path.exists(path):
                return np.load(path)
            return None
        except Exception as e:
            logger.error(f"[BiometricVault] Error retrieving voice print for {name}: {e}")
            return None

    def list_enrolled_users(self) -> list[str]:
        """Lists all users with enrolled biometric data."""
        return [f[:-4] for f in os.listdir(self.vault_dir) if f.endswith(".npy")]

# Singleton for app-wide use
biometric_vault = BiometricVault()
