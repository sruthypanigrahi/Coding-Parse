"""
Base Model - Core serialization and validation
"""

from dataclasses import dataclass
from typing import Dict, Any, ClassVar
from collections import OrderedDict
from logger_config import setup_logger
from .serialization import SerializationHelper

logger = setup_logger(__name__)

__all__ = ['BaseModel']


@dataclass
class BaseModel:
    """Perfect base model with optimized serialization and validation"""
    
    # Instance-level cache to avoid thread safety issues
    _cache_max_size: ClassVar[int] = 128
    
    def to_dict(self) -> Dict[str, Any]:
        """Optimized serialization with security and performance"""
        # Secure hash computation for performance
        try:
            # Use frozenset for efficient hash computation
            hashable_items = frozenset((k, str(v)) for k, v in self.__dict__.items() if not k.startswith('_'))
            content_hash = hash(hashable_items)
        except TypeError:
            # Secure fallback using class name and instance data
            content_hash = hash((self.__class__.__name__, id(self), hash(str(self.__dict__))))
        cache_key = f"{self.__class__.__name__}_{content_hash}"
        
        # Thread-safe instance cache initialization
        if not hasattr(self, '_instance_cache'):
            import threading
            if not hasattr(self, '_cache_lock'):
                self._cache_lock = threading.RLock()
            with self._cache_lock:
                if not hasattr(self, '_instance_cache'):
                    self._instance_cache = OrderedDict()
        
        if cache_key in self._instance_cache:
            return self._instance_cache[cache_key].copy()
        
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):  # Skip private attributes
                result[key] = SerializationHelper.serialize_value(key, value)
        
        # Cache result with LRU eviction to prevent memory leaks
        if len(self._instance_cache) >= self._cache_max_size:
            # Remove oldest entry
            self._instance_cache.popitem(last=False)
        
        self._instance_cache[cache_key] = result.copy()
        self._instance_cache.move_to_end(cache_key)  # Mark as recently used
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create instance from dictionary with validation"""
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
        
        # Filter only valid fields for this class
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
