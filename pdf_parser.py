"""PDF parsing functionality with OOP design"""
import json
import re
import fitz
from pathlib import Path
from typing import List
from models import TOCEntry
from constants import DOC_TITLE, SECTION_TITLE_PATTERN


class PDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc_title = DOC_TITLE
        self._doc = None
    
    def __enter__(self):
        self._doc = fitz.open(self.pdf_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._doc:
            self._doc.close()
    
    def extract_toc(self) -> List[TOCEntry]:
        """Extract table of contents from PDF bookmarks"""
        if not self._doc:
            raise RuntimeError("PDF not opened. Use context manager.")
        
        outline = self._doc.get_toc()
        if not outline:
            return []
        
        return [self._create_toc_entry(level, title, page) 
                for level, title, page in outline]
    
    def _create_toc_entry(self, level: int, title: str, page: int) -> TOCEntry:
        """Create TOC entry from raw data"""
        title = title.strip()
        match = re.match(SECTION_TITLE_PATTERN, title)
        
        if match:
            section_id = match.group(1)
            section_title = match.group(2)
        else:
            section_id = ""
            section_title = title
        
        return TOCEntry(
            section_id=section_id,
            title=section_title,
            page=page,
            level=level
        )
    
    def build_hierarchy(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Build parent-child relationships"""
        result = []
        parent_stack = []
        
        for entry in entries:
            if not entry.section_id:
                continue
            
            level = len(entry.section_id.split('.'))
            entry.level = level
            
            # Adjust parent stack
            while len(parent_stack) >= level:
                parent_stack.pop()
            
            entry.parent_id = parent_stack[-1] if parent_stack else None
            entry.full_path = f"{entry.section_id} {entry.title}"
            
            result.append(entry)
            parent_stack.append(entry.section_id)
        
        return result


class JSONLWriter:
    @staticmethod
    def save(entries: List, filename: str) -> None:
        """Save entries to JSONL file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in entries:
                if hasattr(entry, '__dict__'):
                    data = entry.__dict__
                else:
                    data = entry
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        print(f"Saved {len(entries)} entries to {filename}")