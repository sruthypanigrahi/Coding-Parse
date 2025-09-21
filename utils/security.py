"""Centralized security utilities for path validation"""
import os
from pathlib import Path
from typing import Union
from logger_config import setup_logger

logger = setup_logger(__name__)

class SecurePathValidator:
    """Centralized secure path validation to prevent CWE-22 vulnerabilities"""
    
    @staticmethod
    def validate_and_resolve(filename: Union[str, Path], base_dir: Union[str, Path] = None) -> Path:
        """
        Secure path validation preventing all path traversal attacks
        
        Args:
            filename: Input filename or path
            base_dir: Base directory to restrict access to (defaults to cwd)
            
        Returns:
            Resolved secure path
            
        Raises:
            ValueError: If path is invalid or contains traversal attempts
        """
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Convert to string and sanitize
        clean_name = str(filename).replace('\x00', '').strip()
        if not clean_name:
            raise ValueError("Invalid filename after sanitization")
        
        # Create path object
        path_obj = Path(clean_name)
        
        # Reject absolute paths
        if path_obj.is_absolute():
            raise ValueError("Absolute paths not allowed")
        
        # Set base directory with thread-safe caching
        if base_dir is None:
            import threading
            if not hasattr(SecurePathValidator, '_cached_cwd'):
                with threading.Lock():
                    if not hasattr(SecurePathValidator, '_cached_cwd'):
                        SecurePathValidator._cached_cwd = Path.cwd().resolve()
            base_resolved = SecurePathValidator._cached_cwd
        else:
            base_resolved = Path(base_dir).resolve()
        
        # Validate no path traversal attempts
        if '..' in clean_name or '/' in clean_name or '\\' in clean_name:
            raise ValueError("Path traversal attempts not allowed")
        
        # Construct candidate path using only filename for security
        safe_filename = path_obj.name  # Only filename, no directory components
        if not safe_filename or safe_filename in ('.', '..') or '/' in safe_filename or '\\' in safe_filename:
            raise ValueError("Invalid filename")
        candidate_path = base_resolved / safe_filename
        
        try:
            # Resolve to canonical form
            resolved_path = candidate_path.resolve(strict=False)
            
            # Ensure resolved path is within base directory
            resolved_path.relative_to(base_resolved)
            
            return resolved_path
            
        except (OSError, ValueError) as e:
            raise ValueError(f"Path validation failed: {e}") from e
    
    @staticmethod
    def validate_file_access(filepath: Path) -> Path:
        """Validate file exists and is accessible"""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath.name}")
        
        if not filepath.is_file():
            raise ValueError(f"Path is not a file: {filepath.name}")
        
        return filepath

__all__ = ['SecurePathValidator']