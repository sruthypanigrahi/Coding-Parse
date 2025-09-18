"""Clean components with SOLID principles"""
import fitz
import re
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

from interfaces import Processable, Parseable, Extractable, Filterable
from models import TOCEntry, ContentEntry, ImageInfo, TableInfo
from constants import DOC_TITLE, CONTENT_LIMIT, MAX_WORKERS, PARALLEL_THRESHOLD
from logger_config import setup_logger

logger = setup_logger(__name__)


class PDFProcessor(Processable):
    """PDF processor with context management"""
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._doc = None
    
    def __enter__(self):
        self._doc = fitz.open(self.file_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._doc:
            self._doc.close()


class TOCParser(Parseable):
    """TOC parser implementing Parseable"""
    def __init__(self, processor: PDFProcessor):
        self.processor = processor
    
    def parse(self) -> List[TOCEntry]:
        toc = self.processor._doc.get_toc()
        entries = [self._create_entry(level, title, page) for level, title, page in toc]
        return self._build_hierarchy(entries)
    
    def _create_entry(self, level: int, title: str, page: int) -> TOCEntry:
        match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title.strip())
        section_id = match.group(1) if match else ""
        section_title = match.group(2) if match else title.strip()
        return TOCEntry(
            doc_title="USB Power Delivery Specification",
            section_id=section_id, 
            title=section_title, 
            page=page, 
            level=level
        )
    
    def _build_hierarchy(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        result, parent_stack = [], []
        for entry in entries:
            if not entry.section_id:
                continue
            depth = len(entry.section_id.split('.'))
            parent_stack = parent_stack[:depth-1]
            entry.parent_id = parent_stack[-1] if parent_stack else None
            result.append(entry)
            parent_stack.append(entry.section_id)
        return result


class ContentExtractor(Extractable):
    """Content extractor with parallel processing"""
    def __init__(self, processor: PDFProcessor):
        self.processor = processor
    
    def extract(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        if len(entries) > PARALLEL_THRESHOLD:
            return self._extract_parallel(entries)
        return [self._extract_single(entry, entries, i) for i, entry in enumerate(entries)]
    
    def _extract_parallel(self, entries: List[TOCEntry]) -> List[ContentEntry]:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(self._extract_single, entry, entries, i) 
                      for i, entry in enumerate(entries)]
            return [f.result() for f in futures if f.result()]
    
    def _extract_single(self, entry: TOCEntry, all_entries: List[TOCEntry], index: int) -> ContentEntry:
        start, end = self._get_page_range(entry, all_entries, index)
        return ContentEntry(
            doc_title=DOC_TITLE, section_id=entry.section_id, title=entry.title,
            page_range=f"{start}-{end}", 
            content=self._extract_text(start, end)[:CONTENT_LIMIT],
            images=self._extract_images(start, end),
            tables=self._extract_tables(start, end)
        )
    
    def _get_page_range(self, entry: TOCEntry, all_entries: List[TOCEntry], index: int) -> Tuple[int, int]:
        start = max(1, entry.page)
        end = (all_entries[index + 1].page - 1 if index + 1 < len(all_entries) 
               else len(self.processor._doc))
        return start, end
    
    def _extract_text(self, start: int, end: int) -> str:
        content = []
        for page_num in range(start - 1, end):
            try:
                text = self.processor._doc[page_num].get_text("text").strip()
                if text:
                    content.append(text)
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {e}")
        return '\n'.join(content)
    
    def _extract_images(self, start: int, end: int) -> List[ImageInfo]:
        images = []
        for page_num in range(start - 1, end):
            try:
                page_images = self._extract_page_images(page_num)
                images.extend(page_images)
            except Exception as e:
                logger.warning(f"Failed to extract images from page {page_num}: {e}")
        return images
    
    def _extract_page_images(self, page_num: int) -> List[ImageInfo]:
        page = self.processor._doc[page_num]
        images = []
        for idx, img in enumerate(page.get_images(full=True)):
            colorspace = img[4] if len(img) > 4 else "Unknown"
            images.append(ImageInfo(
                page=page_num + 1, index=idx + 1, xref=img[0],
                width=img[2], height=img[3], colorspace=colorspace
            ))
        return images
    
    def _extract_tables(self, start: int, end: int) -> List[TableInfo]:
        tables = []
        for page_num in range(start - 1, end):
            try:
                page_tables = self._extract_page_tables(page_num)
                tables.extend(page_tables)
            except Exception as e:
                logger.warning(f"Failed to extract tables from page {page_num}: {e}")
        return tables
    
    def _extract_page_tables(self, page_num: int) -> List[TableInfo]:
        page = self.processor._doc[page_num]
        tables = []
        for idx, table in enumerate(page.find_tables()):
            data = table.extract()
            if data:
                tables.append(TableInfo(
                    page=page_num + 1, index=idx + 1,
                    rows=len(data), 
                    cols=len(data[0]) if data else 0,
                    data=data[:10]
                ))
        return tables


class NumericFilter(Filterable):
    """Numeric section filter"""
    def __init__(self):
        self.pattern = re.compile(r'^\d+(?:\.\d+)*$')
    
    def apply(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        filtered = [e for e in entries if e.section_id and self.pattern.match(e.section_id)]
        logger.info(f"Filtered {len(entries)} to {len(filtered)} sections")
        return filtered