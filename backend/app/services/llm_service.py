"""
LLM Service - Real integration with Ollama and other LLM providers
"""
from typing import List, Dict, Any, AsyncIterator, Optional
import asyncio
import httpx
import ollama
from ollama import AsyncClient
import logging

from app.core.config import settings
from app.core.exceptions import LLMException
from app.core.logger import LoggerMixin


class LLMService(LoggerMixin):
    """
    Service for interacting with LLM models (Ollama, OpenAI, DeepSeek)
    """
    
    def __init__(self):
        self.ollama_client: Optional[AsyncClient] = None
        self.ollama_url = settings.OLLAMA_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL
        self.available_models: List[str] = []
        self.initialized = False
    
    async def initialize(self):
        """
        Initialize LLM service and check connections
        """
        try:
            # Initialize Ollama client
            self.ollama_client = AsyncClient(host=self.ollama_url)
            
            # Test connection and get available models
            await self._check_ollama_connection()
            
            # Pull default model if not available
            if self.default_model not in self.available_models:
                self.logger.info(f"Pulling default model: {self.default_model}")
                await self.pull_model(self.default_model)
            
            self.initialized = True
            self.logger.info("LLM Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise LLMException(f"LLM initialization failed: {str(e)}")
    
    async def _check_ollama_connection(self):
        """
        Check Ollama connection and get available models
        """
        try:
            # Get list of available models
            models_response = await self.ollama_client.list()
            self.available_models = [model['name'] for model in models_response.get('models', [])]
            
            self.logger.info(f"Ollama connected. Available models: {self.available_models}")
            
        except Exception as e:
            self.logger.error(f"Ollama connection check failed: {str(e)}")
            raise LLMException(f"Failed to connect to Ollama: {str(e)}")
    
    async def pull_model(self, model_name: str):
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Name of the model to pull
        """
        try:
            self.logger.info(f"Pulling model: {model_name}")
            
            # Pull model with progress tracking
            async for progress in await self.ollama_client.pull(model_name, stream=True):
                if 'status' in progress:
                    self.logger.debug(f"Pull progress: {progress['status']}")
            
            self.available_models.append(model_name)
            self.logger.info(f"Model pulled successfully: {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to pull model {model_name}: {str(e)}")
            raise LLMException(f"Model pull failed: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt
            model: Model name (uses default if None)
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters
        
        Returns:
            Generated text
        """
        if not self.initialized:
            raise LLMException("LLM service not initialized")
        
        model = model or self.default_model
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Generate response
            response = await self.ollama_client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens or 2048,
                    **kwargs
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            raise LLMException(f"Text generation failed: {str(e)}")
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate text with streaming
        
        Args:
            prompt: User prompt
            model: Model name (uses default if None)
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters
        
        Yields:
            Generated text chunks
        """
        if not self.initialized:
            raise LLMException("LLM service not initialized")
        
        model = model or self.default_model
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Generate response with streaming
            async for chunk in await self.ollama_client.chat(
                model=model,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens or 2048,
                    **kwargs
                }
            ):
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
            
        except Exception as e:
            self.logger.error(f"Streaming generation failed: {str(e)}")
            raise LLMException(f"Streaming generation failed: {str(e)}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Chat with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses default if None)
            temperature: Sampling temperature
            **kwargs: Additional model parameters
        
        Returns:
            Generated response
        """
        if not self.initialized:
            raise LLMException("LLM service not initialized")
        
        model = model or self.default_model
        
        try:
            response = await self.ollama_client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    **kwargs
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            self.logger.error(f"Chat failed: {str(e)}")
            raise LLMException(f"Chat failed: {str(e)}")
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Chat with streaming
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses default if None)
            temperature: Sampling temperature
            **kwargs: Additional model parameters
        
        Yields:
            Generated text chunks
        """
        if not self.initialized:
            raise LLMException("LLM service not initialized")
        
        model = model or self.default_model
        
        try:
            async for chunk in await self.ollama_client.chat(
                model=model,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    **kwargs
                }
            ):
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
            
        except Exception as e:
            self.logger.error(f"Streaming chat failed: {str(e)}")
            raise LLMException(f"Streaming chat failed: {str(e)}")
    
    async def get_embeddings(
        self,
        text: str,
        model: str = "llama2"
    ) -> List[float]:
        """
        Get text embeddings
        
        Args:
            text: Input text
            model: Model name
        
        Returns:
            Embedding vector
        """
        try:
            response = await self.ollama_client.embeddings(
                model=model,
                prompt=text
            )
            
            return response['embedding']
            
        except Exception as e:
            self.logger.error(f"Embeddings failed: {str(e)}")
            raise LLMException(f"Embeddings generation failed: {str(e)}")
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models
        
        Returns:
            List of model information
        """
        try:
            response = await self.ollama_client.list()
            return response.get('models', [])
        except Exception as e:
            self.logger.error(f"Failed to list models: {str(e)}")
            return []
    
    async def delete_model(self, model_name: str):
        """
        Delete a model
        
        Args:
            model_name: Name of the model to delete
        """
        try:
            await self.ollama_client.delete(model_name)
            if model_name in self.available_models:
                self.available_models.remove(model_name)
            self.logger.info(f"Model deleted: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete model {model_name}: {str(e)}")
            raise LLMException(f"Model deletion failed: {str(e)}")
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get model information
        
        Args:
            model_name: Name of the model
        
        Returns:
            Model information
        """
        try:
            response = await self.ollama_client.show(model_name)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model_name}: {str(e)}")
            raise LLMException(f"Failed to get model info: {str(e)}")


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get global LLM service instance
    
    Returns:
        LLM service instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

