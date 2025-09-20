"""Streamlined content extractor"""
from typing import List, Tuple, Optional
from interfaces import Extractable
from models import TOCEntry, ContentEntry
from constants import DOC_TITLE, PARALLEL_THRESHOLD
from logger_config import setup_logger
from ..pdf_processor import PDFProcessor
from .text_processor import TextProcessor
from .parallel_extractor import ParallelExtractor

class ContentExtractor(Extractable):
    """High-performance content extractor"""
    
    def __init__(self, processor: PDFProcessor):
        self.processor = processor
        self._logger = setup_logger(self.__class__.__name__)
        self.text_processor = TextProcessor()
        self.parallel_extractor = ParallelExtractor(self._extract_single)
    
    def extract(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        """Extract content with optimal strategy"""
        if not entries:
            return []
        
        if len(entries) >= PARALLEL_THRESHOLD:
            return self.parallel_extractor.extract_parallel(entries)
        else:
            return self._extract_sequential(entries)
    
    def _extract_sequential(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        """Sequential extraction"""
        results = []
        for i, entry in enumerate(entries):
            if entry.section_id:
                result = self._extract_single(entry, entries, i)
                if result:
                    results.append(result)
        return results
    
    def _extract_single(self, entry: TOCEntry, all_entries: List[TOCEntry], index: int) -> Optional[ContentEntry]:
        """Extract single entry content"""
        try:
            start, end = self._get_page_range(entry, all_entries, index)
            content = self._extract_text(start, end)
            content = self.text_processor.truncate_content(content)
            
            return ContentEntry(
                doc_title=DOC_TITLE, 
                section_id=entry.section_id, 
                title=entry.title,
                page_range=f"{start}-{end}", 
                content=content,
                images=[],
                tables=[]
            )
        except Exception as e:
            self._logger.error(f"Extraction failed for {entry.section_id}: {e}")
            return None
    
    def _get_page_range(self, entry: TOCEntry, all_entries: List[TOCEntry], index: int) -> Tuple[int, int]:
        """Get page range for extraction"""
        start = max(1, entry.page)
        if index + 1 < len(all_entries):
            end = max(start, all_entries[index + 1].page - 1)
        else:
            try:
                end = max(start, self.processor.page_count)
            except RuntimeError:
                end = start + 1
        return start, end
    
    def _extract_text(self, start: int, end: int) -> str:
        """Extract text efficiently"""
        texts = []
        try:
            page_count = self.processor.page_count
        except RuntimeError:
            page_count = end
            
        for page_num in range(start - 1, min(end, page_count)):
            text = self._get_page_text(page_num)
            if text:
                texts.append(text)
        return self.text_processor.join_page_texts(texts)
    
    def _get_page_text(self, page_num: int) -> str:
        """Get page text efficiently"""
        try:
            page_count = self.processor.page_count
            if 0 <= page_num < page_count:
                text = self.processor.document[page_num].get_text("text")
                return (text or "").strip()
            return ""
        except (IndexError, AttributeError, OSError, RuntimeError):
            return ""