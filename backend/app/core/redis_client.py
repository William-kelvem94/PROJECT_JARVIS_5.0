"""
Redis Client for Caching and Session Management
"""
import json
from typing import Optional, Any, Dict
import redis.asyncio as redis
import logging

from app.core.config import settings
from app.core.exceptions import JarvisException

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """
    Initialize Redis connection
    """
    global redis_client
    
    try:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise JarvisException(f"Redis connection failed: {str(e)}")


async def close_redis():
    """
    Close Redis connection
    """
    global redis_client
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


def get_redis() -> redis.Redis:
    """
    Get Redis client instance
    
    Returns:
        Redis client
    
    Raises:
        JarvisException: If Redis is not initialized
    """
    if redis_client is None:
        raise JarvisException("Redis client not initialized")
    return redis_client


class RedisCache:
    """
    Redis cache wrapper with helper methods
    """
    
    def __init__(self):
        self.client = get_redis()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
        
        Returns:
            Success status
        """
        try:
            serialized = json.dumps(value)
            if expire:
                await self.client.setex(key, expire, serialized)
            else:
                await self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Success status
        """
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists
        
        Args:
            key: Cache key
        
        Returns:
            Existence status
        """
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {str(e)}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter
        
        Args:
            key: Counter key
            amount: Increment amount
        
        Returns:
            New value
        """
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment error: {str(e)}")
            return 0
    
    async def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values
        
        Args:
            keys: List of keys
        
        Returns:
            Dictionary of key-value pairs
        """
        try:
            values = await self.client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error(f"Redis get_many error: {str(e)}")
            return {}
    
    async def set_many(
        self,
        mapping: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """
        Set multiple values
        
        Args:
            mapping: Dictionary of key-value pairs
            expire: Expiration time in seconds
        
        Returns:
            Success status
        """
        try:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                serialized = json.dumps(value)
                if expire:
                    pipe.setex(key, expire, serialized)
                else:
                    pipe.set(key, serialized)
            await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Redis set_many error: {str(e)}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "user:*")
        
        Returns:
            Number of deleted keys
        """
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear_pattern error: {str(e)}")
            return 0

