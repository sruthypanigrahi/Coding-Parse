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
        """Get instance of interface with thread safety"""
        with self._lock:
            if interface in self._singletons:
                if self._singletons[interface] is None:
                    implementation = self._bindings[interface]
                    try:
                        self._singletons[interface] = implementation()
                    except Exception as e:
                        raise ValueError(f"Failed to instantiate singleton {interface.__name__}: {e}")
                return self._singletons[interface]
            
            if interface in self._bindings:
                implementation = self._bindings[interface]
                try:
                    return implementation()
                except Exception as e:
                    raise ValueError(f"Failed to instantiate {interface.__name__}: {e}")
            
            raise ValueError(f"No binding found for {interface}")
    
    def create_instance(self, cls: Type, **kwargs) -> Any:
        """Create instance with dependency injection and error handling"""
        try:
            return cls(**kwargs)
        except Exception as e:
            raise ValueError(f"Failed to create instance of {cls.__name__}: {e}")