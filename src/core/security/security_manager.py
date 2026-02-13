import os

class SecurityManager:
    """
    As Leis da Robótica - Singularity Edition.
    Regras imutáveis de proteção para caminhos críticos e exfiltração de dados.
    """
    FORBIDDEN_PATHS = [
        r"C:\Windows", r"C:\Program Files", r"C:\Program Files (x86)",
        "SINGULARITY_LAUNCHER.py", "kill_switch.py", "security_manager.py"
    ]
    
    @staticmethod
    def validate_path_access(path: str) -> bool:
        """Retorna False se o caminho for proibido (Anti-Genesis)"""
        if not path or not isinstance(path, str) or not path.strip():
            return False
            
        try:
            abs_path = os.path.abspath(path.strip())
            for forbidden in SecurityManager.FORBIDDEN_PATHS:
                if forbidden.lower() in abs_path.lower():
                    return False
            return True
        except Exception:
            return False

    @staticmethod
    def validate_web_request(url: str) -> bool:
        """Bloqueia exfiltração de dados para domínios desconhecidos"""
        allowed = ["google.com", "googleapis.com", "openai.com", "localhost", "127.0.0.1"]
        return any(domain in url for domain in allowed)
