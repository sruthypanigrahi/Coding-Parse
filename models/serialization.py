"""Serialization utilities to reduce complexity"""
from typing import Dict, Any, List
import html
from logger_config import setup_logger

logger = setup_logger(__name__)

class SerializationHelper:
    """Helper class for serialization operations"""
    
    @staticmethod
    def serialize_value(key: str, value: Any) -> Any:
        """Serialize individual value with type checking"""
        try:
            # Cache to_dict check to avoid redundant calls
            has_to_dict = SerializationHelper._has_to_dict_method(value)
            if has_to_dict:
                return value.to_dict()
            elif isinstance(value, list):
                return SerializationHelper._serialize_list(value)
            elif isinstance(value, dict):
                return SerializationHelper._serialize_dict(value)
            elif isinstance(value, str):
                return html.escape(value)
            else:
                return value
        except Exception as e:
            logger.warning(f"Serialization failed for key {key}: {e}")
            return str(value) if value is not None else None
    
    @staticmethod
    def _serialize_list(items: List[Any]) -> List[Any]:
        """Serialize list items"""
        return [
            item.to_dict() if SerializationHelper._has_to_dict_method(item) else item 
            for item in items if item is not None
        ]
    
    @staticmethod
    def _serialize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize dictionary values recursively"""
        return {
            k: SerializationHelper.serialize_value(k, v)
            for k, v in data.items()
        }
    
    @staticmethod
    def _has_to_dict_method(obj) -> bool:
        """Check if object has to_dict method"""
        return hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict'))