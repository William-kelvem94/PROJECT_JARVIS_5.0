import os
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    As Leis da RobÃ³tica - Singularity Edition.
    Regras imutÃ¡veis de proteÃ§Ã£o para caminhos crÃ­ticos e exfiltraÃ§Ã£o de dados.
    """
    # ZONAS DE PROTEÇÃO (Jaula de Vidro)
    CRITICAL_ZONES = [
        r"C:\Windows", r"C:\Program Files", r"C:\Program Files (x86)",
        r"C:\Users\Public", r"C:\Recovery"
    ]
    
    SYSTEM_SCRIPTS = [
        "SINGULARITY_LAUNCHER.py", "kill_switch.py", "security_manager.py",
        "main.py", "universal_recovery_manager.py"
    ]

    # Whitelist de comandos permitidos
    ALLOWED_COMMANDS = [
        "shutdown", "taskkill", "net", "ipconfig", "ping", "tracert",
        "systeminfo", "whoami", "hostname", "echo", "dir", "type",
        "find", "findstr", "fc", "comp", "copy", "move", "del", "rd",
        "md", "ren", "attrib", "xcopy", "robocopy", "schtasks"
    ]

    @staticmethod
    def safe_execute_command(command: str, allowed_commands: List[str] = None) -> subprocess.CompletedProcess:
        """
        Execute command with whitelist validation to prevent command injection.
        
        Args:
            command: The command string to execute
            allowed_commands: List of allowed command prefixes (defaults to ALLOWED_COMMANDS)
            
        Returns:
            subprocess.CompletedProcess object
            
        Raises:
            SecurityError: If command is not in whitelist
        """
        if allowed_commands is None:
            allowed_commands = SecurityManager.ALLOWED_COMMANDS
            
        # Validate command is in whitelist
        command_lower = command.lower().strip()
        if not any(cmd in command_lower for cmd in allowed_commands):
            logger.error(f"Command not in whitelist: {command}")
            raise SecurityError(f"Command not allowed: {command}")
        
        # Execute with shell=False for security
        try:
            result = subprocess.run(
                command, 
                shell=False, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            raise
        except Exception as e:
            logger.error(f"Command execution failed: {command} - {e}")
            raise

    @staticmethod
    def validate_path_access(path: str, mod_type: str = 'read') -> bool:
        """
        Valida acesso ao sistema de arquivos.
        'read': Pode ler quase tudo fora de Windows/ProgramFiles.
        'write': Só pode escrever em pastas do usuário ou diretório do projeto, fora do core.
        """
        if not path or not isinstance(path, str): return False
        
        abs_path = os.path.abspath(path.strip())
        
        # 1. Regra Universal: Bloqueio de Zonas Críticas
        for zone in SecurityManager.CRITICAL_ZONES:
            if abs_path.lower().startswith(zone.lower()):
                return False
        
        # 2. Regra de Escrita: Proteção de Scripts do Núcleo
        if mod_type == 'write':
            # Bloqueia edição direta de scripts protegidos
            filename = os.path.basename(abs_path)
            if filename in SecurityManager.SYSTEM_SCRIPTS:
                return False
                
            # Bloqueia escrita em C:\ diretamente (root do drive)
            if len(abs_path.split(os.sep)) <= 2:
                return False
                
        return True

    @staticmethod
    def validate_web_request(url: str) -> bool:
        """Bloqueia exfiltraÃ§Ã£o de dados para domÃ­nios desconhecidos"""
        allowed = ["google.com", "googleapis.com", "openai.com", "localhost", "127.0.0.1"]
        return any(domain in url for domain in allowed)

class SecurityError(Exception):
    """Custom exception for security violations"""
    pass

# Singleton instance
security_manager = SecurityManager()
