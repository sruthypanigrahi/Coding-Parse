"""Data models for PDF parsing"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TOCEntry:
    section_id: str
    title: str
    page: int
    level: int
    parent_id: Optional[str] = None
    full_path: str = ""
    
    def __post_init__(self):
        if not self.full_path:
            self.full_path = f"{self.section_id} {self.title}"


@dataclass
class ContentEntry:
    doc_title: str
    section_id: str
    title: str
    page_range: str
    content: str
    content_type: str = "section_with_images_tables"
    has_content: bool = True


@dataclass
class ImageInfo:
    page: int
    index: int
    xref: int
    width: int
    height: int
    colorspace: str


@dataclass
class TableInfo:
    page: int
    index: int
    rows: int
    cols: int
    data: List[List[str]]