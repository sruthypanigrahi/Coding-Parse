"""
Parser Service - Main Orchestration Layer
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from interfaces import Executable
from models import TOCEntry, ContentEntry
from constants import ASSETS_FOLDER, DEFAULT_PDF_FILE, TOTAL_EXPECTED_PAGES
from validators import ValidationError
from utils.decorators import timer
from logger_config import setup_logger
from patterns import Subject, ProgressObserver
from factories import ApplicationContext
from .document_processor import DocumentProcessor
from .export_manager import ExportManager

logger = setup_logger(__name__)

__all__ = ['ParserService']


class ParserService(Executable, Subject):
    """Parser service with advanced OOP patterns and perfect encapsulation"""
    
    def __init__(self, context: Optional[ApplicationContext] = None):
        """Initialize with dependency injection and observer pattern"""
        Subject.__init__(self)
        
        # Encapsulated dependencies with proper initialization
        self._context = context or ApplicationContext()
        self._validator = self._context.get_validator()
        self._document_processor = DocumentProcessor(self._context.get_processor_factory())
        self._export_manager = ExportManager(self._context.get_service_factory())
        
        # Attach progress observer for monitoring
        self.attach(ProgressObserver())
    
    @timer
    def execute(self, pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """Execute parsing workflow with comprehensive error handling and notifications"""
        try:
            self.notify("parsing_started", {"file": pdf_path})
            
            # Step 1: Validate input path
            self.notify("validation_started", {})
            file_path = self._resolve_and_validate_path(pdf_path)
            self.notify("validation_completed", {"path": str(file_path)})
            
            # Step 2: Parse document
            self.notify("parsing_document", {})
            parsing_result = self._document_processor.parse_document(file_path)
            if not parsing_result['success']:
                self.notify("parsing_failed", parsing_result)
                return parsing_result
            
            # Step 3: Export results
            self.notify("exporting_results", {})
            export_result = self._export_manager.export_all_results(
                parsing_result['toc_entries'], 
                parsing_result['content_entries']
            )
            
            if not export_result['success']:
                self.notify("export_failed", export_result)
                return export_result
            
            # Step 4: Create success response
            result = self._create_success_response(
                parsing_result['toc_entries'],
                parsing_result['content_entries']
            )
            self.notify("parsing_completed", result)
            return result
            
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            return {'success': False, 'error': "Invalid input provided"}
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return {'success': False, 'error': "Requested file not accessible"}
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return {'success': False, 'error': "Access denied"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {'success': False, 'error': "Processing failed due to unexpected error"}
    
    def _resolve_and_validate_path(self, pdf_path: Optional[str]) -> Path:
        """Resolve and validate PDF path with comprehensive security checks"""
        if not pdf_path:
            default_path = Path(ASSETS_FOLDER) / DEFAULT_PDF_FILE
            return self._validator.validate_pdf_file(str(default_path))
        
        # Comprehensive security validation
        if any(dangerous in pdf_path for dangerous in ['..',  '/', '\\', '~']):
            raise ValidationError("Path contains dangerous characters")
        
        if Path(pdf_path).is_absolute():
            raise ValidationError("Absolute paths not allowed")
        
        # Resolve path safely within assets folder
        assets_path = Path(ASSETS_FOLDER) / pdf_path
        resolved_path = assets_path.resolve()
        assets_resolved = Path(ASSETS_FOLDER).resolve()
        
        # Ensure resolved path is within assets directory
        try:
            resolved_path.relative_to(assets_resolved)
        except ValueError:
            raise ValidationError("Path traversal attempt detected")
        
        return self._validator.validate_pdf_file(str(resolved_path))
    
    def _create_success_response(self, toc_entries: List[TOCEntry], content_entries: List[ContentEntry]) -> Dict[str, Any]:
        """Create comprehensive success response with metrics"""
        unique_pages = len(set(entry.page for entry in toc_entries if entry.page > 0))
        coverage = round((unique_pages / TOTAL_EXPECTED_PAGES) * 100, 2) if TOTAL_EXPECTED_PAGES > 0 else 0.0
        
        return {
            'success': True,
            'toc_count': len(toc_entries),
            'content_count': len(content_entries),
            'coverage': coverage,
            'message': f'Successfully processed {len(toc_entries)} sections'
        }