"""
Strategy Pattern Implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessingStrategy', 'ParallelProcessingStrategy', 'SequentialProcessingStrategy', 'ProcessingContext']


class ProcessingStrategy(ABC):
    """Abstract strategy for processing operations"""
    
    @abstractmethod
    def process(self, data: Any) -> Dict[str, Any]:
        """Process data using specific strategy"""
        pass


class ParallelProcessingStrategy(ProcessingStrategy):
    """Concrete strategy for parallel processing"""
    
    def process(self, data: Any) -> Dict[str, Any]:
        import os
        workers = min(os.cpu_count() or 4, 8)  # Configurable workers
        logger.info(f"Executing parallel processing strategy with {workers} workers")
        return {"strategy": "parallel", "workers": workers, "data": data}


class SequentialProcessingStrategy(ProcessingStrategy):
    """Concrete strategy for sequential processing"""
    
    def process(self, data: Any) -> Dict[str, Any]:
        logger.info("Executing sequential processing strategy")
        return {"strategy": "sequential", "data": data}


class ProcessingContext:
    """Context class for Strategy pattern"""
    
    def __init__(self, strategy: ProcessingStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ProcessingStrategy):
        """Change strategy at runtime - Open/Closed Principle"""
        self._strategy = strategy
    
    def execute(self, data: Any) -> Dict[str, Any]:
        try:
            return self._strategy.process(data)
        except Exception as e:
            logger.error(f"Strategy execution failed: {type(e).__name__}: {str(e)}")
            return {"success": False, "error": "Processing strategy failed"}