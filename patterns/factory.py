"""
Factory Pattern Implementation
"""

from typing import List, Optional
from .strategy import ProcessingStrategy, ParallelProcessingStrategy, SequentialProcessingStrategy
from .observer import Observer
from .state import StateContext
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessorFactory', 'ProcessorBuilder', 'ProcessorConfiguration']


class ProcessorFactory:
    """Factory for creating processors"""
    
    @staticmethod
    def create_processor(processor_type: str) -> ProcessingStrategy:
        """Create processor based on type"""
        if not processor_type:
            raise ValueError("Processor type cannot be None or empty")
            
        processors = {
            "parallel": ParallelProcessingStrategy,
            "sequential": SequentialProcessingStrategy
        }
        
        if processor_type not in processors:
            raise ValueError(f"Unknown processor type: {processor_type}")
        
        return processors[processor_type]()


class ProcessorBuilder:
    """Builder for complex processor configuration"""
    
    def __init__(self):
        self._strategy: Optional[ProcessingStrategy] = None
        self._observers: List[Observer] = []
        self._state_context: Optional[StateContext] = None
    
    def with_strategy(self, strategy: ProcessingStrategy) -> 'ProcessorBuilder':
        """Add processing strategy"""
        self._strategy = strategy
        return self
    
    def with_observers(self, observers: List[Observer]) -> 'ProcessorBuilder':
        """Add observers with defensive copy"""
        self._observers = list(observers) if observers else []
        return self
    
    def with_state_context(self, context: StateContext) -> 'ProcessorBuilder':
        """Add state context"""
        self._state_context = context
        return self
    
    def build(self) -> 'ProcessorConfiguration':
        """Build processor configuration with validation"""
        if not self._strategy:
            raise ValueError("Strategy is required for processor configuration")
        return ProcessorConfiguration(
            strategy=self._strategy,
            observers=self._observers,
            state_context=self._state_context
        )


class ProcessorConfiguration:
    """Processor configuration object"""
    
    def __init__(self, strategy: ProcessingStrategy,
                 observers: Optional[List[Observer]] = None,
                 state_context: Optional[StateContext] = None):
        self.strategy = strategy
        self.observers = list(observers) if observers else []
        self.state_context = state_context