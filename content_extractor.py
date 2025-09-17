"""Content extraction with performance optimizations"""
import fitz
from pathlib import Path
from typing import List, Tuple, Generator
from models import TOCEntry, ContentEntry, ImageInfo, TableInfo
from constants import DOC_TITLE, PROGRESS_INTERVAL, CONTENT_LIMIT


class ContentExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc_title = DOC_TITLE
        self._doc = None
        self.stats = {'images': 0, 'tables': 0}
    
    def __enter__(self):
        self._doc = fitz.open(self.pdf_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._doc:
            self._doc.close()
    
    def extract_content(self, toc_entries: List[TOCEntry]) -> List[ContentEntry]:
        """Extract content for all sections"""
        if not self._doc:
            raise RuntimeError("PDF not opened. Use context manager.")
        
        print(f"Extracting content from {len(toc_entries)} sections...")
        
        content_entries = []
        for i, entry in enumerate(toc_entries):
            content_entry = self._extract_section_content(entry, toc_entries, i)
            content_entries.append(content_entry)
            
            if (i + 1) % PROGRESS_INTERVAL == 0:
                print(f"Processed {i + 1}/{len(toc_entries)} sections")
        
        self._print_stats()
        return content_entries
    
    def _extract_section_content(self, section: TOCEntry, all_sections: List[TOCEntry], 
                                index: int) -> ContentEntry:
        """Extract content for a single section"""
        page_range = self._calculate_page_range(section, all_sections, index)
        content = self._extract_text_from_pages(page_range)
        
        return ContentEntry(
            doc_title=self.doc_title,
            section_id=section.section_id,
            title=section.title,
            page_range=f"{page_range[0]}-{page_range[1]}",
            content=content[:CONTENT_LIMIT] if content else 
                   f"[Section {section.section_id} - No extractable content]",
            has_content=bool(content)
        )
    
    def _calculate_page_range(self, section: TOCEntry, all_sections: List[TOCEntry], 
                            index: int) -> Tuple[int, int]:
        """Calculate page range for section"""
        start_page = section.page
        
        if index + 1 < len(all_sections):
            end_page = all_sections[index + 1].page
        else:
            end_page = len(self._doc) + 1
        
        return start_page, end_page
    
    def _extract_text_from_pages(self, page_range: Tuple[int, int]) -> str:
        """Extract text from page range with media detection"""
        content_parts = []
        
        for page_num in range(page_range[0] - 1, min(page_range[1] - 1, len(self._doc))):
            try:
                page = self._doc[page_num]
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    content_parts.append(text.strip())
                
                # Extract images
                images = self._extract_images(page, page_num + 1)
                if images:
                    content_parts.append(self._format_images(images))
                
                # Extract tables
                tables = self._extract_tables(page, page_num + 1)
                if tables:
                    content_parts.append(self._format_tables(tables))
            
            except Exception:
                continue
        
        return "\n".join(content_parts)
    
    def _extract_images(self, page, page_num: int) -> List[ImageInfo]:
        """Extract image information from page"""
        images = []
        try:
            image_list = page.get_images()
            for idx, img in enumerate(image_list):
                images.append(ImageInfo(
                    page=page_num,
                    index=idx + 1,
                    xref=img[0],
                    width=img[2],
                    height=img[3],
                    colorspace=img[4] if len(img) > 4 else "Unknown"
                ))
            self.stats['images'] += len(images)
        except Exception:
            pass
        return images
    
    def _extract_tables(self, page, page_num: int) -> List[TableInfo]:
        """Extract table information from page"""
        tables = []
        try:
            table_list = page.find_tables()
            for idx, table in enumerate(table_list):
                try:
                    data = table.extract()
                    tables.append(TableInfo(
                        page=page_num,
                        index=idx + 1,
                        rows=len(data),
                        cols=len(data[0]) if data else 0,
                        data=data[:5]  # Limit to first 5 rows
                    ))
                except Exception:
                    continue
            self.stats['tables'] += len(tables)
        except Exception:
            pass
        return tables
    
    def _format_images(self, images: List[ImageInfo]) -> str:
        """Format image information for output"""
        if not images:
            return ""
        
        lines = [f"=== IMAGES ON PAGE {images[0].page} ==="]
        for img in images:
            lines.append(f"Image {img.index}: xref={img.xref}, "
                        f"size={img.width}x{img.height}, colorspace={img.colorspace}")
        lines.append("=== END IMAGES ===")
        return "\n".join(lines)
    
    def _format_tables(self, tables: List[TableInfo]) -> str:
        """Format table information for output"""
        if not tables:
            return ""
        
        lines = [f"=== TABLES ON PAGE {tables[0].page} ==="]
        for table in tables:
            lines.append(f"Table {table.index} ({table.rows} rows x {table.cols} cols):")
            for row_idx, row in enumerate(table.data):
                clean_row = [str(cell).strip() if cell else '' for cell in row]
                lines.append(f"  Row {row_idx + 1}: {' | '.join(clean_row)}")
            if table.rows > 5:
                lines.append(f"  ... and {table.rows - 5} more rows")
        lines.append("=== END TABLES ===")
        return "\n".join(lines)
    
    def _print_stats(self) -> None:
        """Print extraction statistics"""
        print(f"\nExtraction complete:")
        print(f"Total Images: {self.stats['images']}")
        print(f"Total Tables: {self.stats['tables']}")