"""High-performance content extractor with advanced optimization"""
import fitz
from pathlib import Path
from typing import List, Iterator, Optional, Tuple
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from models import (
    TOCEntry, ContentEntry, ImageInfo, TableInfo, ProcessingStats
)

from constants import DOC_TITLE, PROGRESS_INTERVAL, CONTENT_LIMIT
from logger_config import setup_logger


logger = setup_logger(__name__)


class ContentExtractor:
    """High-performance content extractor with parallel processing"""
    
    def __init__(self, pdf_path: str, max_workers: int = 4):
        self.pdf_path = Path(pdf_path)
        self.doc_title = DOC_TITLE
        self.max_workers = max_workers
        self._doc: Optional[fitz.Document] = None
        self.stats = ProcessingStats()
        self._lock = threading.Lock()
    
    def __enter__(self):
        """Context manager entry"""
        try:
            self._doc = fitz.open(self.pdf_path)
            self.stats.total_pages = len(self._doc)
            logger.info(
                f"Opened PDF for content extraction: "
                f"{self.stats.total_pages} pages"
            )
            return self
        except Exception as e:
            logger.error(f"Failed to open PDF for content extraction: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._doc:
            self._doc.close()
            self._doc = None
    

    
    def extract_content(
        self, toc_entries: List[TOCEntry]
    ) -> List[ContentEntry]:
        """Extract content with parallel processing for performance"""
        if not self._doc:
            raise RuntimeError("PDF not opened")
        
        start_time = time.time()
        logger.info(
            f"Starting content extraction for {len(toc_entries)} sections"
        )
        
        # Use parallel processing for large documents
        if len(toc_entries) > 50:
            content_entries = self._extract_parallel(toc_entries)
        else:
            content_entries = self._extract_sequential(toc_entries)
        
        self.stats.processing_time = time.time() - start_time
        self.stats.total_sections = len(toc_entries)
        self.stats.processed_sections = len(
            [e for e in content_entries if e.has_content]
        )
        
        self._log_stats()
        return content_entries
    
    def _extract_parallel(
        self, toc_entries: List[TOCEntry]
    ) -> List[ContentEntry]:
        """Extract content using parallel processing"""
        content_entries = [None] * len(toc_entries)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            future_to_index = {
                executor.submit(
                    self._extract_section_safe, entry, toc_entries, i
                ): i
                for i, entry in enumerate(toc_entries)
            }
            
            # Collect results
            completed = 0
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    content_entries[index] = future.result()
                    completed += 1
                    
                    if completed % PROGRESS_INTERVAL == 0:
                        logger.info(
                            f"Processed {completed}/{len(toc_entries)} sections"
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to process section {index}: {e}")
                    self.stats.add_error(f"Section {index}: {e}")
        
        return [entry for entry in content_entries if entry is not None]
    
    def _extract_sequential(
        self, toc_entries: List[TOCEntry]
    ) -> List[ContentEntry]:
        """Extract content sequentially for smaller documents"""
        content_entries = []
        
        for i, entry in enumerate(toc_entries):
            try:
                content_entry = self._extract_section_content(
                    entry, toc_entries, i
                )
                content_entries.append(content_entry)
                
                if (i + 1) % PROGRESS_INTERVAL == 0:
                    logger.info(
                        f"Processed {i + 1}/{len(toc_entries)} sections"
                    )
                    
            except Exception as e:
                logger.error(
                    f"Failed to process section {entry.section_id}: {e}"
                )
                self.stats.add_error(f"Section {entry.section_id}: {e}")
                continue
        
        return content_entries
    
    def _extract_section_safe(
        self, 
        section: TOCEntry, 
        all_sections: List[TOCEntry], 
        index: int
    ) -> Optional[ContentEntry]:
        """Thread-safe section extraction wrapper"""
        try:
            return self._extract_section_content(section, all_sections, index)
        except Exception as e:
            logger.error(
                f"Thread-safe extraction failed for {section.section_id}: {e}"
            )
            return None
    
    def _extract_section_content(
        self, 
        section: TOCEntry, 
        all_sections: List[TOCEntry], 
        index: int
    ) -> ContentEntry:
        """Extract content for a single section with optimization"""
        page_range = self._calculate_page_range(section, all_sections, index)
        
        # Extract content components
        text_content = self._extract_text_optimized(page_range)
        images = self._extract_images_batch(page_range)
        tables = self._extract_tables_batch(page_range)
        
        # Update statistics thread-safely
        with self._lock:
            self.stats.total_images += len(images)
            self.stats.total_tables += len(tables)
        
        # Build content entry
        content_entry = ContentEntry(
            doc_title=self.doc_title,
            section_id=section.section_id,
            title=section.title,
            page_range=f"{page_range[0]}-{page_range[1]}",
            content=text_content[:CONTENT_LIMIT] if text_content else 
                   f"[Section {section.section_id} - No extractable content]",
            images=images,
            tables=tables,
            metadata={
                'extraction_time': time.time(),
                'page_count': page_range[1] - page_range[0] + 1
            }
        )
        
        return content_entry
    
    def _calculate_page_range(self, section: TOCEntry,
        all_sections: List[TOCEntry],
                            index: int) -> Tuple[int, int]:
        """Calculate optimal page range for section"""
        start_page = max(1, section.page)
        
        if index + 1 < len(all_sections):
            end_page = (
                min(all_sections[index + 1].page - 1, self.stats.total_pages)
            )
        else:
            end_page = self.stats.total_pages
        
        return start_page, end_page
    

    def _extract_text_optimized(self, page_range: Tuple[int, int]) -> str:
        """Extract text with caching and optimization"""
        content_parts = []
        
        for page_num in range(
            page_range[0] - 1,
            min(page_range[1],
            self.stats.total_pages)
        ):
            try:
                page = self._doc[page_num]
                
                # Use optimized text extraction
                text = (
                    page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                )
                if text and text.strip():
                    content_parts.append(text.strip())
                
            except (
                fitz.FileDataError,
                fitz.EmptyFileError,
                AttributeError
            ) as e:
                logger.warning(
                    f"Text extraction failed for page {page_num + 1}: {e}"
                )
                self.stats.add_error(f"Page {page_num + 1} text: {e}")
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error extracting text from page {page_num + 1}: {e}"
                )
                self.stats.add_error(f"Page {page_num + 1} unexpected: {e}")
                continue
        
        return "\n".join(content_parts)
    
    def _extract_images_batch(
        self,
        page_range: Tuple[int,
        int]
    ) -> List[ImageInfo]:
        """Extract images in batch for performance"""
        images = []
        
        for page_num in range(
            page_range[0] - 1,
            min(page_range[1],
            self.stats.total_pages)
        ):
            try:
                page = self._doc[page_num]
                image_list = page.get_images(full=True)
                
                for idx, img in enumerate(image_list):
                    try:
                        # Extract detailed image info
                        image_info = ImageInfo(
                            page=page_num + 1,
                            index=idx + 1,
                            xref=img[0],
                            width=img[2],
                            height=img[3],
                            colorspace=img[4] if len(img) > 4 else "Unknown",
                            size_bytes=img[6] if len(img) > 6 else None,
                            format=img[8] if len(img) > 8 else None
                        )
                        images.append(image_info)
                        
                    except (IndexError, KeyError, ValueError) as e:
                        logger.debug(f"Image info extraction failed: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"Unexpected image error: {e}")
                        continue
                        
            except (fitz.FileDataError, AttributeError) as e:
                logger.debug(
                    f"Image extraction failed for page {page_num + 1}: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error in image extraction page {page_num + 1}: {e}"
                )
                continue
        
        return images
    
    def _extract_tables_batch(
        self,
        page_range: Tuple[int,
        int]
    ) -> List[TableInfo]:
        """Extract tables in batch with optimization"""
        tables = []
        
        for page_num in range(
            page_range[0] - 1,
            min(page_range[1],
            self.stats.total_pages)
        ):
            page_tables = self._extract_page_tables(page_num)
            tables.extend(page_tables)
        
        return tables
    
    def _extract_page_tables(self, page_num: int) -> List[TableInfo]:
        """Extract tables from a single page"""
        try:
            page = self._doc[page_num]
            return self._try_structured_extraction(
                page,
                page_num) or self._try_fallback_extraction(page,
                page_num
            )
        except (fitz.FileDataError, AttributeError) as e:
            logger.debug(
                f"Table extraction failed for page {page_num + 1}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error extracting tables from page {page_num + 1}: {e}"
            )
            return []
    
    def _try_structured_extraction(
        self,
        page,
        page_num: int
    ) -> List[TableInfo]:
        """Try structured table extraction"""
        try:
            table_list = page.find_tables()
            tables = []
            
            for idx, table in enumerate(table_list):
                table_info = self._extract_table_data(table, page_num, idx)
                if table_info:
                    tables.append(table_info)
            
            return tables
        except Exception:
            return []
    
    def _extract_table_data(
        self,
        table,
        page_num: int,
        idx: int
    ) -> Optional[TableInfo]:
        """Extract data from a single table"""
        try:
            data = table.extract()
            if data:
                return TableInfo(
                    page=page_num + 1,
                    index=idx + 1,
                    rows=len(data),
                    cols=len(data[0]) if data else 0,
                    data=data[:10]  # Limit data for performance
                )
        except (IndexError, ValueError) as e:
            logger.debug(f"Table data extraction failed: {e}")
        return None
    
    def _try_fallback_extraction(self, page, page_num: int) -> List[TableInfo]:
        """Fallback to text-based table detection"""
        try:
            text = page.get_text()
            table_count = text.count('Table ') + text.count('TABLE ')
            
            if table_count > 0:
                return [TableInfo(
                    page=page_num + 1,
                    index=1,
                    rows=0,
                    cols=0,
                    data=[],
                    metadata={'detected_mentions': table_count}
                )]
        except Exception as e:
            logger.debug(f"Fallback table detection failed: {e}")
        
        return []
    
    def _log_stats(self) -> None:
        """Log comprehensive extraction statistics"""
        logger.info("Content extraction completed")
        logger.info(f"Processing time: {self.stats.processing_time:.2f}s")
        logger.info(f"Success rate: {self.stats.get_success_rate():.1f}%")
        logger.info(f"Total images: {self.stats.total_images}")
        logger.info(f"Total tables: {self.stats.total_tables}")
        
        if self.stats.errors:
            logger.warning(
                f"Encountered {len(self.stats.errors)} errors during extraction"
            )
    
    def get_stats(self) -> ProcessingStats:
        """Get processing statistics"""
        return self.stats