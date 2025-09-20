"""
Singleton and Template Method Patterns
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['SingletonMeta', 'ConfigurationManager', 'DocumentProcessor']


class SingletonMeta(type):
    """Thread-safe metaclass for Singleton pattern"""
    _instances = {}
    _lock = __import__('threading').Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigurationManager(metaclass=SingletonMeta):
    """Singleton configuration manager"""
    
    def __init__(self):
        with __import__('threading').Lock():
            if not hasattr(self, '_initialized'):
                self._config = {}
                self._initialized = True
    
    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value


class DocumentProcessor(ABC):
    """Template method for document processing"""
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Template method defining processing steps"""
        try:
            self.validate_input(file_path)
            data = self.load_document(file_path)
            processed_data = self.process_data(data)
            result = self.format_output(processed_data)
            return result
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"File access error: {e}")
            return {"success": False, "error": "File access denied"}
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {"success": False, "error": "Processing failed"}
    
    def validate_input(self, file_path: str):
        """Common validation logic with path traversal protection"""
        if not file_path:
            raise ValueError("File path cannot be empty")
        if not isinstance(file_path, str):
            raise TypeError("File path must be a string")
        
        # Path traversal protection
        if '..' in file_path or file_path.startswith(('/', '\\')):
            raise ValueError("Invalid file path: potential security risk")
        
        # Ensure path is within current directory
        import os
        try:
            abs_path = os.path.abspath(file_path)
            cwd = os.path.abspath('.')
            if not abs_path.startswith(cwd):
                raise ValueError("File path must be within current directory")
        except (OSError, ValueError):
            raise ValueError("Invalid file path")
    
    @abstractmethod
    def load_document(self, file_path: str) -> Any:
        """Load document - subclass specific"""
        pass
    
    @abstractmethod
    def process_data(self, data: Any) -> Any:
        """Process data - subclass specific"""
        pass
    
    def format_output(self, data: Any) -> Dict[str, Any]:
        """Common output formatting"""
        return {"success": True, "data": data}