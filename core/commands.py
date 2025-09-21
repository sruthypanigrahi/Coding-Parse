"""
Command Pattern Implementation
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .base import DocumentProcessor
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessingCommand', 'ParseCommand', 'ProcessingInvoker']


class ProcessingCommand(ABC):
    """Command Pattern for processing operations"""
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute command"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo command if possible"""
        pass


class ParseCommand(ProcessingCommand):
    """Concrete command for parsing operations"""
    
    def __init__(self, processor: DocumentProcessor, input_data: Any):
        self._processor = processor
        self._input_data = input_data
        self._result: Optional[Dict[str, Any]] = None
    
    def execute(self) -> Dict[str, Any]:
        """Execute parsing command with error handling"""
        try:
            self._result = self._processor.process(self._input_data)
            logger.info(f"Parse command executed successfully")
            return self._result
        except Exception as e:
            logger.error(f"Parse command failed: {type(e).__name__}: {str(e)}")
            self._result = {"success": False, "error": f"Parse command failed: {str(e)}"}
            return self._result
    
    def undo(self) -> bool:
        """Undo parsing (cleanup temporary files and resources)"""
        try:
            from pathlib import Path
            # Clean up any temporary files created during processing
            temp_files = ['temp_toc.jsonl', 'temp_content.jsonl', 'temp_validation.xlsx']
            cleaned = 0
            
            for temp_file in temp_files:
                temp_path = Path(temp_file)
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                        cleaned += 1
                    except (OSError, PermissionError):
                        continue
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} temporary files")
            
            # Reset result state
            self._result = None
            
            return True
        except Exception as e:
            logger.error(f"Undo operation failed: {type(e).__name__}: {str(e)}")
            return False


class ProcessingInvoker:
    """Invoker for Command Pattern"""
    
    def __init__(self):
        self._commands: List[ProcessingCommand] = []
    
    def add_command(self, command: ProcessingCommand):
        """Add command to execution queue"""
        self._commands.append(command)
    
    def execute_all(self) -> List[Dict[str, Any]]:
        """Execute all commands - commands handle their own exceptions"""
        results = []
        for command in self._commands:
            # Commands handle their own exceptions internally
            result = command.execute()
            results.append(result)
        return results
    
    def undo_last(self) -> bool:
        """Undo last command and remove it from history"""
        if self._commands:
            command = self._commands.pop()
            return command.undo()
        return False