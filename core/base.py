"""
Core Base Classes and Enums
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum
from models import TOCEntry, ContentEntry
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessingState', 'DocumentProcessor']


class ProcessingState(Enum):
    """State enumeration for State Pattern"""
    IDLE = "idle"
    VALIDATING = "validating"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentProcessor(ABC):
    """Abstract base class for document processing - Template Method Pattern"""
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        pass
    
    @abstractmethod
    def parse_structure(self, input_data: Any) -> List[TOCEntry]:
        """Parse document structure"""
        pass
    
    @abstractmethod
    def extract_content(self, structure: List[TOCEntry]) -> List[ContentEntry]:
        """Extract content from structure.
        
        Args:
            structure: List of TOC entries to extract content from
            
        Returns:
            List of content entries with extracted text and metadata
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def export_results(self, toc: List[TOCEntry], content: List[ContentEntry]) -> bool:
        """Export processing results"""
        pass
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Template method defining the complete document processing workflow.
        
        This method implements the Template Method pattern, defining the skeleton
        of the processing algorithm while allowing subclasses to override specific steps.
        
        Args:
            input_data: Input data to process (typically file path or document)
            
        Returns:
            Dictionary containing processing results with success status,
            counts, and error information if applicable
            
        Raises:
            ValueError: When input data is invalid
            FileNotFoundError: When input file cannot be found
            Exception: For other processing errors
        """
        try:
            if not self.validate_input(input_data):
                return {"success": False, "error": "Validation failed"}
            
            structure = self.parse_structure(input_data)
            if not structure:
                return {"success": False, "error": "No structure found"}
            
            content = self.extract_content(structure)
            
            if not self.export_results(structure, content):
                return {"success": False, "error": "Export failed"}
            
            return {
                "success": True,
                "toc_count": len(structure),
                "content_count": len(content)
            }
        except ValueError as e:
            logger.error(f"Document validation failed: {e}")
            return {"success": False, "error": "Invalid input data"}
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return {"success": False, "error": "File not accessible"}
        except Exception as e:
            logger.error(f"Document processing failed: {type(e).__name__}: {e}")
            return {"success": False, "error": "Processing failed"}