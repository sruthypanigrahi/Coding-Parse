"""
Adapter and Facade Patterns
"""

from typing import Dict, Any
from .builders import ConcreteProcessingBuilder, ProcessingDirector
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['PyMuPDFAdapter', 'DocumentProcessingFacade']


class PyMuPDFAdapter:
    """Adapter for PyMuPDF library"""
    
    def __init__(self, document):
        self._document = document
    
    def get_page_count(self) -> int:
        """Get page count through adapter"""
        return len(self._document)
    
    def get_page_text(self, page_num: int) -> str:
        """Get page text through adapter"""
        if 0 <= page_num < len(self._document):
            return self._document[page_num].get_text()
        return ""


class DocumentProcessingFacade:
    """Simplified interface for document processing"""
    
    def __init__(self):
        self._builder = ConcreteProcessingBuilder()
        self._director = ProcessingDirector(self._builder)
    
    def process_document_simple(self, file_path: str) -> Dict[str, Any]:
        """Simple document processing"""
        return self._process_with_strategy(file_path, "simple", self._director.construct_basic_processing)
    
    def process_document_advanced(self, file_path: str) -> Dict[str, Any]:
        """Advanced document processing"""
        return self._process_with_strategy(file_path, "advanced", self._director.construct_advanced_processing)
    
    def _process_with_strategy(self, file_path: str, strategy_name: str, construction_method) -> Dict[str, Any]:
        """Common processing logic with strategy pattern"""
        try:
            logger.info(f"Starting {strategy_name} processing for: {file_path}")
            pipeline = construction_method()
            result = pipeline.execute()
            logger.info(f"{strategy_name.capitalize()} processing completed successfully")
            return result
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return {"success": False, "error": "File not found"}
        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            return {"success": False, "error": "Permission denied"}
        except Exception as e:
            logger.error(f"{strategy_name.capitalize()} processing failed: {type(e).__name__}: {e}")
            return {"success": False, "error": f"{strategy_name.capitalize()} processing failed"}