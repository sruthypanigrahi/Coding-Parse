"""Advanced parser service with dependency injection and error recovery"""
from pathlib import Path
from typing import Optional, Dict, Any
import time

from pdf_parser import PDFParser, JSONLWriter
from content_extractor import ContentExtractor
from filter import SectionFilter
from search import TOCSearcher
from constants import ASSETS_FOLDER, DEFAULT_PDF_FILE, TOC_OUTPUT_FILE, CONTENT_OUTPUT_FILE
from logger_config import setup_logger
from validators import InputValidator, ValidationError
from models import ProcessingStats

logger = setup_logger(__name__)


class ParserService:
    """High-level parser service with dependency injection"""
    
    def __init__(self, 
                 validator: Optional[InputValidator] = None,
                 writer: Optional[JSONLWriter] = None,
                 section_filter: Optional[SectionFilter] = None):
        self.validator = validator or InputValidator()
        self.writer = writer or JSONLWriter(batch_size=200)
        self.section_filter = section_filter or SectionFilter(use_composite=True)
        self.stats = ProcessingStats()
    
    def parse_pdf(self, pdf_arg: Optional[str] = None) -> Dict[str, Any]:
        """Parse PDF with comprehensive error handling and statistics"""
        start_time = time.time()
        
        try:
            # Resolve and validate PDF path
            pdf_file = self._resolve_pdf_path(pdf_arg)
            self.validator.validate_pdf_file(str(pdf_file))
            
            logger.info(f"Starting PDF parsing: {pdf_file}")
            
            # Extract TOC with error recovery
            toc_entries = self._extract_toc_with_recovery(pdf_file)
            if not toc_entries:
                return self._create_error_result("No TOC entries found")
            
            # Filter and save TOC
            filtered_toc = self.section_filter.filter_numbered_sections(toc_entries)
            self.writer.save(filtered_toc, TOC_OUTPUT_FILE)
            
            logger.info(f"TOC saved: {len(filtered_toc)} sections")
            
            # Extract and save content
            content_entries = self._extract_content_with_recovery(pdf_file, filtered_toc)
            self.writer.save(content_entries, CONTENT_OUTPUT_FILE)
            
            logger.info(f"Content saved: {len(content_entries)} entries")
            
            # Update statistics
            self.stats.processing_time = time.time() - start_time
            self.stats.total_sections = len(filtered_toc)
            self.stats.processed_sections = len(content_entries)
            
            return self._create_success_result(filtered_toc, content_entries)
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return self._create_error_result(f"Validation failed: {e}")
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return self._create_error_result(f"Parsing failed: {e}")
    
    def _extract_toc_with_recovery(self, pdf_file: Path) -> list:
        """Extract TOC with error recovery mechanisms"""
        try:
            with PDFParser(str(pdf_file)) as parser:
                raw_toc = parser.extract_toc()
                if not raw_toc:
                    logger.warning("No TOC found, attempting alternative extraction")
                    return []
                
                structured_toc = parser.build_hierarchy(raw_toc)
                
                # Store parser stats
                parser_stats = parser.get_stats()
                self.stats.errors.extend(parser_stats.errors)
                
                return structured_toc
                
        except Exception as e:
            logger.error(f"TOC extraction failed: {e}")
            self.stats.add_error(f"TOC extraction: {e}")
            return []
    
    def _extract_content_with_recovery(self, pdf_file: Path, toc_entries: list) -> list:
        """Extract content with error recovery and fallback strategies"""
        try:
            with ContentExtractor(str(pdf_file), max_workers=2) as extractor:
                content_entries = extractor.extract_content(toc_entries)
                
                # Store extractor stats
                extractor_stats = extractor.get_stats()
                self.stats.total_images = extractor_stats.total_images
                self.stats.total_tables = extractor_stats.total_tables
                self.stats.errors.extend(extractor_stats.errors)
                
                return content_entries
                
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            self.stats.add_error(f"Content extraction: {e}")
            
            # Fallback: create minimal content entries
            return self._create_fallback_content(toc_entries)
    
    def _create_fallback_content(self, toc_entries: list) -> list:
        """Create minimal content entries as fallback"""
        from models import ContentEntry
        
        fallback_entries = []
        for entry in toc_entries:
            content_entry = ContentEntry(
                doc_title="USB Power Delivery Specification",
                section_id=entry.section_id,
                title=entry.title,
                page_range=f"{entry.page}-{entry.page}",
                content=f"[Fallback] Section {entry.section_id}: {entry.title}",
                has_content=False,
                metadata={'fallback': True}
            )
            fallback_entries.append(content_entry)
        
        logger.warning(f"Created {len(fallback_entries)} fallback content entries")
        return fallback_entries
    
    def _resolve_pdf_path(self, pdf_arg: Optional[str]) -> Path:
        """Resolve PDF file path with validation"""
        if not pdf_arg:
            return Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
        elif Path(pdf_arg).exists():
            return Path(pdf_arg)
        else:
            return Path(ASSETS_FOLDER) / pdf_arg
    
    def _create_success_result(self, toc_entries: list, content_entries: list) -> Dict[str, Any]:
        """Create success result dictionary"""
        return {
            'success': True,
            'toc_file': TOC_OUTPUT_FILE,
            'content_file': CONTENT_OUTPUT_FILE,
            'toc_count': len(toc_entries),
            'content_count': len(content_entries),
            'processing_time': self.stats.processing_time,
            'statistics': self.stats.to_dict(),
            'message': f"Successfully processed {len(toc_entries)} sections"
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result dictionary"""
        return {
            'success': False,
            'error': error_message,
            'statistics': self.stats.to_dict(),
            'processing_time': self.stats.processing_time
        }
    
    def get_statistics(self) -> ProcessingStats:
        """Get comprehensive processing statistics"""
        return self.stats


class SearchService:
    """Advanced search service with caching and optimization"""
    
    def __init__(self, searcher: Optional[TOCSearcher] = None):
        self.searcher = searcher or TOCSearcher()
    
    def search_toc(self, query: str) -> Dict[str, Any]:
        """Search TOC with comprehensive result formatting"""
        try:
            validated_query = InputValidator.validate_search_query(query)
            
            # Perform search
            matches = self.searcher.search_with_results(validated_query)
            
            return {
                'success': True,
                'query': validated_query,
                'matches': matches,
                'count': len(matches),
                'message': f"Found {len(matches)} matches for '{validated_query}'"
            }
            
        except ValidationError as e:
            logger.error(f"Search validation error: {e}")
            return {
                'success': False,
                'error': f"Invalid search query: {e}",
                'matches': [],
                'count': 0
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                'success': False,
                'error': f"Search failed: {e}",
                'matches': [],
                'count': 0
            }


# Service instances (Singleton pattern)
_parser_service = None
_search_service = None


def get_parser_service() -> ParserService:
    """Get parser service instance (Singleton)"""
    global _parser_service
    if _parser_service is None:
        _parser_service = ParserService()
    return _parser_service


def get_search_service() -> SearchService:
    """Get search service instance (Singleton)"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


# Convenience functions for backward compatibility
def parse_pdf(pdf_arg: Optional[str] = None) -> Dict[str, Any]:
    """Parse PDF using service layer"""
    return get_parser_service().parse_pdf(pdf_arg)


def search_toc(query: str) -> Dict[str, Any]:
    """Search TOC using service layer"""
    return get_search_service().search_toc(query)