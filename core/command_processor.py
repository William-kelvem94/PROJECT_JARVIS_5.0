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
                r'abrir\s+(.+)',
                r'abrir\s+aplicativo\s+(.+)',
                r'execute\s+(.+)',
                r'iniciar\s+(.+)',
                r'rodar\s+(.+)',
                r'(.+)\s+app',
                r'(.+)\s+aplicativo',
            ],
            'read_file': [
                r'ler\s+arquivo\s+(.+)',
                r'ler\s+(.+)',
                r'leia\s+(.+)',
                r'abrir\s+arquivo\s+(.+)',
                r'mostrar\s+conteúdo\s+de\s+(.+)',
                r'conteúdo\s+do\s+arquivo\s+(.+)',
            ],
            'list_files': [
                r'listar\s+arquivos',
                r'listar\s+arquivos\s+(.+)',
                r'arquivos\s+na\s+(.+)',
                r'arquivos\s+em\s+(.+)',
                r'mostrar\s+arquivos',
                r'mostrar\s+arquivos\s+(.+)',
                r'lista\s+de\s+arquivos',
                r'arquivos\s+da\s+(.+)',
            ],
            'organize_files': [
                r'organizar\s+arquivos',
                r'organizar\s+arquivos\s+(.+)',
                r'organize\s+arquivos',
                r'organizar\s+(.+)',
                r'ordenar\s+arquivos',
            ],
            'system_info': [
                r'status\s+do\s+sistema',
                r'status\s+do\s+pc',
                r'informações\s+do\s+pc',
                r'informações\s+do\s+sistema',
                r'info\s+do\s+computador',
                r'especificações',
                r'especificações\s+do\s+pc',
            ],
            'execute_command': [
                r'executar\s+comando\s+(.+)',
                r'rodar\s+comando\s+(.+)',
                r'cmd\s+(.+)',
                r'comando\s+(.+)',
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

