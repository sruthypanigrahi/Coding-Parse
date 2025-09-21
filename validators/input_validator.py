"""
Main Input Validator
"""

from pathlib import Path
from .pdf_validator import PDFValidator
from .query_validator import QueryValidator
from .path_validator import PathValidator

__all__ = ['InputValidator']


class InputValidator:
    """Perfect input validator with comprehensive security checks"""
    
    def __init__(self):
        self._pdf_validator = PDFValidator()
        self._query_validator = QueryValidator()
        self._path_validator = PathValidator()
    
    def validate_pdf_file(self, pdf_path: str) -> Path:
        """Validate PDF file"""
        return self._pdf_validator.validate_pdf_file(pdf_path)
    
    def validate_search_query(self, query: str) -> str:
        """Validate search query"""
        return self._query_validator.validate_search_query(query)
    
    def validate_output_path(self, output_path: str) -> Path:
        """Validate output path"""
        return self._path_validator.validate_output_path(output_path)
    
    def validate_page_number(self, page: int, max_pages: int) -> int:
        """Validate page number using PDF validator for semantic correctness"""
        return self._pdf_validator.validate_page_number(page, max_pages)