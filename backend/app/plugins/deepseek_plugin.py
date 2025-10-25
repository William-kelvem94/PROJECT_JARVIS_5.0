"""
DeepSeek Plugin - Integration with DeepSeek API
"""
from typing import Dict, Any, Optional, List, AsyncIterator
import httpx
import asyncio

from app.core.plugin_manager import PluginBase
from app.core.config import settings
from app.core.exceptions import PluginException


class DeepSeekPlugin(PluginBase):
    """
    Plugin for DeepSeek API integration
    """
    
    name = "deepseek"
    version = "1.0.0"
    description = "DeepSeek LLM API integration"
    author = "Jarvis Team"
    
    def __init__(self):
        super().__init__()
        self.api_key: Optional[str] = None
        self.base_url = "https://api.deepseek.com/v1"
        self.client: Optional[httpx.AsyncClient] = None
        self.default_model = "deepseek-chat"
    
    async def initialize(self) -> bool:
        """
        Initialize DeepSeek API connection
        """
        try:
            self.api_key = settings.DEEPSEEK_API_KEY
            
            if not self.api_key:
                self.logger.warning("DeepSeek API key not configured")
                self.enabled = False
                return False
            
            # Create async HTTP client
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=120.0
            )
            
            # Test API connection
            await self._test_connection()
            
            self.logger.info("DeepSeek plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DeepSeek plugin: {str(e)}")
            self.enabled = False
            return False
    
    async def _test_connection(self):
        """
        Test API connection
        """
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            self.logger.info("DeepSeek API connection successful")
        except Exception as e:
            raise PluginException(
                f"DeepSeek API connection test failed: {str(e)}",
                plugin_name=self.name
            )
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request through DeepSeek API
        
        Args:
            data: Request data with 'action' and parameters
                - action: 'chat', 'complete', or 'stream'
                - messages: List of message dicts
                - prompt: Single prompt string (for complete)
                - model: Model name (optional)
                - temperature: Sampling temperature
                - max_tokens: Maximum tokens
        
        Returns:
            API response
        """
        if not self.enabled or not self.client:
            raise PluginException(
                "DeepSeek plugin not properly initialized",
                plugin_name=self.name
            )
        
        action = data.get("action", "chat")
        
        if action == "chat":
            return await self._chat(data)
        elif action == "complete":
            return await self._complete(data)
        elif action == "stream":
            # For streaming, return an async generator
            return {"stream": self._chat_stream(data)}
        else:
            raise PluginException(
                f"Unknown action: {action}",
                plugin_name=self.name
            )
    
    async def _chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chat completion with DeepSeek
        """
        try:
            messages = data.get("messages", [])
            model = data.get("model", self.default_model)
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens", 2048)
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "finish_reason": result["choices"][0].get("finish_reason")
            }
            
        except httpx.HTTPError as e:
            self.logger.error(f"DeepSeek API error: {str(e)}")
            raise PluginException(
                f"DeepSeek API request failed: {str(e)}",
                plugin_name=self.name
            )
    
    async def _complete(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Text completion with DeepSeek
        """
        try:
            prompt = data.get("prompt", "")
            model = data.get("model", self.default_model)
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens", 2048)
            
            # Convert prompt to chat format
            messages = [{"role": "user", "content": prompt}]
            
            return await self._chat({
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens
            })
            
        except Exception as e:
            raise PluginException(
                f"DeepSeek completion failed: {str(e)}",
                plugin_name=self.name
            )
    
    async def _chat_stream(self, data: Dict[str, Any]) -> AsyncIterator[str]:
        """
        Streaming chat with DeepSeek
        """
        try:
            messages = data.get("messages", [])
            model = data.get("model", self.default_model)
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens", 2048)
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            import json
                            chunk = json.loads(data_str)
                            
                            if chunk["choices"][0]["delta"].get("content"):
                                yield chunk["choices"][0]["delta"]["content"]
                        except:
                            continue
            
        except Exception as e:
            self.logger.error(f"DeepSeek streaming error: {str(e)}")
            raise PluginException(
                f"DeepSeek streaming failed: {str(e)}",
                plugin_name=self.name
            )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Convenience method for chat completion
        """
        result = await self._chat({
            "messages": messages,
            "model": model or self.default_model,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
        return result["content"]
    
    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Convenience method for text completion
        """
        result = await self._complete({
            "prompt": prompt,
            "model": model or self.default_model,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
        return result["content"]
    
    async def shutdown(self):
        """
        Cleanup resources
        """
        if self.client:
            await self.client.aclose()
            self.client = None
        
        self.logger.info("DeepSeek plugin shut down")

