"""
Content Models
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import html
import re
from .base import BaseModel

__all__ = ['ContentEntry', 'ImageInfo', 'TableInfo']


@dataclass
class ContentEntry(BaseModel):
    """Perfect content entry with optimized processing"""
    doc_title: str
    section_id: str
    title: str
    page_range: str
    content: str
    content_type: str = "section_with_images_tables"
    has_content: bool = True
    word_count: int = field(default=0)
    images: List['ImageInfo'] = field(default_factory=list)
    tables: List['TableInfo'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize computed fields efficiently with security"""
        if self.content:
            # Efficient word counting using performance optimizer
            from utils.performance import PerformanceOptimizer
            self.word_count = PerformanceOptimizer.efficient_word_count(self.content)
            self.has_content = bool(self.content.strip())
        else:
            self.word_count = 0
            self.has_content = False
    
    def get_content_summary(self, max_length: int = 200) -> str:
        """Get content summary with safe truncation"""
        if not self.content or len(self.content) <= max_length:
            return self.content
        
        truncated = self.content[:max_length]
        if ' ' in truncated:
            return truncated.rsplit(' ', 1)[0] + "..."
        return truncated + "..."


@dataclass
class ImageInfo(BaseModel):
    """Perfect image information with metadata validation"""
    page: int
    index: int
    xref: int
    width: int
    height: int
    colorspace: str
    size_bytes: int = None
    format: str = None
    
    def __post_init__(self):
        """Validate image metadata"""
        # Conditional validation for better performance
        if self.page < 1:
            self.page = 1
        if self.index < 1:
            self.index = 1
        if self.xref < 0:
            self.xref = 0
        if self.width < 0:
            self.width = 0
        if self.height < 0:
            self.height = 0
        
        # Sanitize string fields
        self.colorspace = html.escape(self.colorspace) if self.colorspace else "Unknown"
        if self.format:
            self.format = html.escape(self.format)
    
    def get_dimensions(self) -> str:
        """Get formatted dimensions"""
        return f"{self.width}x{self.height}"
    
    def get_aspect_ratio(self) -> float:
        """Calculate aspect ratio with comprehensive validation"""
        if self.height > 0 and self.width > 0:
            return self.width / self.height
        return 0.0  # Invalid dimensions


@dataclass
class TableInfo(BaseModel):
    """Perfect table information with enhanced validation"""
    page: int
    index: int
    rows: int
    cols: int
    data: List[List[str]] = field(default_factory=list)
    headers: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize headers with bounds checking and sanitization"""
        # Conditional validation for better performance
        if self.page < 1:
            self.page = 1
        if self.index < 1:
            self.index = 1
        if self.rows < 0:
            self.rows = 0
        if self.cols < 0:
            self.cols = 0
        
        # Sanitize table data
        if self.data:
            self.data = [
                [html.escape(str(cell)) if isinstance(cell, str) else str(cell) for cell in row]
                for row in self.data
            ]
            
            # Set headers from first row if not provided and data exists
            if not self.headers and self.data:
                self.headers = self.data[0]
        
        # Sanitize headers
        if self.headers:
            self.headers = [html.escape(str(header)) if isinstance(header, str) else str(header) 
                          for header in self.headers]
    
    def get_cell_count(self) -> int:
        """Get total cell count"""
        return self.rows * self.cols
    
    def is_valid(self) -> bool:
        """Validate table structure"""
        return self.rows > 0 and self.cols > 0 and bool(self.data)
    
    def get_escaped_content(self) -> str:
        """Get HTML-escaped table summary for safe output"""
        if not self.data:
            return "Empty table"
        summary = f"Table with {self.rows} rows and {self.cols} columns"
        return html.escape(summary)