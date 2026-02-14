import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class UserManager:
    """
    JARVIS 5.0 - Identity & User Management System
    Handles multi-user profiles, authorization levels, and registration flows.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.data_dir = Path("data/users")
        self.users_file = self.data_dir / "users_registry.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.users = self._load_users()
        
        # Garantir que o William (Master) esteja sempre lá se for o primeiro boot
        if not self.users:
            self.register_user("William", "Master/Owner", role="master")
            
        logger.info(f"✅ UserManager inicializado. {len(self.users)} usuários cadastrados.")

    def _load_users(self) -> Dict[str, Any]:
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar registro de usuários: {e}")
                return {}
        return {}

    def save_users(self):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar registro de usuários: {e}")

    def register_user(self, name: str, relationship: str, role: str = "trusted", workspace_path: Optional[str] = None) -> bool:
        """
        Adiciona ou atualiza um usuário no registro.
        Se workspace_path for fornecido, o usuário usará esse caminho em vez do padrão.
        """
        name_key = name.lower().strip()
        user_path = self.data_dir / name_key
        
        target_workspace = workspace_path if workspace_path else str(user_path / "workspace")

        if name_key not in self.users:
            self.users[name_key] = {
                "name": name,
                "relationship": relationship,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "last_seen": None,
                "biometrics": {
                    "face": False,
                    "voice": False
                },
                "dirs": {
                    "base": str(user_path),
                    "workspace": target_workspace,
                    "biometrics": str(user_path / "biometrics")
                }
            }
            # Criar estrutura de diretórios
            Path(self.users[name_key]["dirs"]["workspace"]).mkdir(parents=True, exist_ok=True)
            Path(self.users[name_key]["dirs"]["biometrics"]).mkdir(parents=True, exist_ok=True)
            logger.info(f"👤 Novo usuário registrado: {name} ({relationship}) -> Workspace: {target_workspace}")
        else:
            self.users[name_key]["relationship"] = relationship
            self.users[name_key]["role"] = role
            if workspace_path:
                self.users[name_key]["dirs"]["workspace"] = workspace_path
            logger.info(f"👤 Usuário atualizado: {name}")
            
        self.save_users()
        return True

    def relocate_user(self, name: str, new_workspace_path: str) -> bool:
        """Move um usuário para um novo workspace (compartilhado ou exclusivo)"""
        name_key = name.lower().strip()
        if name_key in self.users:
            old_path = self.users[name_key]["dirs"]["workspace"]
            self.users[name_key]["dirs"]["workspace"] = str(Path(new_workspace_path).absolute())
            Path(new_workspace_path).mkdir(parents=True, exist_ok=True)
            self.save_users()
            logger.info(f"🔄 Usuário {name} realocado: {old_path} -> {new_workspace_path}")
            return True
        return False

    def update_biometrics(self, name: str, face: bool = None, voice: bool = None):
        name_key = name.lower().strip()
        if name_key in self.users:
            if face is not None: self.users[name_key]["biometrics"]["face"] = face
            if voice is not None: self.users[name_key]["biometrics"]["voice"] = voice
            self.save_users()

    def record_presence(self, name: str):
        name_key = name.lower().strip()
        if name_key in self.users:
            self.users[name_key]["last_seen"] = datetime.now().isoformat()
            self.save_users()

    def get_user(self, name: str) -> Optional[Dict[str, Any]]:
        return self.users.get(name.lower().strip())

    def is_authorized(self, name: str) -> bool:
        user = self.get_user(name)
        if not user: return False
        return user.get("role") in ["master", "trusted", "guest_authorized"]

    def get_all_authorized_names(self) -> List[str]:
        return [u["name"] for u in self.users.values() if u["role"] in ["master", "trusted"]]

# Instância global
user_manager = UserManager()
