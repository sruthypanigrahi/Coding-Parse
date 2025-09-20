"""Filtering components for TOC entries"""
import re
from typing import List
from interfaces import Filterable
from models import TOCEntry
from logger_config import setup_logger


class NumericFilter(Filterable):
    """Filter for numeric section entries"""
    
    def __init__(self):
        """Initialize filter with compiled pattern for performance"""
        self.pattern = re.compile(r'^\d+(?:\.\d+)*$')
        self._logger = setup_logger(self.__class__.__name__)
    
    def apply(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter numeric sections with logging"""
        if not entries:
            return []
        
        filtered = [
            e for e in entries 
            if e.section_id and self.pattern.match(e.section_id)
        ]
        
        self._logger.info(f"Filtered {len(entries)} entries to {len(filtered)} numeric sections")
        return filtered