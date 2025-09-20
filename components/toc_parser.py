"""TOC parser with hierarchy building"""
import re
from typing import List
from interfaces import Parseable
from models import TOCEntry
from constants import DOC_TITLE
from logger_config import setup_logger
from .pdf_processor import PDFProcessor


class TOCParser(Parseable):
    """TOC parser with hierarchy building and error handling"""
    
    def __init__(self, processor: PDFProcessor):
        """Initialize TOC parser"""
        self.processor = processor
        self._logger = setup_logger(self.__class__.__name__)
        self._section_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.+?)$')
    
    def parse(self) -> List[TOCEntry]:
        """Parse TOC with comprehensive error handling"""
        try:
            toc = self.processor.document.get_toc()
            if not toc:
                self._logger.warning("No TOC found in document")
                return []
            
            # Use generator for memory efficiency with large TOCs
            entries = (self._create_entry(level, title, page) for level, title, page in toc)
            return self._build_hierarchy(list(entries))
            
        except RuntimeError as e:
            self._logger.error(f"Document access failed: {e}")
            return []
        except Exception as e:
            self._logger.error(f"TOC parsing failed: {str(e)}")
            return []
    
    def _create_entry(self, level: int, title: str, page: int) -> TOCEntry:
        """Create TOC entry with error handling"""
        match = self._section_pattern.match(title.strip())
        section_id = match.group(1) if match else ""
        section_title = match.group(2) if match else title.strip()
        
        return TOCEntry(
            doc_title=DOC_TITLE,
            section_id=section_id, 
            title=section_title, 
            page=max(1, page),
            level=max(0, level)
        )
    
    def _build_hierarchy(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Build hierarchy with error handling"""
        result, parent_stack = [], []
        
        for entry in entries:
            if not entry.section_id or not entry.section_id.replace('.', '').isdigit():
                continue
            
            try:
                depth = len(entry.section_id.split('.'))
                parent_stack = parent_stack[:max(0, depth-1)]
                entry.parent_id = parent_stack[-1] if parent_stack else None
                result.append(entry)
                parent_stack.append(entry.section_id)
            except (AttributeError, ValueError) as e:
                self._logger.warning(f"Hierarchy build failed for {entry.section_id}: {e}")
                continue
        
        self._logger.info(f"Built hierarchy for {len(result)} entries")
        return result