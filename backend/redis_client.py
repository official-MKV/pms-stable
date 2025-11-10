import redis
import json
from typing import Any, Optional
from decouple import config

# Redis connection configuration
REDIS_URL = config("REDIS_URL", default="redis://redis:6379/0")

# Create Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class RedisCache:
    """Redis cache utility class."""
    
    def __init__(self, client=None):
        self.client = client or redis_client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (time to live) in seconds."""
        try:
            serialized_value = json.dumps(value, default=str)
            return self.client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis invalidate_pattern error: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0
    
    def set_hash(self, key: str, mapping: dict, ttl: int = 3600) -> bool:
        """Set hash fields."""
        try:
            # Convert values to strings for Redis hash
            str_mapping = {k: json.dumps(v, default=str) for k, v in mapping.items()}
            result = self.client.hset(key, mapping=str_mapping)
            if ttl > 0:
                self.client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            print(f"Redis set_hash error: {e}")
            return False
    
    def get_hash(self, key: str, field: str = None) -> Optional[Any]:
        """Get hash field(s)."""
        try:
            if field:
                value = self.client.hget(key, field)
                if value:
                    return json.loads(value)
                return None
            else:
                hash_data = self.client.hgetall(key)
                if hash_data:
                    return {k: json.loads(v) for k, v in hash_data.items()}
                return {}
        except Exception as e:
            print(f"Redis get_hash error: {e}")
            return None

# Global cache instance
cache = RedisCache()

# Cache key generators
def user_cache_key(user_id: int) -> str:
    """Generate cache key for user data."""
    return f"user:{user_id}"

def user_permissions_key(user_id: int) -> str:
    """Generate cache key for user permissions."""
    return f"user_permissions:{user_id}"

def role_cache_key(role_id: int) -> str:
    """Generate cache key for role data."""
    return f"role:{role_id}"

def system_config_key(config_key: str) -> str:
    """Generate cache key for system configuration."""
    return f"system_config:{config_key}"

# Cache invalidation helpers
def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user."""
    cache.delete(user_cache_key(user_id))
    cache.delete(user_permissions_key(user_id))

def invalidate_role_cache(role_id: int):
    """Invalidate cache entries for a role."""
    cache.delete(role_cache_key(role_id))
    # Also invalidate all user permission caches as they might be affected
    cache.invalidate_pattern("user_permissions:*")

def invalidate_system_cache():
    """Invalidate system configuration cache."""
    cache.invalidate_pattern("system_config:*")