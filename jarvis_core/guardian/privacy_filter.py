"""
Guardian - Privacy Filter
Filtra dados sensíveis antes de enviar para nuvem
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PrivacyFilter:
    """Filtro de privacidade"""
    
    def __init__(self):
        # Padrões regex
        self.patterns = {
            "cpf": r'\d{3}\.\d{3}\.\d{3}-\d{2}',
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "phone": r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}',
            "credit_card": r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
            "ip_address": r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        }
        
        # Palavras-chave sensíveis
        self.sensitive_keywords = [
            "senha", "password", "token", "api_key", "secret",
            "private_key", "credential", "auth"
        ]
    
    def filter_text(self, text: str) -> Tuple[str, List[str]]:
        """Filtra texto e retorna (texto_filtrado, tipos_encontrados)"""
        filtered_text = text
        found_types = []
        
        # Aplicar padrões regex
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            
            if matches:
                found_types.append(pattern_name)
                # Substituir por ***
                filtered_text = re.sub(pattern, f"[{pattern_name.upper()}_REDACTED]", filtered_text)
        
        # Verificar palavras-chave
        for keyword in self.sensitive_keywords:
            if keyword in text.lower():
                found_types.append(f"keyword_{keyword}")
                # Ofuscar linha inteira que contém a palavra
                lines = filtered_text.split('\n')
                filtered_lines = []
                
                for line in lines:
                    if keyword in line.lower():
                        filtered_lines.append(f"[SENSITIVE_LINE_REDACTED]")
                    else:
                        filtered_lines.append(line)
                
                filtered_text = '\n'.join(filtered_lines)
        
        if found_types:
            logger.warning(f"🔒 Dados sensíveis filtrados: {found_types}")
        
        return filtered_text, found_types
    
    def is_safe_to_send(self, text: str) -> bool:
        """Verifica se é seguro enviar para nuvem"""
        _, found_types = self.filter_text(text)
        return len(found_types) == 0


# Instância global
privacy_filter = PrivacyFilter()


# Teste
if __name__ == "__main__":
    filter = PrivacyFilter()
    
    test_text = """
    Meu CPF é 123.456.789-00
    Email: teste@example.com
    Senha: minha_senha_secreta
    Telefone: (11) 98765-4321
    """
    
    filtered, types = filter.filter_text(test_text)
    
    print("Original:")
    print(test_text)
    print("\nFiltrado:")
    print(filtered)
    print(f"\nTipos encontrados: {types}")
