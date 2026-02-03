"""
Gerenciador de Segurança (Gatekeeper)
Controla permissões para ações sensíveis e autônomas do Jarvis.
"""

import logging
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
import threading

logger = logging.getLogger(__name__)

class SecurityManager:
    """Gatekeeper para ações sensíveis do Jarvis"""

    def __init__(self):
        self.auto_mode = False # Se True, aprova tudo (Perigoso - Modo Dev)
        self.trusted_domains = ["google.com", "stackoverflow.com", "github.com", "python.org"]
        
    def request_permission(self, action_type: str, details: str) -> bool:
        """
        Solicita permissão ao usuário para realizar uma ação.
        Retorna True se aprovado, False se negado.
        """
        if self.auto_mode:
            logger.warning(f"Ação AUTO-APROVADA (Modo Dev): {action_type} - {details}")
            return True

        logger.info(f"Solicitando permissão para: {action_type} - {details}")
        
        # Usar dialog nativo do Windows (bloqueante) via thread separada para não travar main
        # Nota: Idealmente seria integrado na GUI do Jarvis, mas aqui usamos um MessageBox simples por segurança
        
        result = [False]
        event = threading.Event()

        def _ask():
            root = tk.Tk()
            root.withdraw() # Esconder janela principal
            root.attributes("-topmost", True) # Sempre no topo
            
            answer = messagebox.askyesno(
                title="Jarvis Security Gatekeeper",
                message=f"JARVIS solicita permissão para:\n\n[{action_type}]\n{details}\n\nAutorizar?",
                icon='warning'
            )
            result[0] = answer
            root.destroy()
            event.set()

        # Rodar na thread principal ou dedicada de UI
        # Como estamos no backend, criamos uma thread temporária para o dialog
        t = threading.Thread(target=_ask)
        t.start()
        t.join() # Esperar resposta
        
        if result[0]:
            logger.info("Permissão CONCEDIDA pelo usuário.")
            return True
        else:
            logger.warning("Permissão NEGADA pelo usuário.")
            return False

    def validate_web_search(self, query: str) -> bool:
        """Valida busca na web"""
        # Filtros de segurança básicos podem ser adicionados aqui
        return self.request_permission("WEB_SEARCH", f"Buscar no Google: '{query}'")

    def validate_file_edit(self, file_path: str, reason: str) -> bool:
        """Valida edição de arquivo"""
        return self.request_permission("FILE_EDIT", f"Editar arquivo: {file_path}\nMotivo: {reason}")

    def validate_shell_command(self, command: str) -> bool:
        """Valida execução de comando shell"""
        return self.request_permission("SHELL_EXEC", f"Executar comando: '{command}'")

# Instância global
security_manager = SecurityManager()
