
import re
from typing import List
from models import TOCEntry
from constants import SECTION_PATTERN


class SectionFilter:
    def __init__(self):
        self._pattern = re.compile(SECTION_PATTERN)
    
    def filter_numbered_sections(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter entries to keep only numbered sections"""
        filtered = []
        
        for entry in entries:
            if self._is_numbered_section(entry):
                if not entry.parent_id:
                    entry.parent_id = None
                filtered.append(entry)
        
        return filtered
    
    def _is_numbered_section(self, entry: TOCEntry) -> bool:
        """Check if entry has numeric section ID"""
        return bool(entry.section_id and self._pattern.match(entry.section_id))