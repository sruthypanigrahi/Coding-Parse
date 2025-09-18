"""Interfaces following SOLID principles"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Parseable(ABC):
    @abstractmethod
    def parse(self) -> List:
        pass


class Extractable(ABC):
    @abstractmethod
    def extract(self, entries: List) -> List:
        pass


class Filterable(ABC):
    @abstractmethod
    def apply(self, entries: List) -> List:
        pass


class Searchable(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        pass


class Executable(ABC):
    @abstractmethod
    def execute(self, *args) -> Dict[str, Any]:
        pass


class Processable(ABC):
    @abstractmethod
    def __enter__(self):
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass