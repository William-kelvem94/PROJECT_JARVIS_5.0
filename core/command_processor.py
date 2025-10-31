# Processador de Comandos Inteligente

import re
from typing import Dict, Any, Optional, List
from core.logger import logger

class CommandProcessor:
    """
    Processa e identifica comandos/intenções nas mensagens do usuário.
    """
    
    def __init__(self):
        self.commands = {
            'open_app': [
                r'abrir\s+(\w+)',
                r'execute\s+(\w+)',
                r'iniciar\s+(\w+)',
                r'rodar\s+(\w+)',
                r'(\w+)\s+app',
            ],
            'read_file': [
                r'ler\s+arquivo\s+(.+)',
                r'leia\s+(.+)',
                r'abrir\s+arquivo\s+(.+)',
                r'mostrar\s+conteúdo\s+de\s+(.+)',
            ],
            'list_files': [
                r'listar\s+arquivos',
                r'arquivos\s+na\s+(.+)',
                r'mostrar\s+arquivos',
                r'lista\s+de\s+arquivos',
            ],
            'organize_files': [
                r'organizar\s+arquivos',
                r'organize\s+arquivos',
                r'organizar\s+(.+)',
            ],
            'system_info': [
                r'status\s+do\s+sistema',
                r'informações\s+do\s+pc',
                r'info\s+do\s+computador',
                r'especificações',
            ],
            'execute_command': [
                r'executar\s+comando\s+(.+)',
                r'rodar\s+comando\s+(.+)',
                r'cmd\s+(.+)',
            ],
        }
    
    def process(self, message: str) -> Dict[str, Any]:
        """
        Processa a mensagem e retorna intenção detectada.
        Retorna None se não for um comando.
        """
        message_lower = message.lower().strip()
        
        # Verificar cada tipo de comando
        for command_type, patterns in self.commands.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    return {
                        'type': command_type,
                        'args': match.groups() if match.groups() else [],
                        'original': message
                    }
        
        return None

