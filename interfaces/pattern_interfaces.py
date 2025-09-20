"""Design pattern interfaces"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from typing_extensions import Self


class Observable(ABC):
    """Interface for observable objects - Observer Pattern"""
    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        """Attach observer"""
        pass
    
    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        """Detach observer"""
        pass
    
    @abstractmethod
    def notify(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers"""
        pass


class Observer(ABC):
    """Interface for observer objects - Observer Pattern"""
    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Handle notification from observable"""
        pass


class Configurable(ABC):
    """Interface for configurable objects"""
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure object with settings"""
        pass


class Serializable(ABC):
    """Interface for serializable objects"""
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Self':
        """Create instance from dictionary"""
        pass