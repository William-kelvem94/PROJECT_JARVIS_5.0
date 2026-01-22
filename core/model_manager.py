"""
Model Manager - Gerenciador de Múltiplos Modelos
Roteamento inteligente baseado em tipo de tarefa
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from core.local_llm import LocalLLM
from core.logger import logger

class ModelType(Enum):
    """Tipos de modelos disponíveis."""
    CODE = "code"  # Para programação
    CHAT = "chat"  # Para conversação
    MULTIMODAL = "multimodal"  # Para análise de imagens
    GENERAL = "general"  # Uso geral

class ModelManager:
    """
    Gerenciador de múltiplos modelos LLM.
    Roteia requisições para o modelo mais adequado.
    """
    
    def __init__(self, base_url: str = None):
        """
        Inicializa gerenciador de modelos.
        
        Args:
            base_url: URL base do Ollama
        """
        self.base_url = base_url
        self.models: Dict[str, LocalLLM] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Mapeamento de tipos de tarefa para modelos
        self.task_model_map = {
            ModelType.CODE: ["codellama:7b", "deepseek-coder:6.7b", "starcoder:1b"],
            ModelType.CHAT: ["llama3:8b", "mistral:7b", "neural-chat:7b"],
            ModelType.GENERAL: ["llama3:8b", "codellama:7b", "mistral:7b"]
        }
        
        logger.info("ModelManager inicializado")
    
    def register_model(self, model_name: str, model_type: ModelType = ModelType.GENERAL):
        """
        Registra um modelo no gerenciador.
        
        Args:
            model_name: Nome do modelo
            model_type: Tipo do modelo
        """
        try:
            llm = LocalLLM(model=model_name, base_url=self.base_url)
            self.models[model_name] = llm
            self.model_metadata[model_name] = {
                "type": model_type,
                "name": model_name,
                "available": True
            }
            logger.info(f"Modelo registrado: {model_name} ({model_type.value})")
        except Exception as e:
            logger.error(f"Erro ao registrar modelo {model_name}: {e}")
    
    def get_best_model(self, task_type: ModelType, prefer_model: Optional[str] = None) -> Optional[LocalLLM]:
        """
        Retorna o melhor modelo para uma tarefa.
        
        Args:
            task_type: Tipo de tarefa
            prefer_model: Modelo preferido (se disponível)
        
        Returns:
            Instância do LLM ou None
        """
        # Se modelo preferido especificado e disponível, usar
        if prefer_model and prefer_model in self.models:
            if self.model_metadata[prefer_model]["available"]:
                return self.models[prefer_model]
        
        # Buscar melhor modelo para o tipo de tarefa
        candidates = self.task_model_map.get(task_type, self.task_model_map[ModelType.GENERAL])
        
        for candidate in candidates:
            if candidate in self.models and self.model_metadata[candidate]["available"]:
                return self.models[candidate]
        
        # Fallback: primeiro modelo disponível
        for model_name, llm in self.models.items():
            if self.model_metadata[model_name]["available"]:
                return llm
        
        return None
    
    def detect_task_type(self, message: str) -> ModelType:
        """
        Detecta o tipo de tarefa baseado na mensagem.
        
        Args:
            message: Mensagem do usuário
        
        Returns:
            Tipo de tarefa detectado
        """
        message_lower = message.lower()
        
        # Palavras-chave para código
        code_keywords = ["código", "programa", "função", "classe", "def", "import", "python", "javascript", "html", "css", "api", "json", "debug", "erro", "bug"]
        
        # Palavras-chave para chat
        chat_keywords = ["olá", "oi", "ajuda", "explicar", "como funciona", "o que é", "conversar", "falar"]
        
        # Verificar palavras-chave
        code_score = sum(1 for keyword in code_keywords if keyword in message_lower)
        chat_score = sum(1 for keyword in chat_keywords if keyword in message_lower)
        
        if code_score > chat_score and code_score > 0:
            return ModelType.CODE
        elif chat_score > 0:
            return ModelType.CHAT
        else:
            return ModelType.GENERAL
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """Retorna lista de modelos disponíveis."""
        return [
            {
                "name": name,
                "type": meta["type"].value,
                "available": meta["available"]
            }
            for name, meta in self.model_metadata.items()
        ]

