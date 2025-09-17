"""Advanced filtering system with strategy pattern"""
import re
from typing import List, Protocol, Callable
from abc import ABC, abstractmethod

from models import TOCEntry
from constants import SECTION_PATTERN
from logger_config import setup_logger

logger = setup_logger(__name__)


class FilterStrategy(Protocol):
    """Protocol for filter strategies"""
    def apply(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Apply filter to entries"""
        ...


class BaseFilter(ABC):
    """Abstract base class for filters"""
    
    @abstractmethod
    def filter(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter entries based on criteria"""
        pass
    
    def __call__(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Make filter callable"""
        return self.filter(entries)


class NumberedSectionFilter(BaseFilter):
    """Filter for numbered sections with compiled regex"""
    
    def __init__(self):
        self._pattern = re.compile(SECTION_PATTERN)
        logger.debug(f"Initialized NumberedSectionFilter with pattern: {SECTION_PATTERN}")
    
    def filter(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter to keep only numbered sections"""
        filtered = []
        
        for entry in entries:
            if self._is_numbered_section(entry):
                # Ensure parent_id is properly set
                if not entry.parent_id:
                    entry.parent_id = None
                filtered.append(entry)
        
        logger.info(
            f"Filtered {len(entries)} entries to {len(filtered)} numbered sections"
        )
        return filtered
    
    def _is_numbered_section(self, entry: TOCEntry) -> bool:
        """Check if entry has numeric section ID using compiled regex"""
        return bool(entry.section_id and self._pattern.match(entry.section_id))


class LevelFilter(BaseFilter):
    """Filter sections by level depth"""
    
    def __init__(self, max_level: int = 10, min_level: int = 1):
        self.max_level = max_level
        self.min_level = min_level
    
    def filter(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter entries by level range"""
        filtered = [
            entry for entry in entries
            if self.min_level <= entry.level <= self.max_level
        ]
        
        logger.debug(f"Level filter: {len(entries)} -> {len(filtered)} entries "
                    f"(levels {self.min_level}-{self.max_level})")
        return filtered


class ContentFilter(BaseFilter):
    """Filter sections based on content criteria"""
    
    def __init__(self, min_title_length: int = 3, exclude_empty: bool = True):
        self.min_title_length = min_title_length
        self.exclude_empty = exclude_empty
    
    def filter(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter based on content quality"""
        filtered = []
        
        for entry in entries:
            # Check title length
            if len(entry.title.strip()) < self.min_title_length:
                continue
            
            # Check for empty sections if required
            if self.exclude_empty and not entry.title.strip():
                continue
            
            filtered.append(entry)
        
        logger.debug(f"Content filter: {len(entries)} -> {len(filtered)} entries")
        return filtered


class CompositeFilter(BaseFilter):
    """Composite filter that applies multiple filters in sequence"""
    
    def __init__(self, filters: List[BaseFilter]):
        self.filters = filters
        logger.debug(f"Created composite filter with {len(filters)} sub-filters")
    
    def filter(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Apply all filters in sequence"""
        result = entries
        
        for i, filter_instance in enumerate(self.filters):
            initial_count = len(result)
            result = filter_instance.filter(result)
            logger.debug(f"Filter {i+1}: {initial_count} -> {len(result)} entries")
        
        logger.info(
            f"Composite filter: {len(entries)} -> {len(result)} entries"
        )
        return result
    
    def add_filter(self, filter_instance: BaseFilter) -> None:
        """Add filter to the chain"""
        self.filters.append(filter_instance)


class SectionFilter:
    """Main section filter with configurable strategies"""
    
    def __init__(self, use_composite: bool = False):
        self.use_composite = use_composite
        
        if use_composite:
            self._filter = CompositeFilter([
                NumberedSectionFilter(),
                ContentFilter(min_title_length=2),
                LevelFilter(max_level=8)
            ])
        else:
            self._filter = NumberedSectionFilter()
    
    def filter_numbered_sections(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter entries to keep only numbered sections"""
        if not entries:
            logger.warning("No entries provided for filtering")
            return []
        
        try:
            filtered = self._filter.filter(entries)
            
            # Post-processing: ensure hierarchy consistency
            filtered = self._ensure_hierarchy_consistency(filtered)
            
            return filtered
            
        except Exception as e:
            logger.error(f"Filtering failed: {e}")
            return entries  # Return original on error
    
    def _ensure_hierarchy_consistency(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Ensure parent-child relationships are consistent"""
        section_ids = {entry.section_id for entry in entries}
        
        for entry in entries:
            # Check if parent exists in filtered set
            if entry.parent_id and entry.parent_id not in section_ids:
                # Find closest existing parent
                entry.parent_id = (
                    self._find_closest_parent(entry.section_id, section_ids)
                )
        
        return entries
    
    def _find_closest_parent(self, section_id: str, available_ids: set) -> str:
        """Find the closest available parent section"""
        if not section_id or '.' not in section_id:
            return None
        
        parts = section_id.split('.')
        
        # Try progressively shorter parent paths
        for i in range(len(parts) - 1, 0, -1):
            parent_candidate = '.'.join(parts[:i])
            if parent_candidate in available_ids:
                return parent_candidate
        
        return None


# Factory function for creating filters
def create_filter(filter_type: str = "numbered", **kwargs) -> BaseFilter:
    """Factory function to create filters"""
    filters = {
        "numbered": NumberedSectionFilter,
        "level": LevelFilter,
        "content": ContentFilter,
        "composite": CompositeFilter
    }
    
    if filter_type not in filters:
        raise ValueError(f"Unknown filter type: {filter_type}")
    
    return filters[filter_type](**kwargs)