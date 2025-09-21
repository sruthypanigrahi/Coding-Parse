"""
Path and File System Validation
"""

import os
from pathlib import Path
from .exceptions import ValidationError
from .security import SecurityValidator

__all__ = ['PathValidator']


class PathValidator:
    """Path and file system validation"""
    
    def __init__(self):
        self._security = SecurityValidator()
    
    def validate_output_path(self, output_path: str) -> Path:
        """
        Validate output file path with comprehensive security checks
        
        Args:
            output_path: Output file path
            
        Returns:
            Path: Validated and resolved path
            
        Raises:
            ValidationError: If validation fails
        """
        if not output_path:
            raise ValidationError("Output path cannot be empty", "EMPTY_PATH")
        
        if not isinstance(output_path, str):
            raise ValidationError("Output path must be a string", "INVALID_TYPE")
        
        # Security validation
        if not self._security.is_safe_path(output_path):
            raise ValidationError("Invalid output path - security violation", "SECURITY_VIOLATION")
        
        try:
            file_path = Path(output_path).resolve()
            
            # Ensure path is within current working directory
            cwd = Path.cwd().resolve()
            try:
                file_path.relative_to(cwd)
            except ValueError:
                raise ValidationError("Output path must be within current directory", "PATH_OUTSIDE_CWD")
            
            # Create parent directory with comprehensive error handling
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise ValidationError(f"Cannot create output directory: {str(e)}", "DIRECTORY_CREATION_FAILED")
            
            # Check write permissions
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise ValidationError("No write permission for output file", "NO_WRITE_PERMISSION")
            
            if not file_path.exists() and not os.access(file_path.parent, os.W_OK):
                raise ValidationError("No write permission for output directory", "NO_WRITE_PERMISSION")
            
            return file_path
            
        except (OSError, ValueError) as e:
            raise ValidationError(f"Output path validation failed: {str(e)}", "PATH_ERROR")
    
    @staticmethod
    def validate_page_number(page: int, max_pages: int) -> int:
        """
        Validate page number
        
        Args:
            page: Page number to validate
            max_pages: Maximum allowed page number
            
        Returns:
            int: Validated page number
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(page, int):
            raise ValidationError("Page number must be an integer", "INVALID_TYPE")
        
        if page < 1:
            raise ValidationError("Page number must be positive", "INVALID_PAGE")
        
        if page > max_pages:
            raise ValidationError(f"Page number exceeds maximum ({max_pages})", "PAGE_OUT_OF_RANGE")
        
        return page