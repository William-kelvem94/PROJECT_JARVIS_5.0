# Integração com Ollama - Modelos LLM Locais Gratuitos

import requests
import json
import os
from typing import Optional, Dict, Any
from core.logger import logger

class LocalLLM:
    """
    Integração com Ollama para modelos LLM locais gratuitos.
    Suporta: codellama, deepseek-coder, llama2, mistral, etc.
    """
    
    def __init__(self, 
                 base_url: str = None, 
                 model: str = "codellama:7b",
                 timeout: int = 120):
        """
        Inicializa a conexão com Ollama.
        
        Args:
            base_url: URL base do Ollama (padrão: http://localhost:11434 ou http://ollama:11434 no Docker)
            model: Nome do modelo a ser usado
            timeout: Timeout para requisições em segundos
        """
        # Configuração automática baseada no ambiente
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', model)
        self.timeout = timeout
        self.api_url = f"{self.base_url}/api"
        
        logger.info(f"LocalLLM inicializado: {self.base_url} | Modelo: {self.model}")
        
        # Verificar conexão com Ollama
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Verifica se o Ollama está rodando e acessível."""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"Ollama conectado! Modelos disponíveis: {[m.get('name') for m in models]}")
                
                # Verificar se o modelo está disponível
                model_names = [m.get('name') for m in models]
                if self.model not in model_names:
                    logger.warning(f"Modelo {self.model} não encontrado. Use 'ollama pull {self.model}' para baixar.")
                
                return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao conectar com Ollama em {self.base_url}: {e}")
            logger.error("Certifique-se de que o Ollama está rodando!")
            return False
    
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """
        Gera uma resposta do modelo LLM.
        
        Args:
            prompt: Prompt do usuário
            system: Mensagem de sistema (opcional)
            **kwargs: Parâmetros adicionais (temperature, top_p, etc.)
        
        Returns:
            Resposta gerada pelo modelo
        """
        try:
            # Preparar payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "top_p": kwargs.get('top_p', 0.9),
                    "top_k": kwargs.get('top_k', 40),
                    "num_predict": kwargs.get('max_tokens', 256)
                }
            }
            
            # Adicionar contexto de sistema se fornecido
            if system:
                payload["system"] = system
            
            # Fazer requisição
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Erro: Resposta vazia do modelo')
            else:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logger.error(error_msg)
                return f"Erro ao gerar resposta: {error_msg}"
                
        except requests.exceptions.Timeout:
            logger.error("Timeout ao gerar resposta. Modelo pode estar ocupado.")
            return "Timeout: O modelo está demorando muito para responder. Tente novamente."
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return f"Erro de conexão: Verifique se o Ollama está rodando."
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return f"Erro ao processar: {str(e)}"
    
    def chat(self, messages: list, **kwargs) -> str:
        """
        Envia uma conversa completa para o modelo.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}, ...]
            **kwargs: Parâmetros adicionais
        
        Returns:
            Resposta do modelo
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "top_p": kwargs.get('top_p', 0.9),
                    "top_k": kwargs.get('top_k', 40),
                    "num_predict": kwargs.get('max_tokens', 256)
                }
            }
            
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', 'Erro: Resposta vazia')
            else:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logger.error(error_msg)
                return f"Erro ao gerar resposta: {error_msg}"
                
        except Exception as e:
            logger.error(f"Erro no chat: {e}")
            return f"Erro ao processar chat: {str(e)}"
    
    def list_models(self) -> list:
        """Lista todos os modelos disponíveis no Ollama."""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name') for m in models]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Baixa um modelo do Ollama."""
        try:
            logger.info(f"Baixando modelo {model_name}...")
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": model_name},
                timeout=600  # 10 minutos para download
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao baixar modelo: {e}")
            return False
