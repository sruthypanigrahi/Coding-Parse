"""
Component Registry and Dependency Injection
"""

import threading
from typing import Dict, Any, Optional, Type
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ComponentRegistry', 'DependencyInjector']


class ComponentRegistry:
    """Registry for managing component instances - Singleton Pattern"""
    
    _instance: Optional['ComponentRegistry'] = None
    
    def __new__(cls) -> 'ComponentRegistry':
        import threading
        if not hasattr(cls, '_lock'):
            cls._lock = threading.Lock()
        
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._components = {}
        return cls._instance
    
    def register(self, name: str, component: Any) -> None:
        """Register a component with thread safety"""
        with self._lock:
            self._components[name] = component
    
    def get(self, name: str) -> Optional[Any]:
        """Get a registered component with thread safety"""
        with self._lock:
            return self._components.get(name)
    
    def unregister(self, name: str) -> bool:
        """Unregister a component with thread safety"""
        with self._lock:
            if name in self._components:
                del self._components[name]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all registered components with thread safety"""
        with self._lock:
            self._components.clear()


class DependencyInjector:
    """Thread-safe dependency injection container"""
    
    def __init__(self):
        self._bindings: Dict[Type, Type] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = threading.Lock()
    
    def bind(self, interface: Type, implementation: Type) -> None:
        """Bind interface to implementation with thread safety"""
        with self._lock:
            self._bindings[interface] = implementation
    
    def bind_singleton(self, interface: Type, implementation: Type) -> None:
        """Bind interface to singleton implementation with thread safety"""
        with self._lock:
            self._bindings[interface] = implementation
            self._singletons[interface] = None
    
    def get(self, interface: Type) -> Any:
        """Get instance with atomic thread-safe pattern"""
        with self._lock:
            singleton = self._get_singleton(interface)
            return singleton if singleton is not None else self._create_instance(interface)
    
    def _get_singleton(self, interface: Type) -> Optional[Any]:
        """Thread-safe singleton creation with proper locking"""
        # Check if interface is registered for singleton
        if interface not in self._singletons:
            return None
            
        # Thread-safe singleton creation
        with self._lock:
            if self._singletons[interface] is None:
                implementation = self._bindings[interface]
                try:
                    self._singletons[interface] = implementation()
                except (TypeError, AttributeError, ValueError) as e:
                    raise ValueError(f"Failed to instantiate singleton {interface.__name__}: {str(e)}") from e
            return self._singletons[interface]
    
    def _create_instance(self, interface: Type) -> Any:
        """Create new instance"""
        with self._lock:
            if interface not in self._bindings:
                raise ValueError(f"No binding found for {interface}")
            
            implementation = self._bindings[interface]
            try:
                return implementation()
            except (TypeError, AttributeError, ValueError) as e:
                raise ValueError(f"Failed to instantiate {interface.__name__}: {str(e)}") from e
    
