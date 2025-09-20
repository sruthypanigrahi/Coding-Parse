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
        """Validate path for security - prevent path traversal"""
        # Security: Check for dangerous patterns first
        if any(dangerous in filename for dangerous in ['..',  '/', '\\', '~']):
            raise ValueError(f"Security violation: Invalid filename {filename}")
        
        # Convert to Path and resolve
        path = Path(filename)
        if path.is_absolute():
            raise ValueError(f"Absolute paths not allowed: {filename}")
        
        # Resolve and validate against working directory
        safe_path = path.resolve()
        cwd = Path.cwd().resolve()
        try:
            safe_path.relative_to(cwd)
        except ValueError:
            raise ValueError(f"Path traversal detected: {filename}")
        
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