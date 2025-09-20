"""Data handling interfaces"""
from abc import ABC, abstractmethod
from typing import Any
from .types import ValidationReport


class Validatable(ABC):
    """Interface for validation operations"""
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate data and return success status"""
        pass


class Reportable(ABC):
    """Interface for report generation"""
    @abstractmethod
    def generate_report(self) -> ValidationReport:
        """Generate validation report"""
        pass


class Exportable(ABC):
    """Interface for exportable objects"""
    @abstractmethod
    def export(self, data: Any, filename: str) -> bool:
        """Export data to file"""
        pass


class Cacheable(ABC):
    """Interface for cacheable objects"""
    @abstractmethod
    def get_cache_key(self) -> str:
        """Get unique cache key"""
        pass
    
    @abstractmethod
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        pass