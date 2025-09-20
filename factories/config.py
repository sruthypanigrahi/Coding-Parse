"""
Configuration Management
"""

from typing import Dict, Any, Optional
from pathlib import Path
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ConfigurationManager']


class ConfigurationManager:
    """Configuration management - Singleton Pattern"""
    
    _instance: Optional['ConfigurationManager'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls) -> 'ConfigurationManager':
        import threading
        if not hasattr(cls, '_lock'):
            cls._lock = threading.Lock()
        
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._load_default_config()
        return cls._instance
    
    def _load_default_config(self) -> None:
        """Load default configuration"""
        self._config = {
            'pdf_processor': {
                'type': 'standard',
                'timeout': 300
            },
            'content_extractor': {
                'parallel_threshold': 100,
                'max_workers': 4,
                'content_limit': 10000
            },
            'exporter': {
                'format': 'jsonl',
                'encoding': 'utf-8'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with thread safety"""
        with self._lock:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with thread safety"""
        with self._lock:
            keys = key.split('.')
            config = self._config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    # Overwrite non-dict values with empty dict
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
    
    def load_from_file(self, file_path: str) -> bool:
        """Load configuration from file with path validation"""
        # Security: Validate file path
        if not file_path or '..' in file_path:
            logger.error("Invalid file path provided")
            return False
            
        try:
            # Security: Ensure path is within current directory
            safe_path = Path(file_path).resolve()
            cwd = Path.cwd().resolve()
            safe_path.relative_to(cwd)
            
            import yaml
            with open(safe_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                if isinstance(file_config, dict):
                    with self._lock:
                        self._config.update(file_config)
                else:
                    logger.error("Configuration file must contain a dictionary")
                    return False
            return True
        except ValueError:
            logger.error("Path traversal attempt detected")
            return False
        except (FileNotFoundError, PermissionError, yaml.YAMLError) as e:
            logger.error(f"Configuration loading failed: {type(e).__name__}")
            return False