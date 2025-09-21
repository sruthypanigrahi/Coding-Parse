"""Performance optimization utilities"""
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

class PerformanceOptimizer:
    """Centralized performance optimizations"""
    
    # Pre-compiled regex patterns for better performance
    WORD_PATTERN = re.compile(r'\b\w{2,}\b')
    NUMERIC_PATTERN = re.compile(r'^\d+(?:\.\d+)*$')
    CONTROL_CHAR_PATTERN = re.compile(r'[^\x20-\x7E\t\n\r]')
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_resolved_cwd() -> Path:
        """Cached current working directory resolution"""
        return Path.cwd().resolve()
    
    @staticmethod
    def sanitize_log_message(message: str) -> str:
        """Efficient log message sanitization"""
        if not message:
            return ""
        # Use pre-compiled regex for better performance
        return PerformanceOptimizer.CONTROL_CHAR_PATTERN.sub('', message)
    
    @staticmethod
    def efficient_word_count(text: str) -> int:
        """Efficient word counting using pre-compiled regex"""
        if not text:
            return 0
        return len(PerformanceOptimizer.WORD_PATTERN.findall(text))
    
    @staticmethod
    def is_numeric_section(section_id: str) -> bool:
        """Efficient numeric section ID validation"""
        if not section_id:
            return False
        return bool(PerformanceOptimizer.NUMERIC_PATTERN.match(section_id))

__all__ = ['PerformanceOptimizer']