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
        self._cached_page_count = None
        import threading
        self._page_count_lock = threading.RLock()
    
    def _get_cached_page_count(self) -> int:
        """Thread-safe cached page count access"""
        if self._cached_page_count is None:
            with self._page_count_lock:
                if self._cached_page_count is None:
                    try:
                        self._cached_page_count = self.processor.page_count
                    except RuntimeError:
                        self._cached_page_count = 1
        return self._cached_page_count
    
    def extract(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        """Extract content with optimal strategy"""
        if not entries:
            return []
        
        if len(entries) >= PARALLEL_THRESHOLD:
            return self.parallel_extractor.extract_parallel(entries)
        else:
            return self._extract_sequential(entries)
    
    def _extract_sequential(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        """Sequential extraction with error handling"""
        results = []
        # Use generator for memory efficiency with large datasets
        valid_entries = ((i, entry) for i, entry in enumerate(entries) if entry.section_id and entry.section_id.strip())
        
        for i, entry in valid_entries:
            try:
                result = self._extract_single(entry, entries, i)
                if result:
                    results.append(result)
            except (AttributeError, ValueError, RuntimeError) as e:
                self._logger.warning(f"Failed to extract content for {entry.section_id}: {type(e).__name__}")
                continue
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
                # Image and table extraction implementation
                images=self._extract_images(start, end),
                tables=self._extract_tables(start, end)
            )
        except (AttributeError, ValueError, RuntimeError) as e:
            self._logger.error(f"Extraction failed for {entry.section_id}: {type(e).__name__}")
            return None
    
    def _get_page_range(self, entry: TOCEntry, all_entries: List[TOCEntry], index: int) -> Tuple[int, int]:
        """Get comprehensive page range for multi-page sections"""
        start = max(1, entry.page)
        
        # Enhanced logic for multi-page sections
        if index + 1 < len(all_entries):
            next_entry = all_entries[index + 1]
            # If next section is at same level or higher, use its page - 1
            if next_entry.level <= entry.level:
                end = max(start, next_entry.page - 1)
            else:
                # For subsections, look ahead to find the next peer section
                end = self._find_section_end(entry, all_entries, index)
        else:
            try:
                end = max(start, self._get_cached_page_count())
            except (RuntimeError, AttributeError):
                end = start + 5  # Default multi-page range
        
        # Ensure minimum coverage for substantial sections
        if end - start < 2 and entry.level <= 2:  # Major sections get more pages
            end = min(start + 3, self._get_cached_page_count())
        
        return start, end
    
    def _extract_text(self, start: int, end: int) -> str:
        """Extract text efficiently"""
        texts = []
        page_count = self._get_cached_page_count()
            
        for page_num in range(start - 1, min(end, page_count)):
            text = self._get_page_text(page_num)
            if text:
                texts.append(text)
        return self.text_processor.join_page_texts(texts)
    
    def _extract_images(self, start: int, end: int) -> List[dict]:
        """Extract images from page range"""
        images = []
        try:
            page_count = self._get_cached_page_count()
            for page_num in range(start - 1, min(end, page_count)):
                page = self.processor.document[page_num]
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    images.append({
                        'page': page_num + 1,
                        'index': img_index,
                        'width': img[2] if len(img) > 2 else 0,
                        'height': img[3] if len(img) > 3 else 0
                    })
        except (AttributeError, RuntimeError, IndexError) as e:
            self._logger.debug(f"Image extraction failed for pages {start}-{end}: {type(e).__name__}")
        return images
    
    def _extract_tables(self, start: int, end: int) -> List[dict]:
        """Extract tables from page range"""
        tables = []
        try:
            page_count = self._get_cached_page_count()
            for page_num in range(start - 1, min(end, page_count)):
                page = self.processor.document[page_num]
                # Basic table detection using text blocks
                blocks = page.get_text("dict")["blocks"]
                table_blocks = [b for b in blocks if self._is_table_block(b)]
                for i, block in enumerate(table_blocks):
                    tables.append({
                        'page': page_num + 1,
                        'index': i,
                        'rows': len(block.get('lines', [])),
                        'bbox': block.get('bbox', [])
                    })
        except (AttributeError, RuntimeError, IndexError, KeyError) as e:
            self._logger.debug(f"Table extraction failed for pages {start}-{end}: {type(e).__name__}")
        return tables
    
    def _is_table_block(self, block: dict) -> bool:
        """Simple heuristic to detect table-like blocks"""
        lines = block.get('lines', [])
        if len(lines) < 2:
            return False
        # Check for consistent spacing patterns with early termination
        spans_per_line = [len(line.get('spans', [])) for line in lines]
        return len(set(spans_per_line)) <= 2 and any(count > 2 for count in spans_per_line)
    
    def _find_section_end(self, entry: TOCEntry, all_entries: List[TOCEntry], index: int) -> int:
        """Find the end page for a section by looking for next peer"""
        for i in range(index + 1, len(all_entries)):
            next_entry = all_entries[i]
            if next_entry.level <= entry.level:
                return max(entry.page, next_entry.page - 1)
        
        # If no peer found, extend to reasonable range
        try:
            return min(entry.page + 10, self._get_cached_page_count())
        except (RuntimeError, AttributeError):
            return entry.page + 5
    
    def _get_page_text(self, page_num: int) -> str:
        """Get page text efficiently with cached page count"""
        try:
            # Early return for obviously invalid pages
            if page_num < 0:
                return ""
            
            page_count = self._get_cached_page_count()
            if page_num < page_count:
                text = self.processor.document[page_num].get_text("text")
                return (text or "").strip()
            return ""
        except (IndexError, AttributeError, OSError, RuntimeError):
            return ""