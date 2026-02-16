"""
Security Manager - Sistema de SeguranÃ§a AvanÃ§ado
Implementa criptografia, controle de acesso e modo privado
"""

import logging
import os
import json
import hashlib
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecurityLevel:
    """NÃ­veis de seguranÃ§a"""

    PUBLIC = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class SecurityManager:
    """Gerenciador de seguranÃ§a e privacidade"""

    def __init__(self, config_dir: str = ".jarvis_security"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.encryption_key = None
        self.private_mode = False
        self.audit_log_enabled = True
        self.audit_log_path = self.config_dir / "audit.log"

        self.permissions = {
            "file_read": True,
            "file_write": False,  # Requer confirmaÃ§Ã£o
            "file_delete": False,  # Requer confirmaÃ§Ã£o
            "system_control": False,  # Requer confirmaÃ§Ã£o
            "network_access": True,
        }

        self._load_or_create_key()
        self._init_audit_log()

    def _load_or_create_key(self):
        """Carrega ou cria chave de criptografia"""
        key_file = self.config_dir / "encryption.key"

        try:
            if key_file.exists():
                with open(key_file, "rb") as f:
                    self.encryption_key = f.read()
                logger.info("âœ… Chave de criptografia carregada")
            else:
                # Gerar nova chave
                self.encryption_key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(self.encryption_key)
                # Proteger arquivo (apenas leitura)
                os.chmod(key_file, 0o400)
                logger.info("âœ… Nova chave de criptografia gerada")
        except Exception as e:
            logger.error(f"Erro ao gerenciar chave: {e}")

    def _init_audit_log(self):
        """Inicializa log de auditoria"""
        if not self.audit_log_path.exists():
            self.audit_log_path.touch()
            logger.info("âœ… Log de auditoria criado")

    def encrypt_data(self, data: str) -> Optional[str]:
        """
        Criptografa dados usando AES-256 (via Fernet)

        Args:
            data: Dados em texto plano

        Returns:
            Dados criptografados (base64)
        """
        try:
            fernet = Fernet(self.encryption_key)
            encrypted = fernet.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erro ao criptografar: {e}")
            return None

    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """
        Descriptografa dados

        Args:
            encrypted_data: Dados criptografados (base64)

        Returns:
            Dados em texto plano
        """
        try:
            fernet = Fernet(self.encryption_key)
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            return None

    def hash_data(self, data: str, algorithm: str = "sha256") -> str:
        """
        Gera hash de dados

        Args:
            data: Dados para hash
            algorithm: Algoritmo (sha256, sha512, md5)

        Returns:
            Hash hexadecimal
        """
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data.encode()).hexdigest()
        else:
            raise ValueError(f"Algoritmo nÃ£o suportado: {algorithm}")

    def validate_file_action(
        self, file_path: str, action: str, require_confirmation: bool = True
    ) -> bool:
        """
        Valida se uma aÃ§Ã£o em arquivo Ã© permitida

        Args:
            file_path: Caminho do arquivo
            action: 'read', 'write', 'delete'
            require_confirmation: Se True, requer confirmaÃ§Ã£o do usuÃ¡rio

        Returns:
            True se permitido
        """
        # Verificar modo privado
        if self.private_mode and action in ["write", "delete"]:
            logger.warning(
                f"ðŸ”’ AÃ§Ã£o bloqueada em modo privado: {action} em {file_path}"
            )
            self.log_audit("BLOCKED", f"{action} em {file_path} (modo privado)")
            return False

        # Verificar permissÃµes
        permission_key = f"file_{action}"
        if not self.permissions.get(permission_key, False):
            logger.warning(f"ðŸ”’ PermissÃ£o negada: {action} em {file_path}")
            self.log_audit("DENIED", f"{action} em {file_path}")
            return False

        # Verificar caminhos sensÃ­veis
        sensitive_paths = [
            "C:\\Windows",
            "C:\\Program Files",
            "/etc",
            "/usr",
            "/System",
        ]

        for sensitive in sensitive_paths:
            if file_path.startswith(sensitive):
                logger.warning(f"ðŸ”’ Caminho sensÃ­vel bloqueado: {file_path}")
                self.log_audit("BLOCKED", f"{action} em caminho sensÃ­vel: {file_path}")
                return False

        # Log da aÃ§Ã£o
        self.log_audit("ALLOWED", f"{action} em {file_path}")
        return True

    def enable_private_mode(self):
        """Ativa modo privado"""
        self.private_mode = True
        self.permissions["file_write"] = False
        self.permissions["file_delete"] = False
        self.permissions["network_access"] = False
        logger.info("ðŸ”’ Modo privado ATIVADO")
        self.log_audit("MODE_CHANGE", "Modo privado ativado")

    def disable_private_mode(self):
        """Desativa modo privado"""
        self.private_mode = False
        self.permissions["file_write"] = True
        self.permissions["network_access"] = True
        logger.info("ðŸ”“ Modo privado DESATIVADO")
        self.log_audit("MODE_CHANGE", "Modo privado desativado")

    def log_audit(self, event_type: str, description: str):
        """
        Registra evento no log de auditoria

        Args:
            event_type: Tipo do evento (ALLOWED, DENIED, BLOCKED, etc)
            description: DescriÃ§Ã£o do evento
        """
        if not self.audit_log_enabled:
            return

        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "type": event_type,
                "description": description,
            }

            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error(f"Erro ao registrar auditoria: {e}")

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retorna Ãºltimas entradas do log de auditoria

        Args:
            limit: NÃºmero mÃ¡ximo de entradas

        Returns:
            Lista de eventos
        """
        try:
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Pegar Ãºltimas N linhas
            recent_lines = lines[-limit:]

            events = []
            for line in recent_lines:
                try:
                    event = json.loads(line.strip())
                    events.append(event)
                except:
                    continue

            return events

        except Exception as e:
            logger.error(f"Erro ao ler log de auditoria: {e}")
            return []

    async def authenticate_user(self, face_encoding=None, password: str = None) -> bool:
        """
        Autentica usuário via FaceID (comparação real) ou senha (hash)
        """
        self.log_audit("AUTH", "Iniciando processo de autenticação")

        # 1. Autenticação por FaceID (Se disponível)
        if face_encoding is not None:
            try:
                import numpy as np
                import face_recognition

                # Carregar face do "William" (Dono)
                authorized_path = self.config_dir / "authorized_face.npy"
                if authorized_path.exists():
                    known_encoding = np.load(authorized_path)
                    results = face_recognition.compare_faces(
                        [known_encoding], face_encoding, tolerance=0.5
                    )

                    if results[0]:
                        logger.info("✅ Autenticação facial BEM-SUCEDIDA")
                        self.log_audit("AUTH_SUCCESS", "Reconhecimento facial: William")
                        return True
                    else:
                        logger.warning(
                            "❌ Reconhecimento facial FALHOU (Não autorizado)"
                        )
                        self.log_audit("AUTH_FAILURE", "Face não reconhecida")
            except ImportError:
                logger.error(
                    "❌ face_recognition ou numpy não instalados para Auth real"
                )
            except Exception as e:
                logger.error(f"Erro no processamento facial: {e}")

        # 2. Fallback por Senha (Se implementado)
        if password:
            stored_hash_path = self.config_dir / "pass.hash"
            if stored_hash_path.exists():
                with open(stored_hash_path, "r") as f:
                    stored_hash = f.read().strip()
                current_hash = self.hash_data(password)
                if current_hash == stored_hash:
                    logger.info("✅ Autenticação por senha BEM-SUCEDIDA")
                    return True

        # Se não houver dados de autorização salvos, permitimos para não travar o usuário
        # mas registramos o aviso. No Modo Singularity, isso deve ser configurado.
        if not (self.config_dir / "authorized_face.npy").exists():
            logger.info("ℹ️ Nenhum dado de autorização salvo. Acesso livre concedido.")
            return True

        return False

    def get_security_status(self) -> Dict[str, Any]:
        """Retorna status de seguranÃ§a do sistema"""
        return {
            "private_mode": self.private_mode,
            "encryption_enabled": self.encryption_key is not None,
            "audit_log_enabled": self.audit_log_enabled,
            "permissions": self.permissions.copy(),
            "audit_log_entries": len(self.get_audit_log()),
        }


# InstÃ¢ncia global removida para evitar execuÃ§Ã£o durante import
# security_manager = SecurityManager(config_dir="data/security")
