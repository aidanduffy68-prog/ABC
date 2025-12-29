"""
Redis Caching Middleware
Caching layer for API responses using Redis

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import redis
import json
import os
from typing import Optional, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching for API responses"""
    
    def __init__(self):
        """Initialize Redis client"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache enabled and connected")
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Error retrieving cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set cached value with TTL (default 5 min)"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.warning(f"Error setting cache key {key}: {e}")
    
    def delete(self, key: str):
        """Delete cached value"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Error deleting cache key {key}: {e}")


def cache_response(ttl: int = 300):
    """
    Decorator to cache API responses
    
    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Generate cache key from function name and arguments
            # Convert args/kwargs to string representation for hashing
            args_str = str(args) if args else ""
            kwargs_str = str(sorted(kwargs.items())) if kwargs else ""
            cache_key = f"{func.__name__}:{args_str}:{kwargs_str}"
            
            # Try cache first
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached
            
            # Call function
            logger.debug(f"Cache miss for {func.__name__}, calling function")
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

