"""
Base Export Functionality
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from models import TOCEntry, ContentEntry
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['BaseExporter']


class BaseExporter:
    """Base exporter with common functionality"""
    
    def __init__(self):
        self._numeric_pattern = re.compile(r'^\d+(\.\d+)*$')
    
    def _validate_path(self, filename: str) -> Path:
        """Secure path validation preventing all path traversal attacks"""
        import os
        
        # Input sanitization
        if not filename or not isinstance(filename, str):
            raise ValueError("Invalid filename")
        
        # Explicit path traversal checks
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError("Path traversal attempts not allowed")
        
        # Remove null bytes and normalize
        clean_name = filename.replace('\x00', '').strip()
        if not clean_name:
            raise ValueError("Empty filename after sanitization")
        
        # Create path and resolve to canonical form
        path = Path(clean_name)
        if path.is_absolute():
            raise ValueError("Absolute paths not allowed")
        
        # Additional validation for filename components
        if path.name in ('.', '..') or not path.name or '/' in str(path) or '\\' in str(path):
            raise ValueError("Invalid filename")
        
        # Resolve to canonical path
        try:
            resolved_path = path.resolve(strict=False)
            cwd = Path.cwd().resolve()
            
            # Use os.path.commonpath for robust path traversal detection
            common = os.path.commonpath([str(resolved_path), str(cwd)])
            if Path(common).resolve() != cwd:
                raise ValueError("Path traversal attempt detected")
                
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")
        
        return path
    
    def _calculate_stats(self, entries: List[TOCEntry]) -> Dict[str, Any]:
        """Calculate validation statistics"""
        total = len(entries)
        valid = 0
        numbered = 0
        
        for e in entries:
            section_id = e.section_id
            if section_id and e.title and e.page > 0:
                valid += 1
            if section_id and self._numeric_pattern.match(section_id):
                numbered += 1
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'numbered_sections': numbered,
            'validation_score': round((valid / total) * 100, 2) if total > 0 else 0
        }