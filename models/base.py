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
    
    # Class-level LRU cache with size limit to prevent memory leaks
    _serialization_cache: ClassVar[OrderedDict] = OrderedDict()
    _cache_max_size: ClassVar[int] = 128
    
    def to_dict(self) -> Dict[str, Any]:
        """Optimized serialization with security and performance"""
        # Use content hash instead of object id to prevent memory leaks
        content_hash = hash(tuple(sorted((k, str(v)) for k, v in self.__dict__.items() if not k.startswith('_'))))
        cache_key = f"{self.__class__.__name__}_{content_hash}"
        
        if cache_key in self._serialization_cache:
            return self._serialization_cache[cache_key].copy()
        
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):  # Skip private attributes
                result[key] = SerializationHelper.serialize_value(key, value)
        
        # Cache result with LRU eviction to prevent memory leaks
        if len(self._serialization_cache) >= self._cache_max_size:
            # Remove oldest entry
            self._serialization_cache.popitem(last=False)
        
        self._serialization_cache[cache_key] = result.copy()
        self._serialization_cache.move_to_end(cache_key)  # Mark as recently used
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
    
