from dataclasses import dataclass

@dataclass
class TOCEntry:
    """Table of Contents entry with hierarchical structure."""
    doc_title: str
    section_id: str
    title: str
    page: int
    level: int
    
    def to_dict(self):
        return {
            'doc_title': self.doc_title,
            'section_id': self.section_id,
            'title': self.title,
            'page': self.page,
            'level': self.level
        }

@dataclass
class ContentEntry:
    """Content entry with text and image count per page."""
    doc_title: str
    page: int
    content: str
    image_count: int = 0
    
    def to_dict(self):
        return {
            'doc_title': self.doc_title,
            'page': self.page,
            'content': self.content,
            'image_count': self.image_count
        }