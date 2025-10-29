from redis import Redis
from typing import Optional, Callable, Any, List
import json
from functools import wraps
import logging
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Centralized cache management for Redis with systematic invalidation patterns.
    Ensures cache consistency across distributed services.
    """
    
    def __init__(self, redis_client: Optional[Redis] = None):
        if redis_client:
            self.redis = redis_client
        else:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis = Redis.from_url(redis_url, decode_responses=True)
        
        self._test_connection()
    
    def _test_connection(self):
        """Test Redis connection and log status"""
        try:
            self.redis.ping()
            logger.info("✅ Cache Manager: Redis connection successful")
        except Exception as e:
            logger.error(f"❌ Cache Manager: Redis connection failed - {str(e)}")
            raise
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching the pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "case:123:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Cache invalidated: {deleted} keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation failed for pattern '{pattern}': {str(e)}")
            return 0
    
    async def invalidate_case(self, case_id: int) -> None:
        """Invalidate all cache related to a specific case"""
        patterns = [
            f"case:{case_id}:*",
            f"case_documents:{case_id}:*",
            f"judge:cases:*",
            "cases:list:*"
        ]
        
        for pattern in patterns:
            await self.invalidate_pattern(pattern)
        
        logger.info(f"Case cache invalidated for case_id: {case_id}")
    
    async def invalidate_document(self, document_id: int, case_id: Optional[int] = None) -> None:
        """Invalidate all cache related to a specific document"""
        patterns = [
            f"document:{document_id}:*",
            "documents:list:*"
        ]
        
        if case_id:
            patterns.append(f"case_documents:{case_id}:*")
        
        for pattern in patterns:
            await self.invalidate_pattern(pattern)
        
        logger.info(f"Document cache invalidated for document_id: {document_id}")
    
    async def invalidate_user_data(self, user_id: int) -> None:
        """Invalidate all cache related to a specific user"""
        patterns = [
            f"user:{user_id}:*",
            f"user_cases:{user_id}:*",
            f"user_documents:{user_id}:*"
        ]
        
        for pattern in patterns:
            await self.invalidate_pattern(pattern)
        
        logger.info(f"User cache invalidated for user_id: {user_id}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed for key '{key}': {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key '{key}': {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete specific cache key"""
        try:
            deleted = self.redis.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Cache delete failed for key '{key}': {str(e)}")
            return False
    
    def cached(self, ttl: int = 3600, key_prefix: str = ""):
        """
        Decorator for automatic caching of function results
        
        Usage:
            @cache_manager.cached(ttl=1800, key_prefix="cases")
            async def get_case(case_id: int):
                return fetch_case_from_db(case_id)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
                
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                result = await func(*args, **kwargs)
                
                self.set(cache_key, result, ttl)
                logger.debug(f"Cache miss: {cache_key} - value cached")
                
                return result
            
            return wrapper
        return decorator

_cache_manager_instance: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """
    Dependency injection for FastAPI endpoints.
    
    Usage:
        @router.put("/cases/{case_id}")
        async def update_case(
            case_id: int,
            cache: CacheManager = Depends(get_cache_manager)
        ):
            await cache.invalidate_case(case_id)
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    
    return _cache_manager_instance
