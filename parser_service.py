"""Core parser service"""
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
    """Main parser service"""
    
    def __init__(self):
        self.validator = InputValidator()
        self.writer = JSONLWriter(batch_size=200)
        self.section_filter = SectionFilter()
        self.stats = ProcessingStats()
    
    def parse_pdf(self, pdf_arg: Optional[str] = None) -> Dict[str, Any]:
        """Parse PDF with error handling"""
        start_time = time.time()
        
        try:
            pdf_file = self._resolve_pdf_path(pdf_arg)
            self.validator.validate_pdf_file(str(pdf_file))
            
            logger.info(f"Starting PDF parsing: {pdf_file}")
            
            toc_entries = self._extract_toc(pdf_file)
            if not toc_entries:
                return self._create_error_result("No TOC entries found")
            
            filtered_toc = self.section_filter.filter_numbered_sections(toc_entries)
            self.writer.save(filtered_toc, TOC_OUTPUT_FILE)
            
            content_entries = self._extract_content(pdf_file, filtered_toc)
            self.writer.save(content_entries, CONTENT_OUTPUT_FILE)
            
            self.stats.processing_time = time.time() - start_time
            return self._create_success_result(filtered_toc, content_entries)
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return self._create_error_result(f"Validation failed: {e}")
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return self._create_error_result(f"Parsing failed: {e}")
    
    def _extract_toc(self, pdf_file: Path) -> list:
        """Extract TOC from PDF"""
        try:
            with PDFParser(str(pdf_file)) as parser:
                raw_toc = parser.extract_toc()
                return parser.build_hierarchy(raw_toc) if raw_toc else []
        except Exception as e:
            logger.error(f"TOC extraction failed: {e}")
            return []
    
    def _extract_content(self, pdf_file: Path, toc_entries: list) -> list:
        """Extract content from PDF"""
        try:
            with ContentExtractor(str(pdf_file)) as extractor:
                return extractor.extract_content(toc_entries)
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return []
    
    def _resolve_pdf_path(self, pdf_arg: Optional[str]) -> Path:
        """Resolve PDF file path"""
        if not pdf_arg:
            return Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
        elif Path(pdf_arg).exists():
            return Path(pdf_arg)
        else:
            return Path(ASSETS_FOLDER) / pdf_arg
    
    def _create_success_result(
        self,
        toc_entries: list,
        content_entries: list
    ) -> Dict[str, Any]:
        """Create success result"""
        return {
            'success': True,
            'toc_count': len(toc_entries),
            'content_count': len(content_entries),
            'processing_time': self.stats.processing_time
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            'success': False,
            'error': error_message
        }


class SearchService:
    """Search service"""
    
    def __init__(self):
        self.searcher = TOCSearcher()
    
    def search_toc(self, query: str) -> Dict[str, Any]:
        """Search TOC"""
        try:
            validated_query = InputValidator.validate_search_query(query)
            matches = self.searcher.search_with_results(validated_query)
            
            return {
                'success': True,
                'matches': matches,
                'count': len(matches)
            }
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'matches': []
            }


# Service instances
_parser_service = None
_search_service = None


def get_parser_service() -> ParserService:
    """Get parser service instance"""
    global _parser_service
    if _parser_service is None:
        _parser_service = ParserService()
    return _parser_service


def get_search_service() -> SearchService:
    """Get search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service