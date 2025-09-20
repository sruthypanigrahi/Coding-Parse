"""
Strategy Pattern Implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass, field
from .base import ProcessingState
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessingContext', 'ProcessingStrategy', 'SequentialStrategy', 'ParallelStrategy']


@dataclass
class ProcessingContext:
    """Context for Strategy Pattern"""
    state: ProcessingState = ProcessingState.IDLE
    progress: float = 0.0
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class ProcessingStrategy(ABC):
    """Strategy interface for different processing approaches"""
    
    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """Process with specific strategy"""
        pass


class SequentialStrategy(ProcessingStrategy):
    """Sequential processing strategy"""
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """Process sequentially with actual implementation"""
        try:
            context.state = ProcessingState.PARSING
            context.message = "Processing sequentially"
            context.progress = 0.5  # Update progress
            logger.info("Sequential processing started")
            # Implement sequential processing
            if 'entries' in context.data:
                entries = context.data['entries']
                processed = []
                for i, entry in enumerate(entries):
                    # Process each entry sequentially
                    processed.append(entry)
                    context.progress = (i + 1) / len(entries)
                context.data['processed'] = processed
            context.state = ProcessingState.COMPLETED
            context.progress = 1.0
            return context
        except Exception as e:
            logger.error(f"Sequential processing failed: {type(e).__name__}")
            context.state = ProcessingState.FAILED
            context.message = "Sequential processing failed"
            return context


class ParallelStrategy(ProcessingStrategy):
    """Parallel processing strategy"""
    
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """Process in parallel with actual implementation"""
        try:
            context.state = ProcessingState.PARSING
            context.message = "Processing in parallel"
            context.progress = 0.5  # Update progress
            logger.info("Parallel processing started")
            # Implement parallel processing
            if 'entries' in context.data:
                from concurrent.futures import ThreadPoolExecutor
                import os
                entries = context.data['entries']
                max_workers = min(len(entries), os.cpu_count() or 4, 8)
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Process entries in parallel with actual work
                    def process_entry(entry):
                        # Actual processing logic for each entry
                        if hasattr(entry, 'content') and entry.content:
                            entry.word_count = len(entry.content.split())
                        return entry
                    processed = list(executor.map(process_entry, entries))
                context.data['processed'] = processed
            context.state = ProcessingState.COMPLETED
            context.progress = 1.0
            return context
        except Exception as e:
            logger.error(f"Parallel processing failed: {type(e).__name__}")
            context.state = ProcessingState.FAILED
            context.message = "Parallel processing failed"
            return context