"""Data models with clean OOP design"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json



@dataclass
class BaseModel:
    """Base model with serialization"""
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list) and value and hasattr(value[0], 'to_dict'):
                result[key] = [item.to_dict() for item in value]
            else:
                result[key] = value
        return result


@dataclass
class TOCEntry(BaseModel):
    """Table of Contents entry with all required fields"""
    doc_title: str = "USB Power Delivery Specification"
    section_id: str = ""
    title: str = ""
    page: int = 0
    level: int = 0
    parent_id: Optional[str] = None
    full_path: str = field(default="")
    children: List['TOCEntry'] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.full_path:
            self.full_path = f"{self.section_id} {self.title}" if self.section_id else self.title


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
        self.word_count = len(self.content.split()) if self.content else 0
        self.has_content = bool(self.content and self.content.strip())


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
    
    pass


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
        if self.data and not self.headers:
            self.headers = self.data[0] if self.data else []


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