"""Core processing interfaces"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .types import ProcessingResult


class Parseable(ABC):
    """Interface for parsing operations"""
    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """Parse and return structured data"""
        pass


class Extractable(ABC):
    """Interface for extraction operations"""
    @abstractmethod
    def extract(self, entries: List[Any]) -> List[Dict[str, Any]]:
        """Extract content from entries"""
        pass


class Filterable(ABC):
    """Interface for filtering operations"""
    @abstractmethod
    def filter(self, entries: List[Any]) -> List[Dict[str, Any]]:
        """Filter entries based on criteria"""
        pass


class Searchable(ABC):
    """Interface for search operations"""
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search and return matching results"""
        pass


class Executable(ABC):
    """Interface for executable operations"""
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> ProcessingResult:
        """Execute operation with arguments"""
        pass


class Processable(ABC):
    """Interface for processable resources"""
    @abstractmethod
    def __enter__(self) -> 'Processable':
        """Enter context manager"""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Optional[bool]:
        """Exit context manager"""
        pass