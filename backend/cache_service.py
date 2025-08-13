import asyncio
import json
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """In-memory cache service for performance optimization."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache service with default TTL in seconds."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task to clean expired entries."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodically clean up expired cache entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                await self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL."""
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        
        serialized_value = self._serialize(value)
        self.cache[key] = {
            'value': serialized_value,
            'expiry': expiry,
            'created_at': time.time()
        }
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key not in self.cache:
            logger.debug(f"Cache MISS: {key}")
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if time.time() > entry['expiry']:
            del self.cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None
        
        logger.debug(f"Cache HIT: {key}")
        return self._deserialize(entry['value'])
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache DELETE: {key}")
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self.cache:
            return False
        
        entry = self.cache[key]
        if time.time() > entry['expiry']:
            del self.cache[key]
            return False
        
        return True
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expiry']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        total_size = 0
        
        for entry in self.cache.values():
            if current_time > entry['expiry']:
                expired_entries += 1
            else:
                valid_entries += 1
            
            # Estimate size
            try:
                total_size += len(json.dumps(entry['value']))
            except:
                total_size += len(str(entry['value']))
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'estimated_size_bytes': total_size,
            'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1) * 100
        }
    
    def _serialize(self, value: Any) -> Any:
        """Serialize value for storage."""
        try:
            # Try to serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                return json.loads(json.dumps(value, default=str))
            return value
        except Exception:
            # Fallback to string representation
            return str(value)
    
    def _deserialize(self, value: Any) -> Any:
        """Deserialize value from storage."""
        return value
    
    async def set_with_callback(self, key: str, callback, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """Set cache with a callback function to generate the value."""
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Generate value using callback
        if asyncio.iscoroutinefunction(callback):
            value = await callback(*args, **kwargs)
        else:
            value = callback(*args, **kwargs)
        
        await self.set(key, value, ttl)
        return value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        import fnmatch
        
        matching_keys = [
            key for key in self.cache.keys()
            if fnmatch.fnmatch(key, pattern)
        ]
        
        for key in matching_keys:
            await self.delete(key)
        
        logger.info(f"Invalidated {len(matching_keys)} cache entries matching pattern: {pattern}")
        return len(matching_keys)

# Cache service configurations for different use cases
CACHE_CONFIGS = {
    'integration_data': {'ttl': 1800},      # 30 minutes
    'workflow_execution': {'ttl': 300},      # 5 minutes  
    'user_sessions': {'ttl': 86400},         # 24 hours
    'ai_responses': {'ttl': 7200},           # 2 hours
    'analytics_data': {'ttl': 600},          # 10 minutes
    'template_data': {'ttl': 3600},          # 1 hour
    'node_types': {'ttl': 86400},            # 24 hours
}

# Global cache instance
cache_service = CacheService()

# Cache decorators for common patterns
def cached(key_pattern: str, ttl: Optional[int] = None):
    """Decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            import hashlib
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = f"{key_pattern}:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_service.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Cache key generators
def generate_cache_key(category: str, *identifiers) -> str:
    """Generate standardized cache keys."""
    key_parts = [category] + [str(id) for id in identifiers]
    return ':'.join(key_parts)