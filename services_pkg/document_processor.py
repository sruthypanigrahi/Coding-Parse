"""
Document Processing Logic
"""

from pathlib import Path
from typing import Dict, Any, List
from components import PDFProcessor, TOCParser, ContentExtractor, NumericFilter
from models import TOCEntry, ContentEntry
from validators import ValidationError
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['DocumentProcessor']


class DocumentProcessor:
    """Handles core document processing logic"""
    
    def __init__(self, factory):
        """Initialize with processor factory for dependency injection"""
        self._factory = factory
    
    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        """Parse document using factory pattern with comprehensive error handling"""
        try:
            # Validate file path for security
            from validators.security import SecurityValidator
            if not SecurityValidator.validate_file_path(str(file_path)):
                raise ValueError(f"Security violation: Invalid file path {file_path}")
            
            with self._factory.create_pdf_processor(str(file_path)) as processor:
                # Parse table of contents
                toc_parser = self._factory.create_toc_parser(processor)
                toc_entries = toc_parser.parse()
                
                if not toc_entries:
                    return {'success': False, 'error': 'No TOC entries found'}
                
                # Apply filtering to remove invalid entries
                filter_obj = self._factory.create_filter()
                filtered_toc = filter_obj.apply(toc_entries)
                if not filtered_toc:
                    return {'success': False, 'error': 'No valid entries after filtering'}
                
                # Extract content from filtered TOC entries
                content_extractor = self._factory.create_content_extractor(processor)
                content_entries = content_extractor.extract(filtered_toc)
                
                return {
                    'success': True,
                    'toc_entries': filtered_toc,
                    'content_entries': content_entries
                }
                
        except ValidationError as e:
            logger.warning(f"Document validation failed: {e}")
            return {'success': False, 'error': 'Invalid document format'}
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"File access error: {e}")
            return {'success': False, 'error': 'Document access failed'}
        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            return {'success': False, 'error': 'Document processing failed'}