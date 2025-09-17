"""Enhanced data models with advanced OOP patterns"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import json
from interfaces import Serializable


@dataclass
class BaseModel(Serializable):
    """Base model with common functionality"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                result[key] = [item.to_dict() for item in value]
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class TOCEntry(BaseModel):
    """Table of Contents entry with enhanced functionality"""
    section_id: str
    title: str
    page: int
    level: int
    parent_id: Optional[str] = None
    full_path: str = field(default="")
    children: List['TOCEntry'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize computed fields"""
        if not self.full_path:
            self.full_path = f"{self.section_id} {self.title}"
    
    def add_child(self, child: 'TOCEntry') -> None:
        """Add child entry"""
        child.parent_id = self.section_id
        self.children.append(child)
    
    def get_depth(self) -> int:
        """Get section depth based on section_id"""
        return len(self.section_id.split('.')) if self.section_id else 0
    
    def is_numbered(self) -> bool:
        """Check if section has numeric ID"""
        import re
        pattern = r'^\d+(\.\d+)*$'
        return bool(self.section_id and re.match(pattern, self.section_id))
    
    def get_ancestors(self) -> List[str]:
        """Get list of ancestor section IDs"""
        if not self.section_id:
            return []
        
        parts = self.section_id.split('.')
        ancestors = []
        for i in range(1, len(parts)):
            ancestors.append('.'.join(parts[:i]))
        return ancestors


@dataclass
class ContentEntry(BaseModel):
    """Content entry with rich metadata"""
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
        """Calculate derived fields"""
        if self.content:
            self.word_count = len(self.content.split())
            self.has_content = bool(self.content.strip())
    
    def get_summary(self, max_length: int = 200) -> str:
        """Get content summary"""
        if not self.content or len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def add_image(self, image: 'ImageInfo') -> None:
        """Add image to content"""
        self.images.append(image)
    
    def add_table(self, table: 'TableInfo') -> None:
        """Add table to content"""
        self.tables.append(table)


@dataclass
class ImageInfo(BaseModel):
    """Image information with metadata"""
    page: int
    index: int
    xref: int
    width: int
    height: int
    colorspace: str
    size_bytes: Optional[int] = None
    format: Optional[str] = None
    
    def get_aspect_ratio(self) -> float:
        """Calculate aspect ratio"""
        return self.width / self.height if self.height > 0 else 0
    
    def is_large(self, threshold: int = 100000) -> bool:
        """Check if image is large"""
        return (self.size_bytes or 0) > threshold


@dataclass
class TableInfo(BaseModel):
    """Table information with enhanced data"""
    page: int
    index: int
    rows: int
    cols: int
    data: List[List[str]] = field(default_factory=list)
    headers: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Extract headers from data"""
        if self.data and not self.headers:
            self.headers = self.data[0] if self.data else []
    
    def get_cell(self, row: int, col: int) -> Optional[str]:
        """Get cell value safely"""
        if 0 <= row < len(self.data) and 0 <= col < len(self.data[row]):
            return self.data[row][col]
        return None
    
    def is_empty(self) -> bool:
        """Check if table has no data"""
        return self.rows == 0 or self.cols == 0 or not self.data


@dataclass
class ProcessingStats(BaseModel):
    """Processing statistics"""
    total_sections: int = 0
    processed_sections: int = 0
    total_pages: int = 0
    total_images: int = 0
    total_tables: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add processing error"""
        self.errors.append(error)
    
    def get_success_rate(self) -> float:
        """Calculate processing success rate"""
        if self.total_sections == 0:
            return 0.0
        return (self.processed_sections / self.total_sections) * 100