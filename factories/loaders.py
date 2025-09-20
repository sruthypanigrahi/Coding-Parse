"""
Module Loading and Application Context
"""

from typing import Dict, Any, Optional, Type
from .base_factories import ProcessorFactory, StandardProcessorFactory, ServiceFactory, StandardServiceFactory
from .registry import DependencyInjector, ComponentRegistry
from .config import ConfigurationManager
from validators import InputValidator
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ModuleLoader', 'ApplicationContext']


class ModuleLoader:
    """Dynamic module loading for extensibility"""
    
    @staticmethod
    def load_processor_class(module_name: str, class_name: str) -> Optional[Type]:
        """Load processor class dynamically with security validation"""
        # Security: Validate module and class names
        if not module_name or not class_name:
            logger.warning("Invalid module or class name provided")
            return None
            
        # Security: Only allow safe module names (no path traversal)
        if '..' in module_name or '/' in module_name or '\\' in module_name:
            logger.warning(f"Unsafe module name rejected: {module_name}")
            return None
            
        # Security: Only allow safe class names (alphanumeric and underscore)
        if not class_name.replace('_', '').isalnum():
            logger.warning(f"Unsafe class name rejected: {class_name}")
            return None
            
        try:
            # Security: Use predefined class registry instead of dynamic imports
            safe_classes = {
                'components.PDFProcessor': 'components.pdf_processor.PDFProcessor',
                'components.TOCParser': 'components.toc_parser.TOCParser',
                'components.ContentExtractor': 'components.content_extractor.ContentExtractor'
            }
            
            class_key = f"{module_name}.{class_name}"
            if class_key not in safe_classes:
                logger.warning(f"Class not in safe registry: {class_key}")
                return None
            
            # Return predefined safe classes only
            from components.pdf_processor import PDFProcessor
            from components.toc_parser import TOCParser
            from components.content_extractor import ContentExtractor
            
            class_map = {
                'components.PDFProcessor': PDFProcessor,
                'components.TOCParser': TOCParser,
                'components.ContentExtractor': ContentExtractor
            }
            
            return class_map.get(class_key)
        except Exception as e:
            logger.error(f"Failed to load {class_name} from {module_name}: {e}")
            return None
    
    @staticmethod
    def create_custom_factory(config: Dict[str, Any]) -> Optional[ProcessorFactory]:
        """Create custom factory from configuration with proper error handling"""
        if not isinstance(config, dict):
            logger.error("Invalid configuration provided")
            return None
            
        try:
            module_name = config.get('module', '')
            class_name = config.get('class', '')
            
            if not module_name or not class_name:
                logger.error("Missing module or class name in configuration")
                return None
                
            factory_class = ModuleLoader.load_processor_class(module_name, class_name)
            if factory_class:
                return factory_class()
            else:
                logger.error(f"Failed to load factory class: {class_name}")
                return None
        except Exception as e:
            logger.error(f"Custom factory creation failed: {type(e).__name__}: {e}")
            return None


class ApplicationContext:
    """Application context for managing dependencies"""
    
    def __init__(self):
        self._injector = DependencyInjector()
        self._config = ConfigurationManager()
        self._registry = ComponentRegistry()
        self._setup_default_bindings()
    
    def _setup_default_bindings(self) -> None:
        """Setup default dependency bindings"""
        self._injector.bind(ProcessorFactory, StandardProcessorFactory)
        self._injector.bind(ServiceFactory, StandardServiceFactory)
        self._injector.bind_singleton(InputValidator, InputValidator)
    
    def get_processor_factory(self) -> ProcessorFactory:
        """Get processor factory with error handling"""
        try:
            return self._injector.get(ProcessorFactory)
        except Exception as e:
            logger.error(f"Failed to get processor factory: {e}")
            return StandardProcessorFactory()
    
    def get_service_factory(self) -> ServiceFactory:
        """Get service factory with error handling"""
        try:
            return self._injector.get(ServiceFactory)
        except Exception as e:
            logger.error(f"Failed to get service factory: {e}")
            return StandardServiceFactory()
    
    def get_validator(self) -> InputValidator:
        """Get input validator"""
        return self._injector.get(InputValidator)
    
    def configure_from_file(self, config_file: str) -> bool:
        """Configure application from file with error handling"""
        try:
            return self._config.load_from_file(config_file)
        except (FileNotFoundError, PermissionError, ValueError) as e:
            logger.error(f"Configuration loading failed: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with error handling"""
        try:
            return self._config.get(key, default)
        except (KeyError, AttributeError, TypeError) as e:
            logger.warning(f"Configuration access failed for key '{key}': {e}")
            return default