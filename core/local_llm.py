# Integração com Ollama - Modelos LLM Locais Gratuitos

import requests
import json
import os
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.llm_optimizer import LLMOptimizer
from core.logger import logger

class LocalLLM:
    """
    Integração com Ollama para modelos LLM locais gratuitos.
    Suporta: codellama, deepseek-coder, llama2, mistral, etc.
    """
    
    def __init__(self, 
                 base_url: str = None, 
                 model: str = "codellama:7b",
                 timeout: int = None,
                 optimizer: Optional['LLMOptimizer'] = None):
        """
        Inicializa a conexão com Ollama.
        
        Args:
            base_url: URL base do Ollama (padrão: http://localhost:11434 ou http://ollama:11434 no Docker)
            model: Nome do modelo a ser usado
            timeout: Timeout para requisições em segundos (auto-ajustado se None)
            optimizer: Instância de LLMOptimizer para auto-ajuste (opcional)
        """
        # Configuração automática baseada no ambiente
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', model)
        self.optimizer = optimizer
        
        # Timeout baseado em recursos se optimizer disponível
        if timeout is None:
            if optimizer:
                self.timeout = optimizer.get_timeout()
            else:
                self.timeout = 45  # Default médio
        else:
            self.timeout = timeout
            
        self.api_url = f"{self.base_url}/api"
        
        logger.info(f"LocalLLM inicializado: {self.base_url} | Modelo: {self.model} | Timeout: {self.timeout}s")
        
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
        Gera uma resposta do modelo LLM com otimização automática.
        
        Args:
            prompt: Prompt do usuário
            system: Mensagem de sistema (opcional)
            **kwargs: Parâmetros adicionais (temperature, top_p, etc.)
        
        Returns:
            Resposta gerada pelo modelo
        """
        try:
            # Usar otimizador se disponível
            if self.optimizer:
                optimal = self.optimizer.get_optimal_params()
                # Mesclar com kwargs (kwargs têm prioridade)
                final_params = {**optimal, **kwargs}
                # Garantir que max_tokens não seja muito alto
                final_params['max_tokens'] = min(final_params.get('max_tokens', 200), 300)
            else:
                final_params = {
                    "temperature": kwargs.get('temperature', 0.65),
                    "top_p": kwargs.get('top_p', 0.9),
                    "top_k": kwargs.get('top_k', 40),
                    "num_predict": kwargs.get('max_tokens', 200)
                }
            
            # Preparar payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": final_params.get('temperature', 0.65),
                    "top_p": final_params.get('top_p', 0.9),
                    "top_k": final_params.get('top_k', 40),
                    "num_predict": final_params.get('max_tokens', final_params.get('num_predict', 200)),
                    "repeat_penalty": final_params.get('repeat_penalty', 1.1),
                    "num_thread": final_params.get('num_threads', None)
                }
            }
            
            # Remover None values
            payload["options"] = {k: v for k, v in payload["options"].items() if v is not None}
            
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
            logger.error(f"Timeout ao gerar resposta com modelo {self.model}. Aumentando timeout ou otimizando parâmetros...")
            # Tentar novamente com parâmetros mais otimizados para velocidade
            try:
                optimized_kwargs = {
                    **kwargs,
                    'max_tokens': kwargs.get('max_tokens', 150) // 2,  # Metade dos tokens
                    'temperature': kwargs.get('temperature', 0.6) * 0.9  # Mais determinístico
                }
                logger.info("Tentando com parâmetros otimizados para velocidade...")
                return self.generate(prompt, system, **optimized_kwargs)
            except:
                return "⏱️ O modelo está processando, mas demorou muito. Tente simplificar a pergunta ou aguarde alguns segundos."
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
                    "temperature": kwargs.get('temperature', 0.65),
                    "top_p": kwargs.get('top_p', 0.9),
                    "top_k": kwargs.get('top_k', 40),
                    "num_predict": kwargs.get('max_tokens', 200)
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
