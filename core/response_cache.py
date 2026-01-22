"""
Response Cache - Cache de Respostas
Armazena respostas frequentes para melhor performance
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from core.logger import logger

class ResponseCache:
    """
    Cache inteligente de respostas do LLM.
    Reduz chamadas repetidas e melhora performance.
    """
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """
        Inicializa cache.
        
        Args:
            ttl_seconds: Tempo de vida do cache em segundos (padrão: 1 hora)
            max_size: Tamanho máximo do cache
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.max_size = max_size
        logger.info(f"ResponseCache inicializado (TTL: {ttl_seconds}s, Max: {max_size})")
    
    def _generate_key(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """
        Gera chave única para cache.
        
        Args:
            prompt: Prompt do usuário
            system: Mensagem de sistema
            **kwargs: Parâmetros adicionais
        
        Returns:
            Hash MD5 da chave
        """
        key_data = {
            "prompt": prompt.lower().strip(),
            "system": system.lower().strip() if system else "",
            "model": kwargs.get("model", ""),
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 200)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, system: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Obtém resposta do cache se disponível.
        
        Args:
            prompt: Prompt do usuário
            system: Mensagem de sistema
            **kwargs: Parâmetros adicionais
        
        Returns:
            Resposta em cache ou None
        """
        key = self._generate_key(prompt, system, **kwargs)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Verificar se ainda é válido
            if time.time() < entry["expires_at"]:
                logger.debug(f"Cache hit: {key[:8]}...")
                entry["hits"] = entry.get("hits", 0) + 1
                entry["last_used"] = time.time()
                return entry["response"]
            else:
                # Expirou, remover
                del self.cache[key]
                logger.debug(f"Cache expired: {key[:8]}...")
        
        return None
    
    def set(self, prompt: str, response: str, system: Optional[str] = None, **kwargs):
        """
        Armazena resposta no cache.
        
        Args:
            prompt: Prompt do usuário
            response: Resposta do LLM
            system: Mensagem de sistema
            **kwargs: Parâmetros adicionais
        """
        # Verificar tamanho do cache
        if len(self.cache) >= self.max_size:
            # Remover entrada mais antiga (LRU)
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].get("last_used", 0)
            )
            del self.cache[oldest_key]
            logger.debug(f"Cache evicted: {oldest_key[:8]}...")
        
        key = self._generate_key(prompt, system, **kwargs)
        self.cache[key] = {
            "response": response,
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl,
            "last_used": time.time(),
            "hits": 0
        }
        logger.debug(f"Cache stored: {key[:8]}...")
    
    def clear(self):
        """Limpa todo o cache."""
        self.cache.clear()
        logger.info("Cache limpo")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_hits = sum(entry.get("hits", 0) for entry in self.cache.values())
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl,
            "total_hits": total_hits,
            "hit_rate": total_hits / len(self.cache) if self.cache else 0
        }

