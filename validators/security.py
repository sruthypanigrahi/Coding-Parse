"""
Security Validation Utilities
"""

import os
from pathlib import Path
from constants import MAX_FILE_SIZE
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['SecurityValidator']


class SecurityValidator:
    """Security-focused validation utilities"""
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Alias for is_safe_path for compatibility"""
        return SecurityValidator.is_safe_path(file_path)
    
    @staticmethod
    def is_safe_path(file_path: str) -> bool:
        """
        Comprehensive path safety validation
        
        Args:
            file_path: Path to validate
            
        Returns:
            bool: True if path is safe
        """
        if not file_path or not isinstance(file_path, str):
            return False
        
        # Split complex validation into clear steps for better maintainability
        has_path_traversal = '../' in file_path or '..\\' in file_path
        dangerous_chars = ['~', '$', '`', '|', ';', '&', '>', '<']
        has_dangerous_chars = any(pattern in file_path for pattern in dangerous_chars)
        
        if has_path_traversal or has_dangerous_chars:
            return False
        
        # Check for absolute paths (security risk)
        if os.path.isabs(file_path):
            return False
        
        try:
            # Resolve path and ensure it's within current directory
            resolved_path = Path(file_path).resolve()
            cwd = Path.cwd().resolve()
            resolved_path.relative_to(cwd)
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def validate_file_size(file_path: Path) -> bool:
        """
        Validate file size against limits
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if file size is acceptable
        """
        try:
            return file_path.stat().st_size <= MAX_FILE_SIZE
        except OSError as e:
            logger.warning(f"File size validation failed: {type(e).__name__}")
            return False