"""
Módulo de Texto - Interface de Chat
Gerencia entrada de texto via diferentes interfaces
"""

from typing import Optional, Callable, Dict, Any
from core.logger import logger

class TextModule:
    """
    Módulo de entrada de texto.
    Gerencia entrada via diferentes interfaces (web, CLI, etc.)
    """
    
    def __init__(self):
        self.message_handlers = []
        logger.info("TextModule inicializado")
    
    def register_handler(self, handler: Callable[[str], Any]):
        """
        Registra um handler para processar mensagens de texto.
        
        Args:
            handler: Função que recebe texto e retorna resposta
        """
        self.message_handlers.append(handler)
        logger.info(f"Handler registrado: {handler.__name__}")
    
    def process_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa entrada de texto.
        
        Args:
            text: Texto de entrada
            context: Contexto adicional (opcional)
        
        Returns:
            Dicionário com resposta e metadados
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Texto vazio",
                "response": None
            }
        
        logger.info(f"Processando texto: {text[:50]}...")
        
        # Processar com todos os handlers registrados
        responses = []
        for handler in self.message_handlers:
            try:
                result = handler(text, context)
                if result:
                    responses.append(result)
            except Exception as e:
                logger.error(f"Erro no handler {handler.__name__}: {e}")
        
        return {
            "success": True,
            "input": text,
            "responses": responses,
            "context": context or {}
        }
    
    def is_available(self) -> bool:
        """Sempre disponível - texto pode ser processado."""
        return True

