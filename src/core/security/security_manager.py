import os

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
        "main.py", "auto_recovery_system.py"
    ]

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

# Singleton instance
security_manager = SecurityManager()
