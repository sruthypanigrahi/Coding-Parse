"""File finding utilities for search"""
from pathlib import Path
from typing import Optional
from logger_config import setup_logger

logger = setup_logger(__name__)


class FileFinder:
    """Handles file location and validation"""
    
    @staticmethod
    def find_toc_file(filename: str) -> Optional[Path]:
        """Find TOC file with security validation"""
        try:
            toc_path = Path(filename).resolve()
            cwd = Path.cwd().resolve()
            toc_path.relative_to(cwd)  # Security check
            
            if toc_path.exists() and toc_path.is_file():
                return toc_path
        except (OSError, ValueError):
            pass
        
        logger.warning(f"TOC file not found: {filename}")
        return None
    
    @staticmethod
    def find_content_file(filename: str) -> Optional[Path]:
        """Find content file with security validation"""
        try:
            content_file = Path(filename).resolve()
            cwd = Path.cwd().resolve()
            content_file.relative_to(cwd)  # Security check - prevent path traversal
            
            if content_file.exists() and content_file.is_file():
                return content_file
        except (OSError, ValueError):
            pass
        
        return None