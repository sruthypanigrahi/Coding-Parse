"""
State Pattern Implementation
"""

from abc import ABC, abstractmethod
from enum import Enum
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessingStateEnum', 'StateHandler', 'StateContext']


class ProcessingStateEnum(Enum):
    """Enumeration for processing states"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class StateHandler(ABC):
    """Abstract state handler"""
    
    @abstractmethod
    def handle(self, context: 'StateContext') -> ProcessingStateEnum:
        """Handle state transition"""
        pass


class IdleStateHandler(StateHandler):
    """Handler for idle state"""
    
    def handle(self, context: 'StateContext') -> ProcessingStateEnum:
        logger.info("Transitioning from IDLE to PROCESSING")
        return ProcessingStateEnum.PROCESSING


class ProcessingStateHandler(StateHandler):
    """Handler for processing state"""
    
    def handle(self, context: 'StateContext') -> ProcessingStateEnum:
        # Check processing success from context
        success = getattr(context, 'processing_success', True)
        if success:
            logger.info("Transitioning from PROCESSING to COMPLETED")
            return ProcessingStateEnum.COMPLETED
        else:
            logger.error("Processing failed - transitioning to ERROR")
            return ProcessingStateEnum.ERROR


class CompletedStateHandler(StateHandler):
    """Handler for completed state"""
    
    def handle(self, context: 'StateContext') -> ProcessingStateEnum:
        logger.info("Transitioning from COMPLETED to IDLE")
        return ProcessingStateEnum.IDLE


class ErrorStateHandler(StateHandler):
    """Handler for error state"""
    
    def handle(self, context: 'StateContext') -> ProcessingStateEnum:
        logger.error("Processing error state - transitioning to IDLE")
        return ProcessingStateEnum.IDLE


class StateContext:
    """Context for State pattern"""
    
    def __init__(self):
        self._states = {
            ProcessingStateEnum.IDLE: IdleStateHandler(),
            ProcessingStateEnum.PROCESSING: ProcessingStateHandler(),
            ProcessingStateEnum.COMPLETED: CompletedStateHandler(),
            ProcessingStateEnum.ERROR: ErrorStateHandler()
        }
        self._current_state = ProcessingStateEnum.IDLE
        self.processing_success = True  # State data
    
    def transition(self):
        """Execute state transition with error handling"""
        handler = self._states.get(self._current_state)
        if handler:
            try:
                new_state = handler.handle(self)
                if isinstance(new_state, ProcessingStateEnum):
                    self._current_state = new_state
                else:
                    logger.error(f"Invalid state returned: {new_state}")
            except Exception as e:
                logger.error(f"State transition failed: {type(e).__name__}: {e}")
                self._current_state = ProcessingStateEnum.ERROR
        else:
            logger.warning(f"No handler found for state: {self._current_state}")
    
    @property
    def state(self) -> ProcessingStateEnum:
        return self._current_state