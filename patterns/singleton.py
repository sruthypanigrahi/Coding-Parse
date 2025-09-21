"""
Singleton and Template Method Patterns
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import threading
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
    """Thread-safe singleton configuration manager"""
    
    _config_lock = threading.Lock()
    
    def __init__(self):
        # Thread-safe initialization
        if not hasattr(self, '_initialized'):
            self._config = {}
            self._initialized = True
    
    def get_config(self, key: str, default=None):
        """Get configuration value with thread safety"""
        with self._config_lock:
            return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value with thread safety"""
        with self._config_lock:
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
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return {"success": False, "error": "File not found"}
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return {"success": False, "error": "File access denied"}
        except (OSError, IOError) as e:
            logger.error(f"I/O error: {e}")
            return {"success": False, "error": "File operation failed"}
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"success": False, "error": "Invalid input"}
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"File operation error: {type(e).__name__}: {str(e)[:100]}")
            return {"success": False, "error": "File operation failed"}
        except Exception as e:
            logger.error(f"Processing error: {type(e).__name__}: {str(e)[:100]}")
            return {"success": False, "error": "Processing failed"}
    
    def validate_input(self, file_path: str):
        """Secure input validation with robust path traversal protection"""
        import os
        
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")
        
        # Explicit path traversal checks first
        if '..' in file_path or '/' in file_path or '\\' in file_path:
            raise ValueError("Path traversal attempts not allowed")
        
        # Sanitize input
        clean_path = file_path.replace('\x00', '').strip()
        if not clean_path:
            raise ValueError("Invalid file path after sanitization")
        
        # Robust path traversal protection
        try:
            path_obj = Path(clean_path)
            if path_obj.is_absolute():
                raise ValueError("Absolute paths not allowed")
            
            resolved_path = path_obj.resolve(strict=False)
            cwd = Path.cwd().resolve()
            
            # Use os.path.commonpath for secure validation
            common = os.path.commonpath([str(resolved_path), str(cwd)])
            if Path(common).resolve() != cwd:
                raise ValueError("Path traversal attempt detected")
                
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid file path: {e}")
    
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