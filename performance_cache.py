"""High-performance caching system"""
import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Optional, Dict
from functools import wraps


class PerformanceCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 128, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}
        self._access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if valid"""
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Check TTL
        if time.time() - timestamp > self.ttl:
            self._evict(key)
            return None
        
        # Update access time for LRU
        self._access_times[key] = time.time()
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Cache value with timestamp"""
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        current_time = time.time()
        self._cache[key] = (value, current_time)
        self._access_times[key] = current_time
    
    def _evict(self, key: str) -> None:
        """Remove key from cache"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), 
                     key=lambda k: self._access_times[k])
        self._evict(lru_key)
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()
        self._access_times.clear()


class FileCache:
    """Persistent file-based cache"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    def get(self, key: str, max_age: int = 3600) -> Optional[Any]:
        """Get cached value from file"""
        cache_path = self.get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        # Check file age
        if time.time() - cache_path.stat().st_mtime > max_age:
            cache_path.unlink(missing_ok=True)
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Cache value to file"""
        cache_path = self.get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception:
            cache_path.unlink(missing_ok=True)


# Global cache instances
memory_cache = PerformanceCache()
file_cache = FileCache()


def cached(ttl: int = 3600, use_file_cache: bool = False):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try memory cache first
            result = memory_cache.get(cache_key)
            if result is not None:
                return result
            
            # Try file cache if enabled
            if use_file_cache:
                result = file_cache.get(cache_key, ttl)
                if result is not None:
                    memory_cache.set(cache_key, result)
                    return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            memory_cache.set(cache_key, result)
            
            if use_file_cache:
                file_cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator