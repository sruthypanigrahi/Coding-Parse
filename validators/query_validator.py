"""
Search Query Validation
"""

from constants import MIN_QUERY_LENGTH
from .exceptions import ValidationError

__all__ = ['QueryValidator']


class QueryValidator:
    """Search query validation"""
    
    # Class-level constants for performance
    DANGEROUS_CHARS = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
    TRANSLATION_TABLE = str.maketrans('', '', ''.join(DANGEROUS_CHARS))
    
    @classmethod
    def validate_search_query(cls, query: str) -> str:
        """
        Validate search query with security checks
        
        Args:
            query: Search query string
            
        Returns:
            str: Validated and sanitized query
            
        Raises:
            ValidationError: If validation fails
        """
        if not query:
            raise ValidationError("Search query cannot be empty", "EMPTY_QUERY")
        
        if not isinstance(query, str):
            raise ValidationError("Search query must be a string", "INVALID_TYPE")
        
        # Sanitize query
        sanitized_query = query.strip()
        
        # Length validation
        if len(sanitized_query) < MIN_QUERY_LENGTH:
            raise ValidationError(
                f"Search query must be at least {MIN_QUERY_LENGTH} characters", 
                "QUERY_TOO_SHORT"
            )
        
        # Security: Remove potentially dangerous characters efficiently
        sanitized_query = sanitized_query.translate(cls.TRANSLATION_TABLE)
        
        if not sanitized_query:
            raise ValidationError("Search query contains only invalid characters", "INVALID_CHARACTERS")
        
        return sanitized_query