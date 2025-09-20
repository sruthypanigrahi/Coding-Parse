"""
Patterns Package - Design Pattern Implementations
"""

from .strategy import ProcessingStrategy, ParallelProcessingStrategy, SequentialProcessingStrategy, ProcessingContext
from .observer import Observer, ProgressObserver, Subject
from .state import ProcessingStateEnum, StateHandler, StateContext
from .factory import ProcessorFactory, ProcessorBuilder, ProcessorConfiguration
from .singleton import SingletonMeta, ConfigurationManager, DocumentProcessor

__all__ = [
    'ProcessingStrategy', 'ParallelProcessingStrategy', 'SequentialProcessingStrategy',
    'ProcessingContext', 'Observer', 'ProgressObserver', 'Subject',
    'ProcessingStateEnum', 'StateHandler', 'StateContext',
    'ProcessorFactory', 'ProcessorBuilder', 'ProcessorConfiguration',
    'ConfigurationManager', 'DocumentProcessor'
]