import hashlib
import platform
import subprocess
import uuid
from functools import lru_cache

from loguru import logger


class SentinelSecurity:
    """
    Sentinel v3 Security Core
    HWID real via hardware fingerprint.
    Biometric encryption mantida desativada (modo SHIM).
    LLM Command Validation ATIVA.
    """

    def __init__(self, blackbox_instance=None):
        self.blackbox = blackbox_instance
        self._hwid_cache: str | None = None

    def _collect_hardware_fingerprint(self) -> str:
        """Coleta dados únicos de hardware para gerar HWID."""
        parts = []

        # 1. UUID da placa-mãe (Windows WMIC)
        try:
            result = subprocess.run(
                ["wmic", "csproduct", "get", "UUID"],
                capture_output=True, text=True, timeout=5
            )
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and l.strip() != "UUID"]
            if lines:
                parts.append(lines[0])
        except Exception:
            pass

        # 2. Endereço MAC (via uuid.getnode — cross-platform)
        try:
            mac = uuid.getnode()
            if mac != 0 and (mac >> 40) % 2 == 0:  # bit multicast = 0 → MAC real
                parts.append(hex(mac))
        except Exception:
            pass

        # 3. Nome do processador (Windows WMIC)
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "Name"],
                capture_output=True, text=True, timeout=5
            )
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and l.strip() != "Name"]
            if lines:
                parts.append(lines[0])
        except Exception:
            pass

        # 4. Fallback: hostname + platform como último recurso
        if not parts:
            parts.append(platform.node())
            parts.append(platform.processor() or "unknown")

        return "|".join(parts)

    def get_hwid(self) -> str:
        """Retorna fingerprint único do hardware como hex string de 16 chars."""
        if self._hwid_cache:
            return self._hwid_cache

        try:
            raw = self._collect_hardware_fingerprint()
            if not raw.strip():
                raise ValueError("fingerprint vazio")
            digest = hashlib.sha256(raw.encode()).hexdigest()
            self._hwid_cache = digest[:16].upper()
            logger.info(f"[Sentinel] HWID gerado: {self._hwid_cache}")
        except Exception as e:
            logger.warning(f"[Sentinel] Falha ao gerar HWID real: {e}. Usando fallback.")
            self._hwid_cache = hashlib.sha256(platform.node().encode()).hexdigest()[:16].upper()

        return self._hwid_cache

    def derive_system_key(self) -> str:
        """Deriva chave de sistema baseada no HWID real."""
        hwid = self.get_hwid()
        _SALT = "JARVIS-SENTINEL-V3-2026"
        key_material = f"{hwid}:{_SALT}"
        return hashlib.sha256(key_material.encode()).hexdigest()[:32]

    async def validate_llm_command(self, command: str, parser, intent_data: dict = None) -> bool:
        """
        CRITICAL: Esta função é PRESERVADA.
        Validação de comandos LLM deve permanecer ativa para segurança do sistema.
        """
        if not command:
            return True

        is_safe = parser.validate_command(command, intent_data)
        if not is_safe:
            logger.warning(f"[SENTINEL ALERT] Comando bloqueado: {command}")
            if not intent_data:
                logger.warning("Motivo: Justificativa JSON ausente para operação privilegiada.")
            else:
                logger.warning(f"Motivo: Intent inválido. Raciocínio: {intent_data.get('reasoning')}")

        return is_safe

    def authenticate_user_biometric(self, user_id: str, b_type: str, b_hash: bytes) -> bool:
        """Bypass biométrico mantido ativo (modo SHIM)."""
        logger.info(f"[Security] Biometric bypass for user: {user_id}")
        return True
