"""
Validation Exceptions
"""

from typing import Optional

__all__ = ['ValidationError']


class ValidationError(Exception):
    """Custom validation error with secure messaging"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code