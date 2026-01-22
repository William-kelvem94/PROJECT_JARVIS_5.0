"""
Security Module - Sistema de segurança e permissões para JARVIS
Implementa whitelist de comandos, autenticação, sandboxing e confirmações
"""

import os
import re
import hashlib
import json
from typing import Dict, Any, Optional, List, Literal, Callable
from pathlib import Path
from datetime import datetime
from core.logger import logger


class PermissionLevel:
    """Níveis de permissão do sistema."""
    GUEST = 0      # Apenas leitura, sem acesso ao sistema
    USER = 1       # Acesso limitado, comandos seguros
    POWER_USER = 2 # Acesso avançado, alguns comandos de sistema
    ADMIN = 3      # Acesso completo ao sistema


class SecurityManager:
    """
    Gerenciador de segurança e permissões.
    Controla acesso a funcionalidades e comandos do sistema.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de segurança.
        
        Args:
            config_path: Caminho para arquivo de configuração de segurança
        """
        self.config_path = config_path or "./config/security.json"
        self.config = self._load_config()
        
        # Usuário atual e nível de permissão
        self.current_user = None
        self.current_permission_level = PermissionLevel.USER
        
        # Registro de comandos executados (audit log)
        self.audit_log_path = Path("./logs/audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Callbacks para confirmação
        self.confirmation_callback: Optional[Callable[[str], bool]] = None
        
        logger.info("SecurityManager inicializado")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração de segurança."""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar config de segurança: {e}")
        
        # Configuração padrão
        default_config = {
            "require_authentication": False,
            "enable_command_whitelist": True,
            "enable_sandboxing": True,
            "require_confirmation_for_critical": True,
            "max_failed_auth_attempts": 3,
            "session_timeout_minutes": 60,
            "allowed_commands": {
                PermissionLevel.GUEST: [
                    "search", "calculate", "weather", "time", "help", "info"
                ],
                PermissionLevel.USER: [
                    "search", "calculate", "weather", "time", "help", "info",
                    "open_app", "play_music", "set_reminder", "send_message"
                ],
                PermissionLevel.POWER_USER: [
                    # Todos do USER +
                    "file_operations", "system_info", "process_list", "network_info"
                ],
                PermissionLevel.ADMIN: [
                    # Acesso total
                    "*"
                ]
            },
            "critical_commands": [
                "delete_file", "delete_folder", "format", "shutdown", "reboot",
                "install_package", "uninstall_package", "kill_process",
                "registry_edit", "system_command"
            ],
            "blacklisted_patterns": [
                r"rm\s+-rf\s+/",
                r"del\s+/f\s+/q",
                r"format\s+c:",
                r"dd\s+if=",
                r"mkfs\.",
            ]
        }
        
        # Salvar configuração padrão
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Autentica usuário.
        
        Args:
            username: Nome de usuário
            password: Senha
        
        Returns:
            True se autenticado
        """
        if not self.config.get("require_authentication", False):
            # Autenticação desabilitada
            self.current_user = username
            return True
        
        # Hash da senha
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Verificar credenciais (simplificado - em produção usar sistema robusto)
        users = self.config.get("users", {})
        user_data = users.get(username)
        
        if user_data and user_data.get("password_hash") == password_hash:
            self.current_user = username
            self.current_permission_level = user_data.get("permission_level", PermissionLevel.USER)
            self._audit_log("authenticate", {"username": username, "success": True})
            logger.info(f"Usuário autenticado: {username}")
            return True
        
        self._audit_log("authenticate", {"username": username, "success": False})
        logger.warning(f"Falha na autenticação: {username}")
        return False
    
    def check_permission(self, command: str, action_type: str = "execute") -> bool:
        """
        Verifica se comando/ação tem permissão.
        
        Args:
            command: Comando a verificar
            action_type: Tipo de ação (execute, read, write, delete)
        
        Returns:
            True se permitido
        """
        # Verificar se whitelist está habilitada
        if not self.config.get("enable_command_whitelist", True):
            return True
        
        # Admin tem acesso total
        if self.current_permission_level == PermissionLevel.ADMIN:
            return True
        
        # Verificar whitelist do nível atual
        allowed = self.config.get("allowed_commands", {})
        level_commands = allowed.get(self.current_permission_level, [])
        
        # Verificar se comando está na lista permitida
        if "*" in level_commands or command in level_commands:
            return True
        
        logger.warning(f"Comando não permitido: {command} (nível: {self.current_permission_level})")
        return False
    
    def is_safe_command(self, command: str) -> tuple[bool, Optional[str]]:
        """
        Verifica se comando é seguro (não está na blacklist).
        
        Args:
            command: Comando a verificar
        
        Returns:
            (is_safe, reason) - True se seguro, False e motivo se não
        """
        # Verificar padrões perigosos
        blacklist = self.config.get("blacklisted_patterns", [])
        
        for pattern in blacklist:
            if re.search(pattern, command, re.IGNORECASE):
                reason = f"Comando contém padrão perigoso: {pattern}"
                logger.warning(f"Comando bloqueado: {command} - {reason}")
                return False, reason
        
        return True, None
    
    def requires_confirmation(self, command: str) -> bool:
        """
        Verifica se comando requer confirmação do usuário.
        
        Args:
            command: Comando a verificar
        
        Returns:
            True se requer confirmação
        """
        if not self.config.get("require_confirmation_for_critical", True):
            return False
        
        critical_commands = self.config.get("critical_commands", [])
        
        # Verificar se comando está na lista crítica
        for critical in critical_commands:
            if critical in command.lower():
                return True
        
        return False
    
    def request_confirmation(self, command: str, description: str) -> bool:
        """
        Solicita confirmação do usuário para comando crítico.
        
        Args:
            command: Comando a executar
            description: Descrição da ação
        
        Returns:
            True se confirmado
        """
        logger.warning(f"Confirmação requerida para: {command}")
        
        # Usar callback se disponível
        if self.confirmation_callback:
            return self.confirmation_callback(description)
        
        # Fallback para input simples
        print(f"\n⚠️  ATENÇÃO: Ação crítica detectada!")
        print(f"Comando: {command}")
        print(f"Descrição: {description}")
        response = input("Deseja continuar? (sim/não): ").strip().lower()
        
        confirmed = response in ["sim", "yes", "s", "y"]
        
        self._audit_log("confirmation", {
            "command": command,
            "description": description,
            "confirmed": confirmed
        })
        
        return confirmed
    
    def execute_with_sandbox(self, command: str, allowed_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Executa comando em ambiente sandboxed (isolado).
        
        Args:
            command: Comando a executar
            allowed_paths: Lista de caminhos permitidos
        
        Returns:
            Resultado da execução
        """
        if not self.config.get("enable_sandboxing", True):
            # Sandboxing desabilitado - executar diretamente (não recomendado)
            logger.warning("Sandboxing desabilitado - executando comando diretamente")
            return self._execute_direct(command)
        
        # Implementar sandboxing
        # TODO: Integrar com Docker ou outras ferramentas de isolamento
        logger.info(f"Executando em sandbox: {command}")
        
        # Por enquanto, apenas logar e simular
        return {
            "success": False,
            "message": "Sandboxing não implementado ainda",
            "sandbox_enabled": True
        }
    
    def _execute_direct(self, command: str) -> Dict[str, Any]:
        """Executa comando diretamente (sem sandbox)."""
        import subprocess
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _audit_log(self, action: str, details: Dict[str, Any]):
        """
        Registra ação no log de auditoria.
        
        Args:
            action: Tipo de ação
            details: Detalhes da ação
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "user": self.current_user or "anonymous",
                "permission_level": self.current_permission_level,
                "action": action,
                "details": details
            }
            
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        
        except Exception as e:
            logger.error(f"Erro ao registrar audit log: {e}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera entradas do log de auditoria.
        
        Args:
            limit: Número máximo de entradas
        
        Returns:
            Lista de entradas do log
        """
        if not self.audit_log_path.exists():
            return []
        
        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Pegar últimas N linhas
            recent_lines = lines[-limit:]
            
            logs = []
            for line in recent_lines:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
            
            return logs
        
        except Exception as e:
            logger.error(f"Erro ao ler audit log: {e}")
            return []
    
    def set_permission_level(self, level: int):
        """Define nível de permissão do usuário atual."""
        self.current_permission_level = level
        logger.info(f"Nível de permissão alterado para: {level}")
    
    def set_confirmation_callback(self, callback: Callable[[str], bool]):
        """Define callback para confirmações."""
        self.confirmation_callback = callback
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de segurança."""
        return {
            "current_user": self.current_user,
            "permission_level": self.current_permission_level,
            "authentication_required": self.config.get("require_authentication", False),
            "whitelist_enabled": self.config.get("enable_command_whitelist", True),
            "sandboxing_enabled": self.config.get("enable_sandboxing", True),
            "confirmation_enabled": self.config.get("require_confirmation_for_critical", True),
            "audit_log_entries": len(self.get_audit_log())
        }
