"""
Observer Pattern Implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['Observer', 'ProgressObserver', 'Subject']


class Observer(ABC):
    """Abstract observer interface"""
    
    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]):
        """Handle notification from subject"""
        pass


class ProgressObserver(Observer):
    """Concrete observer for progress tracking"""
    
    def update(self, event: str, data: Dict[str, Any]):
        # Sanitize sensitive data before logging using comprehensive patterns
        import re
        sensitive_patterns = [r'.*password.*', r'.*token.*', r'.*key.*', r'.*secret.*', r'.*auth.*']
        safe_data = {}
        for k, v in data.items():
            if not any(re.match(pattern, k.lower()) for pattern in sensitive_patterns):
                safe_data[k] = v
        logger.info(f"Progress Update: {event} - {safe_data}")


class Subject:
    """Subject class for Observer pattern"""
    
    def __init__(self):
        self._observers: Set[Observer] = set()
    
    def attach(self, observer: Observer):
        """Attach observer to subject with O(1) duplicate prevention"""
        self._observers.add(observer)
    
    def detach(self, observer: Observer):
        """Detach observer from subject with O(1) removal"""
        self._observers.discard(observer)
    
    def notify(self, event: str, data: Dict[str, Any]):
        """Notify all observers with error handling"""
        for observer in self._observers:
            try:
                observer.update(event, data)
            except Exception as e:
                logger.error(f"Observer notification failed: {type(e).__name__}: {str(e)}")