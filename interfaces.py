"""Abstract interfaces for better OOP design"""
from abc import ABC, abstractmethod
from typing import List, Any, Protocol
from pathlib import Path


class Extractable(Protocol):
    """Protocol for extractable content"""
    def extract(self) -> Any:
        """Extract content from source"""
        ...


class Parseable(ABC):
    """Abstract base class for parsers"""
    
    @abstractmethod
    def parse(self) -> List[Any]:
        """Parse content and return structured data"""
        pass
    
    @abstractmethod
    def validate_input(self) -> bool:
        """Validate input before parsing"""
        pass


class Cacheable(ABC):
    """Abstract base class for cacheable operations"""
    
    @abstractmethod
    def get_cache_key(self) -> str:
        """Get unique cache key"""
        pass
    
    @abstractmethod
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        pass


class Serializable(ABC):
    """Abstract base class for serializable objects"""
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        pass