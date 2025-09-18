"""Services with clean architecture"""
from pathlib import Path
from typing import Optional, Dict, Any
import time
import json

from interfaces import Executable
from components import PDFProcessor, TOCParser, ContentExtractor, NumericFilter
from search import TOCSearcher
from constants import ASSETS_FOLDER, DEFAULT_PDF_FILE, TOC_OUTPUT_FILE, CONTENT_OUTPUT_FILE
from validators import InputValidator, ValidationError
from logger_config import setup_logger

logger = setup_logger(__name__)


class ParserService(Executable):
    """Parser service implementing Executable"""
    def __init__(self):
        self.validator = InputValidator()
        self.filter = NumericFilter()
    
    def execute(self, pdf_path: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            file_path = self._resolve_path(pdf_path)
            self.validator.validate_pdf_file(str(file_path))
            
            with PDFProcessor(str(file_path)) as processor:
                toc_entries = TOCParser(processor).parse()
                if not toc_entries:
                    return {'success': False, 'error': 'No TOC entries'}
                
                filtered_toc = self.filter.apply(toc_entries)
                self._save_json(filtered_toc, TOC_OUTPUT_FILE)
                
                content_entries = ContentExtractor(processor).extract(filtered_toc)
                self._save_json(content_entries, CONTENT_OUTPUT_FILE)
                
                # Generate validation reports
                self._generate_validation_reports()
                
                return {
                    'success': True,
                    'toc_count': len(filtered_toc),
                    'content_count': len(content_entries),
                    'processing_time': time.time() - start_time
                }
        except Exception as e:
            logger.error(f"Parse failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _resolve_path(self, pdf_path: Optional[str]) -> Path:
        if not pdf_path:
            return Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
        return Path(pdf_path) if Path(pdf_path).exists() else Path(ASSETS_FOLDER) / pdf_path
    
    def _save_json(self, entries: list, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in entries:
                data = entry.to_dict() if hasattr(entry, 'to_dict') else entry
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def _generate_validation_reports(self):
        """Generate validation reports"""
        try:
            from validator import generate_validation_reports
            generate_validation_reports()
            logger.info("Generated validation reports")
        except Exception as e:
            logger.warning(f"Failed to generate validation reports: {e}")


class SearchService(Executable):
    """Search service with clean interface"""
    def __init__(self):
        self.searcher = TOCSearcher()
    
    def execute(self, query: str) -> Dict[str, Any]:
        try:
            validated_query = InputValidator.validate_search_query(query)
            matches = self.searcher.search(validated_query)
            return {'success': True, 'matches': matches, 'count': len(matches)}
        except ValidationError as e:
            return {'success': False, 'error': str(e), 'matches': []}


# Service factory
class ServiceFactory:
    @staticmethod
    def create_parser_service() -> ParserService:
        return ParserService()
    
    @staticmethod
    def create_search_service() -> SearchService:
        return SearchService()


# Service instances
_parser_service = None
_search_service = None


def get_parser_service() -> ParserService:
    global _parser_service
    if _parser_service is None:
        _parser_service = ServiceFactory.create_parser_service()
    return _parser_service


def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = ServiceFactory.create_search_service()
    return _search_service