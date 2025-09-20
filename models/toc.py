"""
Table of Contents Models
"""

from dataclasses import dataclass, field
from typing import Optional, List, ClassVar
import html
import re
from .base import BaseModel

__all__ = ['TOCEntry']


@dataclass
class TOCEntry(BaseModel):
    """Perfect TOC entry with comprehensive validation"""
    doc_title: str = "USB Power Delivery Specification"
    section_id: str = ""
    title: str = ""
    page: int = 0
    level: int = 0
    parent_id: Optional[str] = None
    full_path: str = field(default="")
    children: List['TOCEntry'] = field(default_factory=list)
    
    # Validation patterns
    _section_pattern: ClassVar[re.Pattern] = re.compile(r'^\d+(\.\d+)*$')
    
    def __post_init__(self):
        """Initialize computed fields with validation"""
        # Validate inputs
        if self.page < 0:
            self.page = 0
        if self.level < 0:
            self.level = 0
            
        # Sanitize string inputs
        self.doc_title = html.escape(self.doc_title) if self.doc_title else ""
        self.title = html.escape(self.title) if self.title else ""
        
        # Generate full path using already escaped values
        if not self.full_path:
            self.full_path = f"{self.section_id} {self.title}" if self.section_id else self.title
    
    def is_valid_section_id(self) -> bool:
        """Validate section ID format"""
        return bool(self.section_id and self._section_pattern.match(self.section_id))
    
    def get_depth(self) -> int:
        """Get section depth from section ID"""
        return len(self.section_id.split('.')) if self.section_id else 0