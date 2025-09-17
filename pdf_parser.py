"""Advanced PDF parser with performance optimizations"""
import re
import fitz
from pathlib import Path
from typing import List, Iterator, Optional
import time

from models import TOCEntry, ProcessingStats
from interfaces import Parseable, Cacheable
from constants import DOC_TITLE, SECTION_TITLE_PATTERN
from logger_config import setup_logger
from validators import InputValidator, ValidationError
from performance_cache import cached, memory_cache

logger = setup_logger(__name__)


class PDFParser(Parseable, Cacheable):
    """High-performance PDF parser with caching and optimization"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc_title = DOC_TITLE
        self._doc: Optional[fitz.Document] = None
        self._compiled_regex = re.compile(SECTION_TITLE_PATTERN)
        self.stats = ProcessingStats()
    
    def __enter__(self):
        """Context manager entry"""
        try:
            self._doc = fitz.open(self.pdf_path)
            logger.info(f"Opened PDF: {self.pdf_path} ({len(self._doc)} pages)")
            return self
        except Exception as e:
            logger.error(f"Failed to open PDF {self.pdf_path}: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup"""
        if self._doc:
            self._doc.close()
            self._doc = None
        
        if exc_type:
            logger.error(f"PDF parser error: {exc_val}")
    
    def validate_input(self) -> bool:
        """Validate PDF input"""
        try:
            InputValidator.validate_pdf_file(str(self.pdf_path))
            return True
        except ValidationError as e:
            logger.error(f"PDF validation failed: {e}")
            return False
    
    def get_cache_key(self) -> str:
        """Generate cache key based on file path and modification time"""
        stat = self.pdf_path.stat()
        return f"pdf_toc_{self.pdf_path}_{stat.st_mtime}_{stat.st_size}"
    
    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        cache_key = self.get_cache_key()
        return memory_cache.get(cache_key) is not None
    
    @cached(ttl=3600, use_file_cache=True)
    def parse(self) -> List[TOCEntry]:
        """Parse PDF with caching support"""
        if not self.validate_input():
            return []
        
        start_time = time.time()
        
        try:
            raw_entries = self._extract_toc_entries()
            structured_entries = self._build_hierarchy(raw_entries)
            
            self.stats.processing_time = time.time() - start_time
            self.stats.total_sections = len(structured_entries)
            self.stats.processed_sections = len([e for e in structured_entries if e.section_id])
            
            logger.info(f"Parsed {len(structured_entries)} TOC entries in "
                       f"{self.stats.processing_time:.2f}s")
            
            return structured_entries
            
        except Exception as e:
            self.stats.add_error(str(e))
            logger.error(f"TOC parsing failed: {e}")
            return []
    
    def _extract_toc_entries(self) -> List[TOCEntry]:
        """Extract raw TOC entries with error handling"""
        if not self._doc:
            raise RuntimeError("PDF not opened")
        
        outline = self._doc.get_toc()
        if not outline:
            logger.warning("No TOC outline found in PDF")
            return []
        
        entries = []
        for level, title, page in outline:
            try:
                entry = self._create_toc_entry(level, title, page)
                entries.append(entry)
            except Exception as e:
                self.stats.add_error(f"Failed to process TOC entry '{title}': {e}")
                logger.debug(f"Skipping malformed TOC entry: {title}")
                continue
        
        logger.info(f"Extracted {len(entries)} raw TOC entries")
        return entries
    
    def _create_toc_entry(self, level: int, title: str, page: int) -> TOCEntry:
        """Create TOC entry with optimized regex matching"""
        title = title.strip()
        match = self._compiled_regex.match(title)
        
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
            level=level,
            metadata={
                'raw_title': title,
                'extracted_at': time.time()
            }
        )
    
    def _build_hierarchy(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Build hierarchical structure with parent-child relationships"""
        result = []
        parent_stack = []
        
        for entry in entries:
            if not entry.section_id:
                continue
            
            # Calculate level from section ID depth
            calculated_level = entry.get_depth()
            entry.level = calculated_level
            
            # Maintain parent stack
            while len(parent_stack) >= calculated_level:
                parent_stack.pop()
            
            # Set parent relationship
            if parent_stack:
                entry.parent_id = parent_stack[-1]
            
            # Update full path
            entry.full_path = f"{entry.section_id} {entry.title}"
            
            result.append(entry)
            parent_stack.append(entry.section_id)
        
        logger.debug(f"Built hierarchy for {len(result)} entries")
        return result
    
    def get_stats(self) -> ProcessingStats:
        """Get processing statistics"""
        return self.stats
    
    def extract_metadata(self) -> dict:
        """Extract PDF metadata"""
        if not self._doc:
            return {}
        
        try:
            metadata = self._doc.metadata
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(self._doc),
                'file_size': self.pdf_path.stat().st_size
            }
        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {e}")
            return {}


class JSONLWriter:
    """High-performance JSONL writer with batching"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def save(self, entries: List, filename: str) -> None:
        """Save entries with batched writing for performance"""
        try:
            output_path = InputValidator.validate_output_path(filename)
            
            with open(output_path, 'w', encoding='utf-8', buffering=8192) as f:
                self._write_batched(f, entries)
            
            logger.info(f"Saved {len(entries)} entries to {filename}")
            
        except ValidationError as e:
            logger.error(f"Output validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            raise
    
    def _write_batched(self, file, entries: List) -> None:
        """Write entries in batches for better performance"""
        batch = []
        
        for entry in entries:
            # Convert to dict if needed
            if hasattr(entry, 'to_dict'):
                data = entry.to_dict()
            elif hasattr(entry, '__dict__'):
                data = entry.__dict__
            else:
                data = entry
            
            batch.append(data)
            
            # Write batch when full
            if len(batch) >= self.batch_size:
                self._flush_batch(file, batch)
                batch = []
        
        # Write remaining entries
        if batch:
            self._flush_batch(file, batch)
    
    def _flush_batch(self, file, batch: List) -> None:
        """Flush batch to file"""
        import json
        for data in batch:
            file.write(json.dumps(data, ensure_ascii=False) + '\n')